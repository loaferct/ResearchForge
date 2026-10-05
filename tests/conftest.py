import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from support import FakeApis, make_toolkit, small_settings  # noqa: E402

from researchforge.workspace import Workspace  # noqa: E402


@pytest.fixture
def settings(tmp_path):
    return small_settings(tmp_path)


@pytest.fixture
def ws(settings):
    return Workspace.create(settings.resolved_projects_dir(), "Can request-aware dynamic KV-cache eviction reduce LLM inference memory?")


@pytest.fixture
def apis():
    return FakeApis()


@pytest.fixture
def tk(ws, settings, apis):
    return make_toolkit(ws, settings, apis)
