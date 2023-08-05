import json


def jsonencoder(data):
    with open(data) as file:
        obj = file.read()
        obj = json.loads(obj)
        return obj
