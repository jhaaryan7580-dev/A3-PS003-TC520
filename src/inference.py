"""Actual forward inference from a verified exported primary checkpoint.

No training or test-driven selection occurs here. A dataset window or a manual
12-value history must use the original benchmark's global index-cycle phase.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import data as D
import models as Mo

ROOT=Path(__file__).resolve().parents[1]
FORMAT='chauraha-sync-verified-checkpoint-v1'


def parameter_hash(params):
    return hashlib.sha256(Mo.get_flat(params).astype('<f4').tobytes()).hexdigest()


def load_checkpoint(path):
    doc=json.loads(Path(path).read_text())
    if doc.get('format')!=FORMAT: raise ValueError('Unsupported checkpoint format')
    arrays=doc.get('parameters',{})
    if set(arrays)!=set(Mo.ORDER): raise ValueError('Checkpoint has missing/extra parameter tensors')
    params={k:np.asarray(arrays[k],dtype=np.float32) for k in Mo.ORDER}
    for key,shape in Mo.SHAPES.items():
        if params[key].shape!=shape or not np.isfinite(params[key]).all():
            raise ValueError(f'Invalid/non-finite parameter tensor {key}')
    if parameter_hash(params)!=doc.get('parameter_sha256'): raise ValueError('Parameter checksum mismatch')
    scaler=doc.get('scaler',{})
    if not np.isfinite(scaler.get('mean',np.nan)) or not np.isfinite(scaler.get('std',np.nan)) or scaler['std']<=0:
        raise ValueError('Invalid training scaler')
    if doc.get('lags')!=D.LAGS or doc.get('cycle_period')!=D.PERIOD or doc.get('horizon')!=1:
        raise ValueError('Unsupported feature/horizon settings')
    if Mo.payload_bytes(params)!=2052: raise ValueError('Unexpected float32 model payload')
    return doc,params


def features_from_history(history,global_index,mean,std):
    history=np.asarray(history,dtype=np.float64)
    if history.shape!=(D.LAGS,): raise ValueError('Exactly 12 lag flows, oldest to newest, are required')
    if not np.isfinite(history).all() or (history<=0).any():
        raise ValueError('History must contain finite positive flows; zero is excluded by this protocol')
    if isinstance(global_index,bool) or not isinstance(global_index,(int,np.integer)) or global_index<D.LAGS:
        raise ValueError('Global target index must be an integer >=12')
    if not np.isfinite(mean) or not np.isfinite(std) or std<=0: raise ValueError('Invalid scaler')
    phase=2*np.pi*(global_index%D.PERIOD)/D.PERIOD
    return np.concatenate(((history-mean)/std,[np.sin(phase),np.cos(phase)])).astype(np.float32)[None,:]


def predict_history(checkpoint,params,history,global_index):
    scaler=checkpoint['scaler']
    X=features_from_history(history,global_index,scaler['mean'],scaler['std'])
    prediction=float(Mo.predict(params,X)[0])*scaler['std']+scaler['mean']
    if not np.isfinite(prediction): raise ValueError('Non-finite forecast')
    return prediction


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,default=ROOT/'checkpoints/fedavg_non_iid_seed0.json')
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--data',type=Path,help='Exact PEMS08 NPZ; provide --sensor-index')
    source.add_argument('--history',help='12 comma-separated positive flows, oldest to newest')
    p.add_argument('--sensor-index',type=int)
    p.add_argument('--global-index',type=int,required=True)
    a=p.parse_args(argv)
    try:
        doc,params=load_checkpoint(a.checkpoint)
        actual=None
        if a.data:
            if D.sha256(a.data)!=doc['dataset_sha256']: raise ValueError('Dataset checksum differs from checkpoint provenance')
            flow=D.load_flow(a.data)
            if a.sensor_index is None or not 0<=a.sensor_index<flow.shape[1]: raise ValueError('Valid --sensor-index is required')
            if not D.LAGS<=a.global_index<len(flow): raise ValueError('Target index outside dataset')
            history=flow[a.global_index-D.LAGS:a.global_index,a.sensor_index]
            actual=float(flow[a.global_index,a.sensor_index])
            if actual<=0: raise ValueError('This target is excluded by the complete-case policy')
        else:
            history=[float(x.strip()) for x in a.history.split(',')]
        pred=predict_history(doc,params,history,a.global_index)
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as e:
        p.error(str(e))
    print(json.dumps({'mode':'actual saved-model forward pass; no retraining',
        'condition':doc['condition'],'seed':doc['seed'],'global_target_index':a.global_index,
        'forecast_flow':pred,'persistence_reference':float(history[-1]),'observed_flow_if_dataset':actual,
        'model_float32_payload_bytes':Mo.payload_bytes(params),
        'note':'Benchmark one-step inference; not a deployed city model or privacy guarantee. Predictions are not clipped.'},indent=2))
    return 0


if __name__=='__main__': raise SystemExit(main())
