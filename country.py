import requests

url = "http://restcountries.com/v3.1/name/india"
response = requests.get(url,timeout =5)
data = response.json()
print(response.status_code)
print(response.text[:200])