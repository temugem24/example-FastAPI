from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.json() == {"message": "Welcome to the home page"}
    assert res.status_code == 200 

def test_create_user():
    res = client.post("/users/", json = {"email": "testing123@gmail.com", "password": "password123"})
    print (res.json())

    assert res.status_code == 201