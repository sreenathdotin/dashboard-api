from fastapi import FastAPI,HTTPException,status,Response,Depends,Header
from pydantic import BaseModel
from datetime import datetime,timedelta
import sqlite3
from fastapi import HTTPException
from typing import List
from database import get_connection
from models import DashboardResponse,DashboardEntry,DashboardStats
from auth import verify_api_key
from models import LoginRequest,Token
from auth import create_access_token
from auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from database import init_db
from auth import hash_password
from database import get_user
from auth import verify_password



app = FastAPI()
init_db()

@app.get("/")
def home():
    return {
        "message": "Dashboard API is running!",
        "docs": "/docs"
    }

print("Testing branch")
print("Testing GitHub")

@app.get("/profile")
def profile(user: str= Depends(get_current_user)):
  return{
    "username" : user
  }

@app.post("/login",response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):

  user = get_user(form_data.username)
  if user is None:
    raise HTTPException(
      status_code = 401,
      detail = "Invalid username or password"
    )
  if not verify_password(
    form_data.password,
    user[1]
    ):
    raise HTTPException(
      status_code = 401,
      detail = "Invalid username or password"
    )
  token = create_access_token(
    {"sub": user[0]}
  )
  return {
    "access_token": token,
    "token_type":"bearer"
  }

@app.delete("/entry/{id}")
def delete_entry(id : int):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM dashboard WHERE id = ?",(id,))
  if cursor.rowcount == 0:
    conn.close()
    raise HTTPException(
      status_code = 404,
      detail = f"Entry {id} not found "
    )
  conn.commit()
  conn.close()
  return {"message" : "Entry deleted successfully"}

@app.put("/entry/{id}")
def update_entry(id: int, entry: DashboardEntry):
  conn= get_connection()
  cursor = conn.cursor()
  cursor.execute("""UPDATE dashboard SET temperature = ?, ethereum_price = ? ,joke = ? WHERE id = ?""",
  (entry.temperature,entry.ethereum_price,entry.joke,id))
  if cursor.rowcount == 0:
    conn.close()
    raise HTTPException(
      status_code= 404,
      detail=f"Entry{id}not found"
    )
  conn.commit()
  conn.close()
  return {"message": "Entry updated Successfully"}

@app.post("/entry",status_code=201)
def create_entry(entry: DashboardEntry):
  conn = get_connection()
  cursor = conn.cursor()
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute("""INSERT INTO dashboard (timestamp,temperature,ethereum_price,joke) VALUES(?,?,?,?)""",
  (timestamp,entry.temperature,entry.ethereum_price,entry.joke))
  conn.commit()
  conn.close()
  return {"message": "Entry created successfully"}

@app.get("/search", response_model = List[DashboardResponse])
def search(keyword: str):
  query = ("""SELECT * FROM dashboard WHERE joke LIKE ? ORDER BY id DESC""")
  params = (f"%{keyword}%",)
  return execute_query(query,params)


@app.get("/hello")
def hello(_ : str = Depends(verify_api_key)):
  return {"message":"Hello from fastapi  - Dashboard API is running"}

@app.get("/latest", response_model = DashboardResponse)
def latest():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard ORDER BY id DESC LIMIT 1""")
  row = cursor.fetchone()
  conn.close()

  return {
    "id" : row[0],
    "timestamp" : row[1],
    "temperature": row[2],
    "ethereum_price" : row[3],
    "joke":row[4]
  }

@app.get("/stats",response_model = DashboardStats)
def stats():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""
    SELECT COUNT(*),
      Min(temperature),
      Max(temperature),
      AVG(temperature)
      FROM dashboard
  """)

  stats = cursor.fetchone()
  conn.close()

  return{ 
    "total_entries" : stats[0],
    "min_temperature" : stats[1],
    "max_temperature" : stats[2],
    "avg_temperature" : round(stats[3],2)
  }

@app.get("/entry/{entry_id}",response_model = DashboardResponse,dependencies=[Depends(verify_api_key)])
def get_single_entry(entry_id : int, _ : str = Depends(verify_api_key)):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard  WHERE id = ?""",(entry_id,))
  row = cursor.fetchone()
  if row is not None:
    conn.close()
    return {"ID": row[0], "Timestamp": row[1], "Temperature": row[2],"Ethereum_price": row[3],"Joke": row[4]}
  else:
    conn.close()
    raise HTTPException(
      status_code = 404,
      detail= f"Entry {entry_id} not found"
    )

def row_to_dict(row):
  return {"id": row[0],"timestamp": row[1], "temperature": row[2],"ethereum_price":row[3],"joke":row[4]}

def execute_query(query,params):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute(query,params)
  rows = cursor.fetchall()
  conn.close()
  return [row_to_dict(row)for row in rows]


@app.get("/entries",response_model = List[DashboardResponse])
def entries(
    limit : int = 5,
    offset : int = 0,
    min_temp: float | None = None, 
    max_temp : float | None = None, 
    sort: str ="id",
    _ : str = Depends(verify_api_key)
    ):
  allowed_sorts = [
    "id",
    "temperature",
    "ethereum_price",
    "timestamp"
  ]
  
  if sort not in allowed_sorts:
    sort = "id"

  if min_temp is not None and max_temp is not None:
    query = (f"""SELECT * FROM dashboard  WHERE temperature >= ? AND temperature <= ? ORDER BY {sort} DESC LIMIT ? OFFSET ?""")
    params = (min_temp,max_temp,limit,offset)
    
  
  elif min_temp is not None and max_temp is None:
    query = (f"""SELECT * FROM dashboard  WHERE temperature >= ? ORDER BY {sort} DESC LIMIT ? OFFSET ?""")
    params = (min_temp,limit,offset)
    

  elif max_temp is not None and min_temp is None:
    query=(f"""SELECT * FROM dashboard  WHERE temperature <= ? ORDER BY {sort} DESC LIMIT ? OFFSET ?""")
    params = (max_temp,limit,offset)
    

  else:
    query = (f"""SELECT * FROM dashboard   ORDER BY {sort} DESC LIMIT ? OFFSET ?""")
    params = (limit,offset)
  
  return execute_query(query,params)
    


@app.post("/entry",status_code=status.HTTP_201_CREATED)
def create_entry(entry: DashboardEntry):
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  try:
    conn = get_connection()
    if conn is None:
        raise HTTPException(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database connection failed"
        )
    cursor= conn.cursor()
    cursor.execute("""INSERT INTO dashboard (timestamp,temperature,ethereum_price,joke) 
      VALUES(?,?,?,?) """, (current_time,entry.temperature,entry.ethereum_price,entry.joke))
    conn.commit()
    conn.close()
    return {"message": "Entry added Successfully"}
  except HTTPException:
    raise
  except Exception as e:
    print(f"Unexpected error: {e}")
    raise HTTPException(
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
      details = f"Database error: {str(e)}"
      )
  
@app.delete("/entry/{entry_id}")
def delete_entry(entry_id :int ):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dashboard WHERE id=?",(entry_id,))
    row = cursor.fetchone()
    if row is not None:
      cursor.execute("DELETE FROM dashboard WHERE id =?",(entry_id,))
      conn.commit()
      conn.close()
      return {"message": f"Entry {entry_id} deleted"}
    else:
      conn.close()
      raise HTTPException(status_code=404, detail = f"Entry {entry_id}  not found",)
      #return {"message": f"{entry_id} not found"}

   
@app.put("/entry/{entry_id}")
def update_entry(entry_id : int,entry : DashboardEntry):
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  conn=get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM dashboard WHERE id = ?",(entry_id,))
  row = cursor.fetchone()
  if row is not None:
    cursor.execute("UPDATE dashboard SET timestamp = ?,temperature =?, ethereum_price =? , joke =? WHERE id = ? ",(current_time,entry.temperature,entry.ethereum_price,entry.joke, entry_id))
    conn.commit()
    conn.close()
    return{"message": f"{entry_id} has been updated"}
  else:
    conn.close()
    return {"message": f"{entry_id} not found"}


# Response API


