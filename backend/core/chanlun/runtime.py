"""Runtime setup for local Chanlun calculations."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def setup_local_czsc() -> Path:
    """Prefer the bundled ``backend/czsc`` package for Chanlun endpoints."""

    backend_dir = Path(__file__).resolve().parents[2]
    czsc_dir = backend_dir / "czsc"
    czsc_path = str(czsc_dir)
    if czsc_path not in sys.path:
        sys.path.insert(0, czsc_path)
    os.environ.setdefault("CZSC_USE_PYTHON", "1")
    return backend_dir
