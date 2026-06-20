import requests
import json

def get_temperature(latitude,longitude):
  url = "https://api.open-meteo.com/v1/forecast"

  params = {
    "latitude": latitude,
    "longitude": longitude,
    "current" : "temperature_2m"
  }

  response = requests.get(url,params = params)
  data = response.json()
  print(json.dumps(data,indent=4))
  return data["current"]["temperature_2m"]
temp = get_temperature(12.97 , 77.59)
print(f"Current temperature: {temp} deg C")