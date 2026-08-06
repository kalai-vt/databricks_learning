import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.bootstrap import build_pipeline


@pytest.fixture()
def pipeline():
    pipeline, _registry = build_pipeline()
    return pipeline
