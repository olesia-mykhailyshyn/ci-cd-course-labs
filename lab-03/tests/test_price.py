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
        if isinstance(self.body, Exception):
            raise self.body
        return self.body


@pytest.fixture
def client():
    return catshop.app.test_client()


@pytest.fixture
def partner(monkeypatch):
    calls = []

    def answer_with(response):
        def fake_get(url, **kwargs):
            calls.append({"url": url, **kwargs})
            if isinstance(response, Exception):
                raise response
            return response

        monkeypatch.setattr(catshop.requests, "get", fake_get)
        return calls

    return answer_with


def test_price_returns_what_the_partner_said(client, partner):
    partner(FakeResponse(200, {"sku": "MK-II", "price": "1234.56", "currency": "UAH"}))
    response = client.get("/price/MK-II")

    assert response.status_code == 200
    assert response.get_json() == {
        "sku": "MK-II",
        "price": "1234.56",
        "currency": "UAH",
        "source": f"{catshop.PARTNER_URL}/v1/catalog/MK-II",
    }


def test_price_asks_the_partner_for_that_sku_and_never_waits_forever(client, partner):
    calls = partner(FakeResponse(200, {"price": "1", "currency": "UAH"}))
    client.get("/price/BOOM-7")

    assert len(calls) == 1
    assert calls[0]["url"] == f"{catshop.PARTNER_URL}/v1/catalog/BOOM-7"
    assert calls[0]["timeout"] == catshop.PARTNER_TIMEOUT


def test_price_answers_502_when_the_partner_fails(client, partner):
    partner(FakeResponse(500, {}))
    response = client.get("/price/MK-II")

    assert response.status_code == 502
    assert response.get_json()["error"] == "HTTPError"


def test_price_answers_502_when_the_partner_is_too_slow(client, partner):
    partner(requests.Timeout("Read timed out"))
    response = client.get("/price/MK-II")

    assert response.status_code == 502
    assert response.get_json()["error"] == "Timeout"


def test_price_answers_502_when_the_partner_sends_garbage(client, partner):
    partner(FakeResponse(200, ValueError("not JSON")))
    response = client.get("/price/MK-II")

    assert response.status_code == 502
    assert response.get_json()["sku"] == "MK-II"
