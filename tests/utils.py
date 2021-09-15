import os

import pytest

LOCAL_ONLY = pytest.mark.skipif(
    os.environ.get("ENV") != "local", reason="only for local env"
)
