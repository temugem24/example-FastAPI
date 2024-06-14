from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.json() == ['Welcome to the home page!!!']
    assert res.status_code == 200 