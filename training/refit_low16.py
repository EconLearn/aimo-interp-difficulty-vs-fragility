"""Decision models for the low-effort entry from the POOLED low reads (ledger 113): agreement = mean of the per-read pairwise
agreement of two gpt-oss-low K 8 reads at budget 3,000 (v2+v3 read, v4 oss_low_ans read) = consolidated.py's pair16 (0.845 / 0.844).
Skywork coded like the other small models (ledger 103), as the entry's _STRENGTH does. usage: refit_low16.py OUT.json"""
import sys, json, numpy as np
out=sys.argv[1]
exec(open('consolidated.py').read().split("print(f'\\n{\"rule")[0])
print('Skywork strength codes before:', sorted(set(D.loc[D.model_id.str.contains('Skywork'),'strength'])))
D.loc[D.model_id.str.contains('Skywork'),'strength']=1
res={"primary_feature":"pair_nat","primary_cap":3000,"fitted_on":"71 public rows; agreement = mean of two gpt-oss-low K 8 reads at 3,000 (v2+v3, v4); qfin = Qwen3.5-4B thinking off, K 4, 2,000; Skywork strength 1"}
for name,cols in (('full',['pair16','qfin','strength']),('agreement_only',['pair16','strength']),('finish_only',['qfin','strength'])):
    z=zscores(cols); yh=(z>0).astype(int); X=D[cols].values.astype(float); b,mu,sd=fit(X,y.astype(float)); g=D.oss.values
    res[name]={"features":[{'pair16':'pair_nat'}.get(c,c) for c in cols],"beta":b.round(5).tolist(),"mu":mu.round(5).tolist(),"sd":sd.round(5).tolist(),
               "note":f"leave-one-template-out accuracy {acc_at(yh,y):.3f} +/- {boot(yh):.3f} (public mix) / {acc_at(yh,y,0.5):.3f} +/- {boot(yh,0.5):.3f} (50-50); gpt-oss {int((yh[g]==y[g]).sum())}/37 small {int((yh[~g]==y[~g]).sum())}/34"}
    print(f'{name:15s}', res[name]['note'])
b,mu,sd=[np.array(res['full'][k]) for k in ('beta','mu','sd')]
print('rule: non-robust iff agreement below', {f'qfin {q}, strength {s}': round(float(mu[0]+sd[0]*(-(b[0]+b[2]*(q-mu[1])/sd[1]+b[3]*(s-mu[2])/sd[2])/b[1])),2) for q in (0,1) for s in (1,2,3)})
json.dump(res,open(out,'w'),indent=1); print('wrote',out)
