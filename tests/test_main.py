from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_login():
    response = client.post(
        "/login",
        data={
            "username" : "admin",
            "password": "python123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_profile():
    login = client.post(
        "/login",
        data = {
            "username": "admin",
            "password": "python123"
        }
    )
    token = login.json()["access_token"]
    response = client.get(
        "/profile",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200

def test_invalid_login():
  response = client.post(
      "/login",
      data ={
          "username": "admin",
          "password": "wrongpassword"
      }
  )
  assert response.status_code == 401

def test_profile_without_token():
    response = client.get("/profile")
    assert response.status_code == 401