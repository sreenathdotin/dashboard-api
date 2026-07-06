from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token():
    response = client.post(
        "/login",
        data = {
            "username": "admin",
            "password" : "python123"
        })
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_entry():
    token = get_token()
    response = client.post(
        "/entry",
        headers = {
            "Authorization" : f"Bearer {token}"
        },
        json = {
            "temperature" : 30.5,
            "ethereum_price": 3500,
            "joke": "pytest created this"
        }
    )
    print(response.json())
    assert response.status_code == 201

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