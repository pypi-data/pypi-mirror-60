from dataexchange.json.encoders import jsonencoder
from dataexchange.json.keyrename import list_keyrename
from dataexchange.json.keyrename import dict_keyrename
from dataexchange.json.nesteddict import nested_dict


class JsonExchange(object):

    def __init__(self, data):
        if isinstance(data, str):
            self.data = jsonencoder(data)
        else:
            self.data = data
        self.raw_data = self.data

    def key_rename(self, depth=None, keys=None):
        if keys:
            if isinstance(self.data, list):
                return list_keyrename(self.data, keys)
            elif isinstance(self.data, dict):
                if depth:
                    return nested_dict(self.data, self.raw_data, depth, keys)
                else:
                    return dict_keyrename(self.data, keys)
            else:
                return f"{type(self.data)} Data Type is not Accepted."
        else:
            return "Key(s) not provided."
