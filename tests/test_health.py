from django.test import Client


def test_healthcheck_returns_ok() -> None:
    client = Client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"
