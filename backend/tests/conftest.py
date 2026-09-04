import os
import sys
import tempfile
import pytest

# Ensure backend package imports resolve
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Use an isolated SQLite file per test session
TEST_DB = os.path.join(tempfile.gettempdir(), "detectai_test.db")
os.environ["DETECTAI_TEST_DB"] = TEST_DB

# Patch DB path before importing app modules
import database.db as db_module

db_module.DB_PATH = TEST_DB

from main import app
from database.db import init_db

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
