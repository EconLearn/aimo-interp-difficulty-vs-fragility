"""Scorecard on the scored metric (advice file, items 1-2 and 5). usage: scorecard.py CAP LOG [LOG ...]
For every method: plain accuracy on the public mix (73% robust) AND balanced accuracy (= expected plain accuracy on a
50/50 test such as the hidden validation sets), each with the trivial baselines and a template-cluster bootstrap error.
Then: what the decision threshold gives away under each prior, a ceiling table, and a scan by class."""
import sys, re, json, numpy as np, pandas as pd
exec(open('pool_all.py').read().split("nread=pd.Series")[0])
D=L[L.pair.notna()].copy().reset_index(drop=True); y=D.y.values; n=len(D); stems=D.stem.values
print(f'rows {n} | templates {D.stem.nunique()} | robust {int((y==0).sum())} non-robust {int((y==1).sum())}')
def zscores(cols,DD=D):
    X=DD[cols].values.astype(float); yy=DD.y.values; z=np.full(len(DD),np.nan)
    for s in DD.stem.unique():
        tr=(DD.stem!=s).values
        if len(set(yy[tr]))<2: continue
        b,mu,sd=fit(X[tr],yy[tr]); z[~tr]=b[0]+((X[~tr]-mu)/sd)@b[1:]
    return z
def acc_at(yh,yy,pi=None):
    tpr=(yh[yy==1]==1).mean(); tnr=(yh[yy==0]==0).mean()
    return (yh==yy).mean() if pi is None else pi*tpr+(1-pi)*tnr
rng=np.random.default_rng(0); U=np.unique(stems)
def boot(yh,pi=None,B=1000):
    out=[]
    for _ in range(B):
        pick=rng.choice(U,len(U)); idx=np.concatenate([np.where(stems==s)[0] for s in pick])
        yy=y[idx]; 
        if len(set(yy))<2: continue
        out.append(acc_at(yh[idx],yy,pi))
    return float(np.std(out))
methods={'always robust':np.zeros(n,int),'always non-robust':np.ones(n,int)}
Z={}
for name,cols in (('strength only (config prior)',['strength']),('quick finish + strength',['qfin','strength']),('agreement + strength',['pair','strength']),('agreement + quick finish + strength',['pair','qfin','strength'])):
    Z[name]=zscores(cols); methods[name]=(Z[name]>0).astype(int)
# template oracle (not deployable): each row predicted from the mean drop of the OTHER rows of its template (band rows included)
A=pd.DataFrame(calib); om=[]
for _,r in D.iterrows():
    o=A[(A.stem==r.stem)&~((A.model_id==r.model_id)&(A.effort==r.effort))].max_drop
    om.append(o.mean() if len(o) else np.nan)
om=np.array(om); has=~np.isnan(om)
print('\nSCORECARD (leave-one-template-out). accuracy = public mix; balanced = expected accuracy on a 50/50 test. +/- = template bootstrap')
print(f'{"method":38s} {"accuracy":>14s} {"balanced":>14s}')
for name,yh in methods.items():
    print(f'{name:38s} {acc_at(yh,y):.3f} +/- {boot(yh):.3f} {acc_at(yh,y,0.5):.3f} +/- {boot(yh,0.5):.3f}')
yo=(om[has]>0.175).astype(int)
print(f'{"template oracle (other rows, n="+str(int(has.sum()))+")":38s} {acc_at(yo,y[has]):.3f}            {acc_at(yo,y[has],0.5):.3f}        (ledger 9; rows whose template has another row)')
print(f'{"label-noise ceiling (simulation)":38s} 0.97-0.99                             (miners3/bench/02_noise_ceiling.out)')
print('\nTHRESHOLD: accuracy of the adopted rule if the cut on its score is moved (score > cut = non-robust)')
z=Z['agreement + quick finish + strength']
print(f'{"cut":>6s} {"public mix (27% nr)":>20s} {"35% nr":>8s} {"50% nr":>8s} {"predicted nr share":>19s}')
best={}
for cut in (-1.5,-1.0,-0.5,-0.25,0.0,0.25,0.5,1.0,1.5,2.0):
    yh=(z>cut).astype(int); row=[acc_at(yh,y,pi) for pi in (0.268,0.35,0.5)]
    for pi,a in zip((0.268,0.35,0.5),row):
        if a>best.get(pi,(0,0))[0]: best[pi]=(a,cut)
    print(f'{cut:6.2f} {row[0]:20.3f} {row[1]:8.3f} {row[2]:8.3f} {yh.mean():19.2f}')
print('best cut by prior (in-sample choice of one number, so optimistic by ~0.01-0.02):', {f'{int(100*pi)}% nr': f'cut {c:+.2f} acc {a:.3f}' for pi,(a,c) in best.items()})
print('\nCLASS SCAN of the adopted rule (cut 0)')
yh=(z>0).astype(int); D['hit']=(yh==y); D['cfg']=D.model_id.str.split('/').str[-1].str[:12]+':'+D.effort
print(D.groupby('cfg').agg(rows=('hit','size'),non_robust=('y','sum'),correct=('hit','sum'),accuracy=('hit','mean')).round(2).to_string())
D['T']=D.text.map(lambda t: texts.index(t)+1)
print('wrong rows:', ', '.join(f"T{r['T']:02d} {r.cfg} drop {r.max_drop:+.2f}" for _,r in D[~D.hit].sort_values('T').iterrows()))
