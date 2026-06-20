import requests

url = "http://api.coingecko.com/api/v3/simple/price"

params ={
  "ids" : "ethereum",
  "vs_currencies" : "usd"
}

response = requests.get(url,params = params)
data = response.json()

print("Ethereum Price: ", data ["ethereum"]["usd"],"USD")
