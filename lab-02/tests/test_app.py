import pytest

import app as catshop


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(catshop, "DATABASE_URL", None)
    monkeypatch.setattr(catshop, "COUNTER_FILE", tmp_path / "visits.txt")
    return catshop.app.test_client()


def test_health_answers_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"ok\n"


def test_ready_reports_file_store(client, tmp_path):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.get_json() == {"ready": True, "store": f"file:{tmp_path / 'visits.txt'}"}


def test_ready_answers_503_when_database_is_down(client, monkeypatch):
    monkeypatch.setattr(catshop, "DATABASE_URL", "postgresql://nobody@127.0.0.1:1/none")
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.get_json()["ready"] is False


def test_visits_counts_up(client):
    first = client.get("/visits")
    second = client.get("/visits")
    assert first.get_json() == {"visits": 1, "store": "file"}
    assert second.get_json()["visits"] == 2


def test_visits_continues_from_saved_number(client, tmp_path):
    (tmp_path / "visits.txt").write_text("41")
    assert client.get("/visits").get_json()["visits"] == 42


def test_visits_answers_503_when_counter_file_is_broken(client, tmp_path):
    (tmp_path / "visits.txt").write_text("not a number")
    response = client.get("/visits")
    assert response.status_code == 503
    assert "error" in response.get_json()
