from fastapi import FastAPI,HTTPException,status,Depends
from datetime import datetime
from typing import List
from database import get_connection
from models import DashboardResponse,DashboardEntry,DashboardStats
from models import Token
from auth import create_access_token
from auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from database import init_db
from database import get_user
from auth import verify_password
from logger import logger
from fastapi import Request
import time



app = FastAPI()
init_db()

@app.middleware("http")
async def log_requests(request: Request,call_next):
  start_time = time.time()
  response = await call_next(request)
  process_time = time.time() - start_time
  logger.info(
    f"{request.method} "
    f"{request.url.path} "
    f"Status={response.status_code} "
    f"Time={process_time:.4f}s"
  )
  return response

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
    logger.warning(f"Invalid login attempt for username {form_data.username}")
    raise HTTPException(
      status_code = 401,
      detail = "Invalid username or password"
    )
  if not verify_password(
    form_data.password,
    user[1]
    ):
    logger.warning(f"Invalid login attempt for username {form_data.username}")
    raise HTTPException(
      status_code = 401,
      detail = "Invalid username or password"
    )
  token = create_access_token(
    {"sub": user[0]}
  )
  logger.info(f"User {user[0]} logged in")
  return {
    "access_token": token,
    "token_type":"bearer"
  }

@app.delete("/entry/{id}")
def delete_entry(id : int,current_user: str = Depends(get_current_user)):
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
  logger.info(f"Entry {id} deleted by {current_user}")
  conn.close()
  return {"message" : "Entry deleted successfully"}

@app.put("/entry/{id}")
def update_entry(id: int, entry: DashboardEntry,current_user: str = Depends(get_current_user)):
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
  logger.info(f"Entry {id} updated by {current_user}")
  conn.close()
  return {"message": "Entry updated Successfully"}

@app.get("/search", response_model = List[DashboardResponse])
def search(keyword: str):
  query = ("""SELECT * FROM dashboard WHERE joke LIKE ? ORDER BY id DESC""")
  params = (f"%{keyword}%",)
  return execute_query(query,params)


@app.get("/latest", response_model = DashboardResponse)
def latest(current_user: str = Depends(get_current_user)):
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
def stats(current_user: str = Depends(get_current_user)):
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

@app.get("/entry/{entry_id}",response_model = DashboardResponse)
def get_single_entry(
  entry_id : int,
  current_user: str = Depends(get_current_user)
  ):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard  WHERE id = ?""",(entry_id,))
  row = cursor.fetchone()
  if row is not None:
    conn.close()
    return {"id": row[0], "timestamp": row[1], "temperature": row[2],"ethereum_price": row[3],"joke": row[4]}
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


@app.get("/entries")
def get_entries(
    current_user: str = Depends(get_current_user),
    limit : int = 5,
    offset : int = 0,
    min_temp: float | None = None, 
    max_temp : float | None = None, 
    sort: str ="id"
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
def create_entry(entry: DashboardEntry,
  current_user: str = Depends(get_current_user)):
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
    logger.info(f"New dashboard entry created by {current_user}")
    conn.close()
    return {"message": "Entry added Successfully"}
  except HTTPException:
    raise
  except Exception as e:
    logger.exception("Unexpected error")
    print(f"Unexpected error: {e}")
    raise HTTPException(
      status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail = f"Database error: {str(e)}"
      )
  


