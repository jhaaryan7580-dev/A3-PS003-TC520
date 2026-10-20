"""Presentation helpers must not imply retraining or cross-seed selection."""
from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import demo


def test_replay_is_honest_and_has_actual_windows(capsys):
    assert demo.main(['--condition','fedavg_non_iid','--seed','1','--rounds-to-show','0']) == 0
    out=capsys.readouterr().out
    assert 'precomputed saved results; no live training' in out
    assert 'fedavg_non_iid, seed 1' in out
    assert '2098136' in out and '448533' in out
    assert 'No best-seed selection' in out
    assert 'Global best saved' not in out


def test_smoke_requires_local_dataset(tmp_path,monkeypatch,capsys):
    monkeypatch.setattr(demo,'ROOT',tmp_path)
    assert demo.run_smoke() == 2
    assert '--train-smoke requires dataset' in capsys.readouterr().err


def test_smoke_delegates_to_separate_directory(tmp_path,monkeypatch):
    monkeypatch.setattr(demo,'ROOT',tmp_path)
    (tmp_path/'data').mkdir(); (tmp_path/'configs').mkdir()
    (tmp_path/'data/PEMS08.npz').write_bytes(b'unit-test stub, never loaded')
    (tmp_path/'configs/smoke.json').write_text('{}\n')
    calls=[]
    def fake_run(command, cwd):
        calls.append((command,cwd)); return SimpleNamespace(returncode=0)
    monkeypatch.setattr(demo.subprocess,'run',fake_run)
    assert demo.run_smoke() == 0
    cmd,cwd=calls[0]
    assert cmd[cmd.index('--out')+1] == str(tmp_path/'artifacts/demo_smoke')
    assert cmd[cmd.index('--data')+1] == str(tmp_path/'data/PEMS08.npz')
    assert cwd == tmp_path
