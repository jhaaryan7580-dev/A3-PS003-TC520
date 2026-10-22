"""Deprecated original evidence exporter; intentionally makes no file changes.

The delivered evidence/manifest/checkpoints are frozen and already verified.
The old exporter required the excluded raw benchmark and could overwrite the
current source-manifest schema and obsolete Markdown downloads. It is disabled
rather than silently rewriting the audited browser evidence.

For current standalone HTML document downloads, run from the scientific root:
    python scripts/export_standalone_documents.py --out prototype/client/public/downloads
Then rebuild the prototype and run scripts/verify_submission.py.
This does not train models or change any result values.
"""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    sys.exit(
        "Deprecated exporter: no files changed. Frozen evidence needs no regeneration. "
        "For standalone documents, use "
        f"{root / 'scripts/export_standalone_documents.py'} "
        "--out prototype/client/public/downloads from the scientific root."
    )
