import requests
from datetime import datetime
import csv
import os
import sqlite3
import json

def get_temperature():
  url = "https://api.open-meteo.com/v1/forecast"

  params = {
    "latitude" : 12.97,
    "longitude" : 77.59,
    "current" : "temperature_2m"
  }

  try:
    response = requests.get(url,params = params,timeout = 5)
    response.raise_for_status()
    data = response.json()
    return data["current"]["temperature_2m"]
  except requests.exceptions.ConnectionError:
    print("Connection Error")
  except requests.exceptions.HTTPError:
    print(f"HTTP error: {response.status_code}")
  except Exception as e:
    print(f"Unexpected error: {e}")
  return None
  


def get_eth_price():
  url = "https://api.coingecko.com/api/v3/simple/price"

  params = {
    "ids" : "ethereum",
    "vs_currencies" : "usd"
  }
  try:
    response = requests.get(url, params= params,timeout = 5)
    response.raise_for_status()
    data = response.json()
    return data["ethereum"]["usd"]
  except requests.exceptions.Timeout:
    print("Request timed out")
  except requests.exceptions.ConnectionError:
    print("Connection error")
  except requests.exceptions.HTTPError:
    print(f"HTTP Error: {response.status_code}")

  except Exception as e:
    print(f"Unexpected error: {e}")
  return None
  

def get_joke():
  try:
    response = requests.get(
    "https://official-joke-api.appspot.com/random_joke",
    timeout =5
    )
    response.raise_for_status()
    data = response.json()
    print(f"\n Raw JSON  data:\n {json.dumps(data,indent=4)}")
    if "errors" in data:
      print("API returned an error")
    return f"{data['setup']} - {data['punchline']}"
  except requests.exceptions.Timeout:
    print("Request timed out")
  except requests.exceptions.ConnectionError:
    print("Connection Error")
  except requests.exceptions.HTTPError:
    print(f"HTTP Error : {response.status_code}")
  except Exception as e:
    print(f"Unexpected error: {e}")
  return None

  
def save_to_file(current_time,temperature,eth_price,joke):
  with open("dashboard_log.txt", "a") as file:
    file.write(
      f"{current_time} | {temperature} | {eth_price} | {joke}\n"
    )

def save_to_csv(current_time, temperature,eth_price, joke):
  file_exists = os.path.isfile("dashboard_data.csv")
  with open("dashboard_data.csv","a",newline="") as file:
    writer = csv.writer(file)
    if not file_exists:
      writer.writerow(["timestamp","temperature","eth_price","joke"])
    writer.writerow ([current_time,temperature,eth_price,joke]) 



def get_connection():
  return sqlite3.connect("dashboard.db")    

def save_to_sqlite(current_time,temperature,eth_price,joke):
  try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dashboard(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT,
      temperature REAL,
      ethereum_price REAL,
      joke TEXT              
    )
    """)
    cursor.execute(
      """INSERT INTO dashboard (timestamp,temperature,ethereum_price,joke) VALUES (?,?,?,?)""",
      (current_time,temperature,eth_price,joke)
    )

    conn.commit()
    
  except sqlite3.Error as e:
    print(f"Database error : {e}")
  finally:
    conn.close()

def show_last_entries():
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  SELECT * FROM dashboard ORDER BY id DESC LIMIT 5 """)
  rows = cursor.fetchall()
  for row in rows:
    print(
      f"ID : {row[0]} |"
      f"Time: {row[1]} |"
      f"Temp: {row[2]} °C | "
      f"ETH : $ {row[3]}"
    )
  conn.close()

def show_total_entries():
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  SELECT COUNT(*) FROM dashboard
  """)
  total = cursor.fetchone()[0]
  if total is not None:
    print(f"\nTotal dashboard entries: {total}")
  else:
    print("No entries found")
  conn.close()

def show_average_temperature():
  conn= get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT AVG(temperature) FROM dashboard""")
  avg_temp = cursor.fetchone()[0]
  if avg_temp is not None:
    print(f"Average temperature: {avg_temp:.2f} °C")
  else:
    print("No values found")
  conn.close()

def show_highest_eth_price():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT MAX(ethereum_price) FROM dashboard""")
  highest= cursor.fetchone()[0]
  if highest is not None:
    print(f"Highest ETH price Recorded : ${highest:.2f}")
  else:
    print("No data found")
  conn.close()

def show_latest_entry():
  conn = get_connection()
  cursor= conn.cursor()
  cursor.execute("""SELECT * FROM dashboard ORDER BY id DESC LIMIT 1""")
  row = cursor.fetchone()
  if row is not None:
    print("\nLatest Entry: ")
    print(f"🆔ID: {row[0]}")
    print(f"🕛Time: {row[1]}")
    print(f"🌡 Temperature °C: {row[2]}")
    print(f"💰Ethereum: ${row[3]:.2f}")
  else:
    print("No Entries found")
  #print(row)
  conn.close()



def show_lowest_temperature():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT MIN(temperature) FROM dashboard""")
  lowest = cursor.fetchone()[0]
  if lowest is not None:
   print(f"Lowest Temperature °C : {lowest:.2f} °C")
  else:
    print("No temperature data found")
  conn.close()


def main():
  temperature = get_temperature()
  eth_price = get_eth_price()
  joke = get_joke()

  now = datetime.now()
  current_time= now.strftime("%Y-%m-%d %H:%M:%S")


  print("\n======= MY DASHBOARD =======")
  print(f"🕒 Time        : {current_time}")
  if temperature is not None:
    print(f"🌡️  Temperature °C : {temperature}")
  else:
    print("Temperature : Unavailable")

  if eth_price is not None:
    print(f"💰 Ethereum    : ${eth_price:.2f}")
  else:
    print("Ethereum : Unavailable")

  if joke is not None:
    print(f"😂 Joke        : {joke}")
  else:
    print("Jokes : Not available")
  print("============================")

  save_to_file(current_time,temperature,eth_price,joke)

  save_to_csv(current_time,temperature,eth_price,joke)

  save_to_sqlite(current_time,temperature,eth_price,joke) 

  print("\nLast 5 entries")
  show_last_entries()
  show_total_entries()
  show_average_temperature()
  show_highest_eth_price()
  show_latest_entry()
  show_lowest_temperature()

if __name__ == "__main__":
  main()