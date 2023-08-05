___
## DataExchange : A Python module to work on JSON.  

**```DataExchange``` is a Reusable ```python``` app which provides many features to work on ```JSON```.**
___


## Installation :  
**You can install ```DataExchange``` module from PyPI using ```pip```**.  

``` pip install dataexchange ```
___


## Configurations :  
**In order to use ```dataexchange``` module in ```python``` you need to ```import``` it.**  

```python
from dataexchange.json.exchange import JsonExchange  
```
___


## Features :  
1\. **```Re-Name``` The ```Keys``` of ```JSON``` Data in ```Runtime```**  
>>> When JSON data in json file.  
```python
from dataexchange.json.exchange import JsonExchange  
jsx = JsonExchange("JSON_File_Name.json")
```


2\. **```Re-Name``` The ```Keys``` of ```JSON``` Data in ```Runtime```**  
>>> When JSON data come from ```requests``` object.  
```python
import requests  
from dataexchange.json.exchange import JsonExchange  

req = requests.get("https://cricapi.com/api/matches?apikey=KLuy78452poolnufyBAnb61S2")  
print(type(req.json()))  

jsx = JsonExchange(req.json())  
result = jsx.key_rename(keys={'matches': 'data'})  
print(type(result), result)  

```
___