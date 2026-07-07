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

def test_search_not_found():
    response = client.get("/search?keyword=xyzxyzxyz")
    assert response.status_code == 200
    assert response.json() == []

def test_min_temperature():
    token = get_token()
    response = client.get(
        "/entries?min_temp=20",
        headers = {"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    for entry in data:
        assert entry["temperature"] >= 20

def test_sort_temperature():
    token = get_token()
    response = client.get(
        "/entries?sort=temperature",
        headers = {"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_sort_temperature_descending():
    token = get_token()
    response = client.get(
        "/entries?sort=temperature",
        headers = {"Authorization": f"Bearer {token}"}
    )
    assert response.status_code ==200
    data = response.json()
    temperatures= [entry["temperature"] for entry in data]
    assert temperatures == sorted(temperatures,reverse=True)

def test_pagination():
    token = get_token()
    response = client.get(
        "/entries?limit=2&offset=0",
        headers = {"Authorization": f"Bearer {token}"}, 
    )
    assert response.status_code == 200
    assert len(response.json()) <= 2

def test_update_invalid_entry():
    token = get_token()
    response = client.put(
        "/entry/999999",
        headers = {"Authorization" : f"Bearer {token}"},
        json = {
            "temperature": 30,
            "ethereum_price" : 3000,
            "joke" : "test_update_invalid_entry"
        }  
    )
    assert response.status_code == 404



def test_update_entry():
    token = get_token()
    response = client.post(
        "/entry",
        headers = {"Authorization": f"Bearer {token}"},
        json = {
            "temperature": 20,
            "ethereum_price" : 2000,
            "joke": "Test Update entry"
        }
    )

    entries = client.get(
        "/entries",
        headers ={"Authorization": f"Bearer {token}"}
    )

    entry_id = entries.json()[0]["id"]

    response = client.put(f"/entry/{entry_id}",
        headers = {"Authorization": f"Bearer {token}"},
        json = {"temperature" : 40,
                "ethereum_price": 5000,
                "joke": "test_update_entry"}     
        )

    assert response.status_code == 200

def test_update_entry_without_token():
    response = client.put(
        "/entry/{entry_id}",
        json = {
            "temperature" : 40,
            "ethereum_price": 5000,
            "joke" : "test_update_entry_without_token"
        }
    )
    assert response.status_code == 401

def test_delete_invalid_entry():
    token = get_token()
    response = client.delete(
        "/entry/999999",
        headers = {
            "Authorization" : f"Bearer {token}"
        }
    )
    assert response.status_code == 404


def test_delete_entry():
    token = get_token()
    create = client.post(
        "/entry",
        headers = {
            "Authorization": f"Bearer {token}"},
            json ={
                "temperature" : 28,
                "ethereum_price": 3100,
                "joke": "Delete me"
            }
        
    )
    entries = client.get(
        "/entries",
        headers = {"Authorization": f"Bearer {token}"}
    )
    entry_id = entries.json()[0]["id"]

    response = client.delete(
            f"/entry/{entry_id}",
            headers = {"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_delete_entry_without_token():
    response = client.delete("/entry/{entry_id}")
    assert response.status_code == 401

def test_invalid_entry():
    token = get_token()
    response = client.get(
        "/entry/9999999",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 404

def test_create_without_token():
    response = client.post(
        "/entry",
        json = {
            "temperature": 25,
            "ethereum_price": 3000,
            "joke": "No token"
        }
    )
    assert response.status_code == 401

def test_stats():
    token = get_token()
    response = client.get(
        "/stats",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code ==200
    data = response.json()
    assert "total_entries" in data

def test_stats_without_token():
    response = client.get("/stats")
    assert response.status_code == 401

def test_search():
    token = get_token()
    response = client.get(
        "/search?keyword=pytest",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)

def test_latest_entry():
    token = get_token()
    response = client.get(
        "/latest",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "ethereum_price" in data
    assert "joke" in data

def test_latest_entry_without_token():
    response = client.get("/latest")
    assert response.status_code == 401

def test_get_entries():
    token = get_token()
    response = client.get(
        "/entries",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)

def test_get_entries_withouttoken():
    response = client.get("/entries",)
    assert response.status_code == 401
    
    


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
    #print(response.json())
    assert response.status_code == 201

def test_create_entry_without_token():
    response = client.post("/entry")
    assert response.status_code == 401

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

def test_profile_without_token():
    response = client.get("/profile")
    assert response.status_code == 401

def test_invalid_login():
  response = client.post(
      "/login",
      data ={
          "username": "admin",
          "password": "wrongpassword"
      }
  )
  assert response.status_code == 401
