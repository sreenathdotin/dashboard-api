import requests
import json

response = requests.get("https://official-joke-api.appspot.com/random_joke",timeout = 5)
data = response.json()
print(json.dumps(data,indent =4))
print(data)
print("Setup: ")
print(data["setup"])
print("\nPunchline:")
print(data["punchline"])