"""Consolidated scorecard after the v4 log: low-effort agreement pooled over two reads at budget 3,000 (K 16),
medium modal share (K 4, 4,304), quick finish, strength. Accuracy on the public mix / balanced (50-50)."""
import sys, re, json, numpy as np, pandas as pd
sys.argv=['x']
exec(open('medium.py').read().split("print('templates with a medium read:'")[0])
y=D.y.values; stems=D.stem.values; n=len(D); U=np.unique(stems); rng=np.random.default_rng(3)
txt=open('runs/v4_main_960863.log').read(); new={}
for m in re.finditer(r'oss_low_ans T(\d\d) drop [^|]*\|[^|]*\| (\S.*)',txt):
    a=[(int(re.match(r'\d+',c).group()),re.search(r'[ncf]',c).group(),re.sub(r'^\d+[ncf]','',c).strip('_')) for c in m.group(1+1).split()]
    K=len(a); c={}
    for nn,k,g in a:
        if k=='n' and nn<3001 and g!='x': c[g]=c.get(g,0)+1
    new[int(m.group(1))]=(sum(v*(v-1) for v in c.values())/(K*(K-1)), max(c.values())/K if c else 0.0)
D['pair_v4']=D['T'].map(lambda T: new[T][0]); D['pair16']=(D.pair+D.pair_v4)/2; D['modal_v4']=D['T'].map(lambda T: new[T][1])
tt=D.drop_duplicates('T').set_index('T'); dr=pd.DataFrame(calib).assign(T=lambda d:d.text.map(lambda t: texts.index(t)+1)).groupby('T').max_drop.mean().reindex(tt.index)
sp=lambda c: float(np.corrcoef(tt[c].rank(),dr.rank())[0,1])
print('template-level Spearman with the mean drop:', {c: round(sp(c),3) for c in ('pair','pair_v4','pair16','med_modal','qfin')}, '| low read-to-read Spearman', round(float(np.corrcoef(tt.pair.rank(),tt.pair_v4.rank())[0,1]),3))
def paired(a,b,pi=None,B=2000):
    d=[]
    for _ in range(B):
        pick=rng.choice(U,len(U)); idx=np.concatenate([np.where(stems==s)[0] for s in pick]); yy=y[idx]
        if len(set(yy))<2: continue
        d.append(acc_at(a[idx],yy,pi)-acc_at(b[idx],yy,pi))
    d=np.array(d); return d.mean(), d.std()
print(f'\n{"rule (leave-one-template-out, 71 rows)":52s} accuracy          balanced        gpt-oss  small')
print(f'{"always robust":52s} 0.732             0.500')
R={}
for name,cols in (('low K 8 (earlier read) + quick finish + strength',['pair','qfin','strength']),('low K 8 (v4 read) + quick finish + strength',['pair_v4','qfin','strength']),
                  ('low K 16 pooled + quick finish + strength',['pair16','qfin','strength']),('low K 16 pooled + strength',['pair16','strength']),
                  ('medium K 4 + quick finish + strength',['med_modal','qfin','strength']),('medium K 4 + low K 16 + quick finish + strength',['med_modal','pair16','qfin','strength']),
                  ('medium K 4 + low K 16 + strength',['med_modal','pair16','strength'])):
    z=zscores(cols); yh=(z>0).astype(int); R[name]=yh; g=D.oss.values
    print(f'{name:52s} {acc_at(yh,y):.3f} +/- {boot(yh):.3f}   {acc_at(yh,y,0.5):.3f} +/- {boot(yh,0.5):.3f}   {int((yh[g]==y[g]).sum())}/37   {int((yh[~g]==y[~g]).sum())}/34')
m,s=paired(R['medium K 4 + quick finish + strength'],R['low K 16 pooled + quick finish + strength']); print(f'\nmedium rule minus pooled-low rule (paired, public mix): {m:+.3f} +/- {s:.3f}')
m,s=paired(R['low K 16 pooled + quick finish + strength'],R['low K 8 (earlier read) + quick finish + strength']); print(f'pooled-low rule minus single-read low rule: {m:+.3f} +/- {s:.3f}')
yh=R['medium K 4 + quick finish + strength']; D['cfg']=D.model_id.str.split('/').str[-1].str[:12]+':'+D.effort
print('misses of the medium rule:', ', '.join(f"T{r['T']:02d} {r.cfg} {r.max_drop:+.2f}" for _,r in D[yh!=y].sort_values('T').iterrows()))
yh=R['low K 16 pooled + quick finish + strength']; print('misses of the pooled-low rule:', ', '.join(f"T{r['T']:02d} {r.cfg} {r.max_drop:+.2f}" for _,r in D[yh!=y].sort_values('T').iterrows()))
