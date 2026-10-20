"""Medium-effort reading (gpt-oss-120b medium, K 4) at a fair cap, with the low-effort reading at cap 3,000.
v2 log: T01-T09 complete to 4,813 steps (T10-T13 cut at 2,331, not used); v3 log: T10-T28 cut at 4,304. Fair cap 4,304."""
import sys, re, json, numpy as np, pandas as pd
sys.argv=['x','3001','runs/v2_main_960630.log','runs/v3_main_960796.log']
exec(open('scorecard.py').read().split("methods={'always robust'")[0].replace("print(f'rows {n} |","pass #"))           # D (low-effort pair at 3,001, qfin, strength), helpers
MC=4304; med={}
for path,keep in (('runs/v2_main_960630.log',range(1,10)),('runs/v3_main_960796.log',range(10,29))):
    for m in re.finditer(r'oss_medium_5000 T(\d\d) drop [^|]*\|[^|]*\| (\S.*)',open(path).read()):
        T=int(m.group(1))
        if T in keep: med[T]=[(int(re.match(r'\d+',c).group()),re.search(r'[ncf]',c).group(),re.sub(r'^\d+[ncf]','',c)) for c in m.group(2).split()]
def mfeat(a):
    K=len(a); f=[g for n,k,g in a if k=='n' and n<MC and g!='x']; c={}
    for g in f: c[g]=c.get(g,0)+1
    tok=[min(n,MC) for n,k,g in a]
    return len(f)/K, sum(v*(v-1) for v in c.values())/(K*(K-1)), max(c.values())/K if c else 0.0, float(np.mean(tok))/MC
D['T']=D.text.map(lambda t: texts.index(t)+1)
for j,nm in enumerate(('med_fin','med_pair','med_modal','med_tok')): D[nm]=D['T'].map(lambda T: mfeat(med[T])[j] if T in med else np.nan)
print('templates with a medium read:',len(med),'| attempts per template',sorted({len(v) for v in med.values()}))
tt=D.drop_duplicates('T').set_index('T').sort_index()
dr=pd.DataFrame(calib).assign(T=lambda d:d.text.map(lambda t: texts.index(t)+1)).groupby('T').max_drop.mean()
rng=np.random.default_rng(0)
print('template-level Spearman with the mean drop (two-sided permutation p), 27 labelled templates:')
for c in ('pair','med_fin','med_pair','med_modal','med_tok','qfin'):
    x=tt[c].values.astype(float); yv=dr.reindex(tt.index).values
    r=float(np.corrcoef(pd.Series(x).rank(),pd.Series(yv).rank())[0,1]); null=[np.corrcoef(pd.Series(rng.permutation(x)).rank(),pd.Series(yv).rank())[0,1] for _ in range(5000)]
    print(f'   {c:10s} rho {r:+.3f}  p {np.mean(np.abs(null)>=abs(r)):.4f}')
y=D.y.values; stems=D.stem.values; n=len(D)
print(f'\nSCORECARD with the medium reading (rows {n}; accuracy on the public mix / balanced = 50-50 test; +/- template bootstrap)')
print(f'{"always robust":44s} {acc_at(np.zeros(n,int),y):.3f}            {0.5:.3f}')
ZZ={}
for name,cols in (('low agreement + strength',['pair','strength']),('medium modal share + strength',['med_modal','strength']),('medium finished share + strength',['med_fin','strength']),
                  ('low + medium modal + strength',['pair','med_modal','strength']),('low + quick finish + strength (adopted)',['pair','qfin','strength']),
                  ('low + medium modal + quick finish + strength',['pair','med_modal','qfin','strength'])):
    z=zscores(cols); ZZ[name]=z; yh=(z>0).astype(int); g=D.oss.values
    print(f'{name:44s} {acc_at(yh,y):.3f} +/- {boot(yh):.3f} {acc_at(yh,y,0.5):.3f} +/- {boot(yh,0.5):.3f} | gpt-oss rows {int((yh[g]==y[g]).sum())}/{int(g.sum())} small rows {int((yh[~g]==y[~g]).sum())}/{int((~g).sum())}')
sab=[]
for _ in range(200):
    S=D.copy(); perm=dict(zip(tt.index,rng.permutation(tt.med_modal.values))); S['med_modal']=S['T'].map(perm); z=zscores(['pair','med_modal','qfin','strength'],S); sab.append(acc_at((z>0).astype(int),y,0.5))
print(f'sabotage (medium reading shuffled across templates), balanced: mean {np.mean(sab):.3f}, 95th pct {np.quantile(sab,.95):.3f}')
z=ZZ['low + medium modal + quick finish + strength']; yh=(z>0).astype(int); D['hit']=yh==y; D['cfg']=D.model_id.str.split('/').str[-1].str[:12]+':'+D.effort
print(D.groupby('cfg').agg(rows=('hit','size'),correct=('hit','sum')).T.to_string())
print('wrong rows:', ', '.join(f"T{r['T']:02d} {r.cfg} {r.max_drop:+.2f}" for _,r in D[~D.hit].sort_values('T').iterrows()))
print(tt[['pair','med_fin','med_modal','qfin']].assign(drop=dr).round(2).T.to_string())
