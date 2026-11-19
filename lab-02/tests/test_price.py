import pytest
import requests

import app as catshop


class FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error")

    def json(self):
        return self.body


@pytest.fixture
def client():
    return catshop.app.test_client()


def test_price_returns_what_the_partner_said(client, monkeypatch):
    calls = []

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return FakeResponse(200, {"sku": "MK-II", "price": "1234.56", "currency": "UAH"})

    monkeypatch.setattr(catshop.requests, "get", fake_get)
    response = client.get("/price/MK-II")

    assert response.status_code == 200
    assert response.get_json()["price"] == "1234.56"
    assert response.get_json()["currency"] == "UAH"
    assert calls == [(f"{catshop.PARTNER_URL}/v1/catalog/MK-II", catshop.PARTNER_TIMEOUT)]


def test_price_answers_502_when_the_partner_fails(client, monkeypatch):
    monkeypatch.setattr(catshop.requests, "get", lambda url, timeout: FakeResponse(500, {}))
    response = client.get("/price/MK-II")

    assert response.status_code == 502
    assert response.get_json()["error"] == "HTTPError"


def test_price_answers_502_when_the_partner_is_too_slow(client, monkeypatch):
    def slow_get(url, timeout):
        raise requests.Timeout("Read timed out")

    monkeypatch.setattr(catshop.requests, "get", slow_get)
    response = client.get("/price/MK-II")

    assert response.status_code == 502
    assert response.get_json()["error"] == "Timeout"
