import importlib.util
from pathlib import Path
from unittest.mock import MagicMock
import pytest
import psycopg

spec = importlib.util.spec_from_file_location("campus_app", Path(__file__).parents[1] / "app/app.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

@pytest.fixture
def client():
    module.app.config["TESTING"] = True
    return module.app.test_client()

@pytest.fixture
def unavailable(monkeypatch):
    def fail():
        raise psycopg.OperationalError("unavailable")
    monkeypatch.setattr(module, "connect", fail)


def test_preview_and_readiness_when_database_down(client, unavailable):
    page = client.get("/")
    assert page.status_code == 200
    assert b"Not connected" in page.data
    assert b"disabled" in page.data
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 503
    assert page.headers["Cache-Control"] == "no-store"

@pytest.mark.parametrize("data", [
    {}, {"team":"A", "rating":"abc", "comment":"Hi"},
    {"team":"A", "rating":"6", "comment":"Hi"},
    {"team":"A", "rating":"0", "comment":"Hi"},
    {"team":" " , "rating":"5", "comment":"Hi"},
    {"team":"A"*61, "rating":"5", "comment":"Hi"},
    {"team":"A", "rating":"5", "comment":"X"*501},
])
def test_invalid_feedback_rejected(client, data):
    assert client.post("/feedback", data=data).status_code == 400

def test_valid_feedback_uses_parameters(client, monkeypatch):
    conn = MagicMock()
    conn.__enter__.return_value = conn
    monkeypatch.setattr(module, "connect", lambda: conn)
    result = client.post("/feedback", data={"team":"O'Reilly", "rating":"5", "comment":"Nice"})
    assert result.status_code == 303
    query, values = conn.execute.call_args.args
    assert "%s" in query and "O'Reilly" not in query
    assert values == ("O'Reilly", 5, "Nice")

def test_valid_feedback_reports_storage_failure(client, unavailable):
    assert client.post("/feedback", data={"team":"A", "rating":"5", "comment":"Hi"}).status_code == 503

def test_feedback_is_html_escaped(client, monkeypatch):
    from datetime import datetime, timezone
    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.execute.return_value.fetchall.return_value = [("<script>bad()</script>", 5, "<b>comment</b>", datetime.now(timezone.utc))]
    conn.execute.return_value.fetchone.return_value = (1, 5)
    monkeypatch.setattr(module, "connect", lambda: conn)
    result = client.get("/")
    assert result.status_code == 200
    assert b"<script>bad()" not in result.data
    assert b"&lt;script&gt;" in result.data
    assert b"&lt;b&gt;comment" in result.data

def test_oversized_request_rejected(client):
    assert client.post("/feedback", data={"comment":"x"*20000}).status_code == 413
