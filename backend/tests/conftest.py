import os
import sys
import tempfile
import pytest

# Ensure repo root and backend directory are in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT_DIR, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Use an isolated SQLite file per test session
TEST_DB = os.path.join(tempfile.gettempdir(), "detectai_test.db")
os.environ["DETECTAI_TEST_DB"] = TEST_DB

# Patch DB path before importing app modules
import backend.database.db as db_module
from backend.main import app
from backend.database.db import init_db

db_module.DB_PATH = TEST_DB

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except OSError:
            pass
    init_db()
    yield
    import gc
    gc.collect()
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except OSError:
            pass

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)
