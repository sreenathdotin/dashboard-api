from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException

app = FastAPI()
@app.get("/hello")
def hello():
  return {"M1 Message" : "Hello from  fastapi Dashboard API is running"}

def get_connection():
  return sqlite3.connect("dashboard.db")
@app.get("/latest")
def get_latest():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard ORDER BY id DESC LIMIT 1""")
  row = cursor.fetchone()
  conn.close()
  if row is not None:
    return {"Main1 ID": [row[0]] ,"Time": row[1] , "Temperature " :[row[2]] ,"Ethereum Price" : [row[3]] ,"Joke" : [row[4]]}
  else:
    return None

@app.get("/stats")
def get_stats():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT COUNT(*) FROM dashboard""")
  total_entries = cursor.fetchone()[0]

  cursor.execute("""SELECT AVG(temperature) FROM dashboard""")
  avg_temp = cursor.fetchone()[0]

  cursor.execute("""SELECT MAX(ethereum_price) FROM dashboard""")
  high_eth_price = cursor.fetchone()[0]
  conn.close()
  return {"Total Entries": total_entries, "Avg Temperature": round(avg_temp,2),"Highest Ethereum Price": round(high_eth_price,2) }


@app.get("/entries")
def entries():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard ORDER BY id DESC LIMIT 5""")
  rows = cursor.fetchall()
  conn.close()

  return [{"ID": row[0],"Time": row[1], "Temperature": row[2],"Ethereum Price": row[3],"Joke": row[4]} for row in rows]


class DashboardEntry(BaseModel):
  temperature: float
  ethereum_price : float
  joke : str

@app.post("/entry")
def create_entry(entry : DashboardEntry):
  try:
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    if conn is not None:
      cursor = conn.cursor()
      cursor.execute("""INSERT INTO dashboard (timestamp, temperature,ethereum_price,joke)Values(?,?,?,?)""",(current_time,entry.temperature,entry.ethereum_price,entry.joke))
      conn.commit()
      conn.close()
  except Exception as e:
    print(f"Unexpected error {e}")
    return {"Error": str(e)}
  
@app.delete("/entry/{entry_id}")
def delete_entry(entry_id : int):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard WHERE id= ?""",(entry_id,))
  row = cursor.fetchone()
  if row is not None:
    cursor.execute("""DELETE FROM dashboard WHERE id=?""",(entry_id,))
    conn.commit()
    conn.close()
    return {"Message": f"{entry_id} deleted"}
  else:
    return {"Error": f"{entry_id} not found"}
  
@app.put("/entry/{entry_id}")
def update_entry(entry_id : int,entry : DashboardEntry):
  now = datetime.now()
  current_time = now.strftime("%Y-%m-%d %H:%M:%S")

  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT * FROM dashboard WHERE id=?""",(entry_id,))
  row = cursor.fetchone()
  if row is not None:
    cursor.execute("""UPDATE dashboard SET timestamp =?, temperature = ?,ethereum_price= ?,joke =? WHERE id=?""",(current_time,entry.temperature,entry.ethereum_price,entry.joke,entry_id))
    conn.commit()
    conn.close()
    return {"Message": f"{entry_id} has been updated"}
  else:
    conn.close()
    return {"Message": f"{entry_id} not found"}  
  
