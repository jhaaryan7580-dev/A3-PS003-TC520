"""Synthetic fixtures exercise inference plumbing, not reported traffic results."""
from pathlib import Path
import json
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import data as D
import inference as I
import models as Mo


def checkpoint(tmp_path):
    params=Mo.init_params(0)
    doc={'format':I.FORMAT,'condition':'unit_test','seed':0,'lags':12,'cycle_period':288,'horizon':1,
         'scaler':{'mean':20.0,'std':5.0},'parameters':{k:v.tolist() for k,v in params.items()},
         'parameter_sha256':I.parameter_hash(params)}
    path=tmp_path/'checkpoint.json'; path.write_text(json.dumps(doc))
    return path,doc,params


def test_checkpoint_roundtrip(tmp_path):
    path,doc,params=checkpoint(tmp_path)
    loaded,p=I.load_checkpoint(path)
    assert loaded['condition']=='unit_test'
    assert all(np.array_equal(params[k],p[k]) for k in Mo.ORDER)
    assert Mo.payload_bytes(p)==2052


def test_feature_parity_with_frozen_data_layer():
    flow=np.arange(1,601,dtype=float).reshape(300,2)
    t=289; s=1
    expected,_=D.build_xy(flow,np.array([t]),np.array([s]),20.0,5.0)
    got=I.features_from_history(flow[t-12:t,s],t,20.0,5.0)
    assert np.array_equal(expected,got)


def test_real_forward_function(tmp_path):
    path,doc,params=checkpoint(tmp_path)
    h=np.arange(1,13,dtype=float)
    X=I.features_from_history(h,289,20.,5.)
    expected=float(Mo.predict(params,X)[0])*5.+20.
    assert I.predict_history(doc,params,h,289)==expected


@pytest.mark.parametrize('history',[list(range(1,12)),[1.]*11+[0.],[1.]*11+[-1.],[1.]*11+[float('nan')]])
def test_invalid_history(history):
    with pytest.raises(ValueError): I.features_from_history(history,289,20.,5.)


@pytest.mark.parametrize('index',[-1,11,1.5,True])
def test_invalid_global_index(index):
    with pytest.raises(ValueError): I.features_from_history([1.]*12,index,20.,5.)


def test_checksum_catches_parameter_change(tmp_path):
    path,doc,params=checkpoint(tmp_path)
    doc['parameters']['b2'][0]=1.0; path.write_text(json.dumps(doc))
    with pytest.raises(ValueError,match='checksum'): I.load_checkpoint(path)


def test_bad_tensor_shape(tmp_path):
    path,doc,params=checkpoint(tmp_path)
    doc['parameters']['W2']=[1.]; path.write_text(json.dumps(doc))
    with pytest.raises(ValueError,match='tensor'): I.load_checkpoint(path)


def test_bad_scaler(tmp_path):
    path,doc,params=checkpoint(tmp_path)
    doc['scaler']['std']=0.; path.write_text(json.dumps(doc))
    with pytest.raises(ValueError,match='scaler'): I.load_checkpoint(path)
