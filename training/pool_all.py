"""Pool every gpt-oss-low read we have (any log, instruments oss_low / oss_low_3000) and judge agreement at a chosen cap,
together with the Qwen quick-finish reading. usage: pool_all.py CAP LOG [LOG ...]
Only attempts that can be scored fairly at CAP are used: finished below CAP (answer counted), or still running / finished
later (counted as unanswered); attempts cut by the clock BEFORE CAP are dropped."""
import sys, re, json, numpy as np, pandas as pd
CAP=int(sys.argv[1]); logs=sys.argv[2:]
calib=json.load(open('sub_v1c/calib.json'))['rows']; texts=list(dict.fromkeys(r['text'] for r in calib))
att={t:[] for t in texts}; med={t:[] for t in texts}
for path in logs:
    txt=open(path).read()
    for inst,store in (('oss_low_3000',att),('oss_low',att),('oss_medium_5000',med),('oss_medium',med)):
        for m in re.finditer(rf'(?<![\w]){inst} T(\d\d) drop [^|]*\|[^|]*\| (\S.*)',txt):
            for c in m.group(2).split():
                n=int(re.match(r'\d+',c).group()); kind=re.search(r'[ncf]',c).group(); g=re.sub(r'^\d+[ncf]','',c)
                lim=CAP if store is att else 10**9
                if kind=='c' and g=='x' and n<lim: continue          # cut by the clock before the cap: unknown, drop
                store[texts[int(m.group(1))-1]].append((n,kind,g,path))
def agree(a,cap):
    by={}
    for n,k,g,p in a: by.setdefault(p,[]).append((n,k,g))
    vals=[]
    for p,rows in by.items():                                        # agreement within each run, then averaged
        K=len(rows); c={}
        for n,k,g in rows:
            if n<cap and k!='f' and g!='x': c[g]=c.get(g,0)+1
        if K>1: vals.append(sum(v*(v-1) for v in c.values())/(K*(K-1)))
    return float(np.mean(vals)) if vals else np.nan
qlog=open('runs/r1_small_957664.log').read()
qfin={texts[int(m.group(1))-1]:float(float(m.group(2))>0) for m in re.finditer(r'qwen_nothink T(\d\d) .*?natural ([\d.]+)',qlog)}
STR={('Skywork/Skywork-OR1-Math-7B','default'):0,('allenai/Olmo-3-7B-Think','default'):1,('deepseek-ai/DeepSeek-R1-0528-Qwen3-8B','default'):1,('Qwen/Qwen3.5-4B','default'):1,('openai/gpt-oss-120b','low'):1,('openai/gpt-oss-120b','medium'):2,('openai/gpt-oss-120b','high'):3}
L=pd.DataFrame(calib); L=L[L.label.notna()].copy(); L['y']=L.label.astype(int)
L['strength']=[STR[(m,e)] for m,e in zip(L.model_id,L.effort)]; L['oss']=L.model_id.str.contains('gpt-oss')
L['pair']=L.text.map(lambda t: agree(att[t],CAP)); L['qfin']=L.text.map(qfin); L['pmed']=L.text.map(lambda t: agree(med[t],10**9))
def bal(y,yh): return 0.5*((yh[y==1]==1).mean()+(yh[y==0]==0).mean())
def fit(X,yy):
    mu,sd=X.mean(0),X.std(0)+1e-9; Z=np.column_stack([np.ones(len(X)),(X-mu)/sd])
    sw=np.where(yy==1,0.5/max(yy.mean(),1e-9),0.5/max(1-yy.mean(),1e-9)); b=np.zeros(Z.shape[1]); R=np.eye(Z.shape[1])/len(X); R[0,0]=0
    for _ in range(100):
        p=1/(1+np.exp(-Z@b)); g=Z.T@(sw*(p-yy))/len(X)+R@b; H=(Z*(sw*p*(1-p))[:,None]).T@Z/len(X)+R+1e-8*np.eye(Z.shape[1]); b-=np.linalg.solve(H,g)
    return b,mu,sd
def loto(D,cols):
    yy=D.y.values; pred=np.zeros(len(D)); X=D[cols].values.astype(float)
    for s in D.stem.unique():
        tr=(D.stem!=s).values
        if len(set(yy[tr]))<2: continue
        b,mu,sd=fit(X[tr],yy[tr]); pred[~tr]=b[0]+((X[~tr]-mu)/sd)@b[1:]
    yh=(pred>0).astype(int); return bal(yy,yh),(yh==yy).mean(),yh
nread=pd.Series({t:len(att[t]) for t in texts}); print(f'cap {CAP}: attempts per template min {nread.min()} median {int(nread.median())} max {nread.max()}; templates with a medium read: {sum(len(v)>0 for v in med.values())}')
D=L[L.pair.notna()]
for cols in (['pair','strength'],['pair','qfin','strength']):
    b,a,yh=loto(D,cols); g=D.oss.values; y=D.y.values
    print(f'{"+".join(cols):22s} rows {len(D)} balanced {b:.3f} acc {a:.3f} | gpt-oss rows bal {bal(y[g],yh[g]):.3f} acc {(yh[g]==y[g]).mean():.2f} | small rows acc {(yh[~g]==y[~g]).mean():.2f}')
M=L[L.pmed.notna() & L.pair.notna()]
if M.stem.nunique()>=20:
    for cols in (['pmed','strength'],['pair','pmed','qfin','strength']):
        b,a,yh=loto(M,cols); g=M.oss.values; y=M.y.values
        print(f'{"+".join(cols):22s} rows {len(M)} balanced {b:.3f} acc {a:.3f} | gpt-oss rows bal {bal(y[g],yh[g]):.3f} acc {(yh[g]==y[g]).mean():.2f}')
X=D[['pair','qfin','strength']].values.astype(float); b,mu,sd=fit(X,D.y.values.astype(float))
print('refit full model at this cap:',json.dumps({'beta':b.round(5).tolist(),'mu':mu.round(5).tolist(),'sd':sd.round(5).tolist()}))
