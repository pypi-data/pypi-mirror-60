import requests
from dataexchange.json.exchange import JsonExchange


req = requests.get("https://cricapi.com/api/matches?apikey=KLBozKlsnufyvBAnMsbO61kSuS42")
print(type(req.json()))


jsx = JsonExchange(req.json())
result = jsx.key_rename(keys={'matches': 'data'})
print(type(result), result)
