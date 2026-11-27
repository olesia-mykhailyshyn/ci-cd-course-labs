import os

import requests

BASE = os.environ.get("QA_BASE_URL", "http://localhost:8080")


def test_ready_reports_postgres():
    body = requests.get(f"{BASE}/ready", timeout=5).json()
    assert body == {"ready": True, "store": "postgres"}


def test_visits_are_kept_in_postgres():
    first = requests.get(f"{BASE}/visits", timeout=5).json()
    second = requests.get(f"{BASE}/visits", timeout=5).json()
    assert first["store"] == second["store"] == "postgres"
    assert second["visits"] > first["visits"]


def test_post_to_health_is_405():
    assert requests.post(f"{BASE}/health", timeout=5).status_code == 405


def test_visits_answers_200_as_soon_as_the_stack_is_up():
    response = requests.get(f"{BASE}/visits", timeout=5)
    assert response.status_code == 200, response.text
