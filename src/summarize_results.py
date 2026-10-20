"""Generate submission tables/figures from saved JSONs; no training or invented data.

    python src/summarize_results.py --out artifacts/reproduced_summary
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
CONDITIONS=['centralised','local_iid','local_non_iid','fedavg_iid','fedavg_non_iid']
LABELS={'centralised':'Centralised','local_iid':'Local IID','local_non_iid':'Local non-IID','fedavg_iid':'FedAvg IID','fedavg_non_iid':'FedAvg non-IID'}
COLORS=['#163C67','#8AA6BC','#597E99','#169A8A','#D97537']
METRICS=['mae','rmse','relative_abs_error']


def stat(values):
    a=np.asarray(values,dtype=float)
    if not np.isfinite(a).all(): raise ValueError('Non-finite metric')
    return {'mean':float(a.mean()),'sample_sd':float(a.std(ddof=1)),'values':a.tolist()}


def isolated_output(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    protected = [root/name for name in ('results','reports','figures','checkpoints','src','configs','tests','docs','data','presentation','prototype')]
    if output == root or output in root.parents or any(output == p or p in output.parents for p in protected):
        raise ValueError('Refusing a frozen project/ancestor output path; use artifacts/reproduced_summary or a separate directory.')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('Output must be a new or empty directory; do not overwrite an earlier reproduction.')
    output.mkdir(parents=True, exist_ok=True)
    return output


def csv_out(path,rows):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def build(root,output):
    root=Path(root)
    main={(c,s):json.loads((root/f'results/full_results/{c}_seed{s}.json').read_text()) for c in CONDITIONS for s in range(3)}
    diag={(c,s):json.loads((root/f'results/diagnostic_100rounds/{c}_seed{s}.json').read_text()) for c in CONDITIONS[-2:] for s in range(3)}
    baseline=json.loads((root/'results/baselines.json').read_text())['test']
    summary={'primary':{},'diagnostic':{},'baselines':{k:{m:v[m] for m in METRICS+['n']} for k,v in baseline.items()},'communication':{'model_bytes':2052,'round_bytes':20520,'primary_run_bytes':615600,'diagnostic_run_bytes':2052000,'training_flow_reference':8499320,'reference_crossing_rounds':8499320/20520,'first_round_above_reference':415},'selection':'Validation-minimum checkpoint, never test-selected. Main 30-round schedule remains primary.'}
    runs=[]; clients=[]; history=[]; target_rows=[]; gaps=[]
    for phase,rr,conditions in [('primary',main,CONDITIONS),('diagnostic',diag,CONDITIONS[-2:])]:
        for c in conditions:
            rs=[rr[(c,s)] for s in range(3)]
            summary[phase][c]={'test':{m:stat([r['test']['overall'][m] for r in rs]) for m in METRICS},'canonical_gap_relative_error':stat([r['test']['per_client_non_iid']['gap_relative_error'] for r in rs]),'canonical_clients':{str(k):{m:stat([r['test']['per_client_non_iid']['clients'][k][m] for r in rs]) for m in METRICS} for k in range(5)}}
            for seed,r in enumerate(rs):
                runs.append({'phase':phase,'condition':c,'seed':seed,**{m:r['test']['overall'][m] for m in METRICS},'test_n':r['test']['overall']['n'],'payload_bytes':r['communication']['total_bytes'],'best_global_step':r['best_checkpoint'].get('round',r['best_checkpoint'].get('epoch','per-client'))})
                for part in ('iid','non_iid'):
                    group=r['test']['per_client_'+part]
                    gaps.append({'phase':phase,'condition':c,'seed':seed,'evaluation_partition':part,'relative_error_gap_pp':100*group['gap_relative_error'],'absolute_mae_gap':group['gap_mae']})
                    for k,v in enumerate(group['clients']): clients.append({'phase':phase,'condition':c,'seed':seed,'evaluation_partition':part,'client':k,**{m:v[m] for m in METRICS},'n':v['n']})
                if c.startswith('fedavg'):
                    target=main[('centralised',seed)]['best_checkpoint']['val_mae']*1.05
                    hits=[h['round'] for h in r['history'] if h['val_mae']<=target]
                    target_rows.append({'phase':phase,'condition':c,'seed':seed,'target_validation_mae':target,'first_hit_round':hits[0] if hits else 'not reached','first_hit_payload_bytes':20520*hits[0] if hits else 'not reached','selected_round':r['best_checkpoint']['round'],'completed_run_bytes':r['communication']['total_bytes']})
                    for h in r['history']: history.append({'phase':phase,'condition':c,'seed':seed,'round':h['round'],'val_mae':h['val_mae'],'target_val_mae':target,'cumulative_bytes':h['cumulative_bytes']})
    tables=Path(output)/'reports/tables'; tables.mkdir(parents=True,exist_ok=True)
    (tables/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    for name,rows in [('all_runs.csv',runs),('all_clients.csv',clients),('client_gaps.csv',gaps),('validation_histories.csv',history),('rounds_to_target.csv',target_rows)]: csv_out(tables/name,rows)
    accuracy=['| Condition | Test MAE mean ± sample SD | Test RMSE mean ± sample SD |','| --- | ---: | ---: |']
    for c in CONDITIONS:
        v=summary['primary'][c]['test']; accuracy.append(f"| {LABELS[c]} | {v['mae']['mean']:.3f} ± {v['mae']['sample_sd']:.3f} | {v['rmse']['mean']:.3f} ± {v['rmse']['sample_sd']:.3f} |")
    (tables/'PRIMARY_ACCURACY.md').write_text('# Primary 30-round / 30-epoch results\n\n'+'\n'.join(accuracy)+'\n\nThree seeds; sample SD uses ddof=1. Full-precision inputs are retained in JSON/CSV.\n')
    return summary,main,diag


def plots(root,summary,main,diag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white'})
    dest=Path(root)/'figures'; dest.mkdir(exist_ok=True)
    fig,axs=plt.subplots(1,2,figsize=(12.5,4.8),layout='constrained')
    for ax,m in zip(axs,('mae','rmse')):
        means=[summary['primary'][c]['test'][m]['mean'] for c in CONDITIONS]; sd=[summary['primary'][c]['test'][m]['sample_sd'] for c in CONDITIONS]; x=np.arange(5)
        ax.errorbar(x,means,yerr=sd,fmt='none',ecolor='#333333',capsize=5)
        ax.scatter(x,means,c=COLORS,s=65,zorder=3)
        for k,c in enumerate(CONDITIONS):
            ax.scatter(np.full(3,k)+np.array([-.10,0,.10]),summary['primary'][c]['test'][m]['values'],s=18,color=COLORS[k],alpha=.5)
            ax.annotate(f'{means[k]:.3f}',(k,means[k]+sd[k]),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
        ax.set_xticks(x,[LABELS[c] for c in CONDITIONS],rotation=23,ha='right'); ax.set_title('Test '+m.upper()); ax.set_ylabel('Flow units'); ax.grid(axis='y',alpha=.18); ax.margins(y=.28)
    fig.suptitle('Primary fixed schedule: three-seed test accuracy',fontsize=15)
    fig.supxlabel('Error bars: sample SD. Individual seeds shown; vertical axes are zoomed, not zero-based.',fontsize=9)
    fig.savefig(dest/'primary_accuracy.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    for c,color in zip(CONDITIONS,COLORS):
        vals=[100*summary['primary'][c]['canonical_clients'][str(k)]['relative_abs_error']['mean'] for k in range(5)]
        ax.plot(range(5),vals,'o-',label=LABELS[c],color=color,lw=1.8)
    ax.set_xticks(range(5),['Q1: quietest','Q2','Q3','Q4','Q5: busiest']); ax.set_ylabel('Relative absolute error (%)'); ax.set_title('Primary predictions evaluated on identical quiet-to-busy groups'); ax.legend(ncol=2,frameon=False); ax.grid(alpha=.18)
    fig.supxlabel('Mean of three seeds; total absolute error / total actual flow. Not MAPE or a fairness guarantee.',fontsize=9)
    fig.savefig(dest/'canonical_client_errors.png',dpi=180); plt.close(fig)
    fig,axs=plt.subplots(1,3,figsize=(14,4.8),layout='constrained',sharey=True)
    for seed,ax in enumerate(axs):
        for c,color in [('fedavg_iid',COLORS[3]),('fedavg_non_iid',COLORS[4])]: ax.plot(range(1,31),[h['val_mae'] for h in main[(c,seed)]['history']],color=color,label=LABELS[c],lw=1.7)
        target=main[('centralised',seed)]['best_checkpoint']['val_mae']*1.05; ax.axhline(target,ls='--',color=COLORS[0],label='1.05 × central best validation')
        ax.set_title(f'Seed {seed}'); ax.set_xlim(1,30); ax.set_yscale('log'); ax.set_xlabel('Round'); ax.grid(alpha=.18)
    axs[0].set_ylabel('Validation MAE (log scale; full range)'); h,l=axs[0].get_legend_handles_labels(); fig.legend(h,l,loc='outside lower center',ncol=3,frameon=False,fontsize=10); fig.suptitle('Primary validation convergence and seed-matched targets',fontsize=14)
    fig.savefig(dest/'primary_convergence.png',dpi=180); plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12.5,4.5),layout='constrained')
    x=np.arange(2)
    for c,color,offset in [('fedavg_iid',COLORS[3],-.1),('fedavg_non_iid',COLORS[4],.1)]:
        means=[summary[phase][c]['test']['mae']['mean'] for phase in ('primary','diagnostic')]; sd=[summary[phase][c]['test']['mae']['sample_sd'] for phase in ('primary','diagnostic')]
        axs[0].errorbar(x+offset,means,yerr=sd,fmt='o-',color=color,capsize=4,label=LABELS[c])
    axs[0].set_xticks(x,['30-round primary','100-round diagnostic']); axs[0].set_ylabel('Test MAE (zoomed axis)'); axs[0].set_ylim(13.75,14.4); axs[0].legend(frameon=False); axs[0].grid(alpha=.18)
    axs[1].bar(x,[615600/1e6,2052000/1e6],color=[COLORS[0],COLORS[4]],width=.55); axs[1].set_xticks(x,['30 rounds','100 rounds']); axs[1].set_ylabel('Completed model payload (decimal MB)'); axs[1].set_ylim(0,2.5)
    for k,v in enumerate([.6156,2.052]): axs[1].text(k,v+.06,f'{v:.4f} MB',ha='center')
    fig.suptitle('Extended-budget diagnostic: modest accuracy gain, 3.33× payload',fontsize=14)
    fig.supxlabel('Validation-selected checkpoints; main and diagnostic schedules remain separately labelled.',fontsize=9)
    fig.savefig(dest/'diagnostic_tradeoff.png',dpi=180); plt.close(fig)


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--out',type=Path); ap.add_argument('--no-plots',action='store_true'); a=ap.parse_args()
    try: output=isolated_output(a.root,a.out or a.root/'artifacts/reproduced_summary')
    except ValueError as error: ap.error(str(error))
    summary,main,diag=build(a.root,output)
    if not a.no_plots: plots(output,summary,main,diag)
    print('Generated exact tables'+(' and four figures' if not a.no_plots else '')+f' in {output}; frozen artifacts unchanged; no training performed.')
