"""Check delivered model artifacts without dataset download or neural training."""
from pathlib import Path
import json
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import inference as I
import models as Mo


@pytest.mark.parametrize('condition',['centralised','fedavg_non_iid'])
def test_exported_model_provenance(condition):
    doc,params=I.load_checkpoint(ROOT/f'checkpoints/{condition}_seed0.json')
    original=json.loads((ROOT/f'results/full_results/{condition}_seed0.json').read_text())
    manifest=json.loads((ROOT/'artifacts/AUDITED_SOURCE_SHA256.json').read_text())
    assert doc['condition']==condition and doc['seed']==0
    assert doc['dataset_sha256']==original['metadata']['dataset_sha256']
    assert doc['config_hash']==original['metadata']['config_hash']
    assert doc['scaler']==original['metadata']['scaler']
    assert doc['selected_checkpoint']==original['best_checkpoint']
    assert doc['verification']['maximum_absolute_float_difference']<1e-5
    export=json.loads((ROOT/'artifacts/VERIFIED_CHECKPOINT_EXPORT.json').read_text())
    assert doc['parameter_sha256']==export['runs'][condition]['parameter_sha256']
    for name,sha in doc['scientific_source_sha256'].items(): assert sha==manifest[name]
    assert Mo.get_flat(params).shape==(513,) and Mo.payload_bytes(params)==2052
    for name in ('mae','rmse','relative_abs_error','n'):
        assert np.isclose(doc['verification']['test_overall'][name],original['test']['overall'][name],rtol=1e-6,atol=1e-5)
