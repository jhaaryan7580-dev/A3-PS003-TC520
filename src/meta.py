"""Reproducibility metadata stored inside every result JSON."""
import hashlib
import json
import subprocess
from pathlib import Path


def code_commit():
    try:
        root = Path(__file__).resolve().parent.parent
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip() + ("+uncommitted-changes" if dirty.stdout.strip() else "")
    except Exception:
        pass
    return "unavailable (not a git repository)"


def config_hash(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
