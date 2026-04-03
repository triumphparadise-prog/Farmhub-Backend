from rest_framework.test import APIRequestFactory

from core.views import HealthCheckAPIView


class DummyCursor:
    def execute(self, query):
        self.query = query

    def fetchone(self):
        return (1,)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyConnection:
    def cursor(self):
        return DummyCursor()


def test_healthcheck_returns_ok(monkeypatch):
    monkeypatch.setattr("core.views.connections", {"default": DummyConnection()})
    factory = APIRequestFactory()
    request = factory.get("/healthz/")
    response = HealthCheckAPIView.as_view()(request)

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"]["database"] == "ok"
