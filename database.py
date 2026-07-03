import sqlite3


def get_connection():
  return sqlite3.connect("dashboard.db")

def get_user(username):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""
    SELECT username,password FROM users WHERE username = ?""",(username,))
  user= cursor.fetchone()
  conn.close()
  return user

def init_db():
  conn =sqlite3.connect("dashboard.db")
  cursor= conn.cursor()
  cursor.execute("""CREATE TABLE IF NOT EXISTS dashboard(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,temperature REAL,
  ethereum_price REAL,
  joke TEXT
  )""")
  cursor.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE, password TEXT)""")
  conn.commit()
  conn.close()

