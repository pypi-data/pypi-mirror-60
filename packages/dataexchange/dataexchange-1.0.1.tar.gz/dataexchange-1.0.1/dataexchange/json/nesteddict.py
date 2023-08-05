from dataexchange.json.keyrename import dict_keyrename
from dataexchange.json.keyrename import list_keyrename


def nested_dict(data, raw_data, depth, keys):
    var_store = []
    for idx, item in enumerate(depth, 0):
        var_store.append(item)
        popper = data.pop(item)
        try:
            if isinstance(popper, dict):
                for key, val in keys.items():
                    popper[key]
                popper = dict_keyrename(popper, keys)
            elif isinstance(popper, list):
                x = popper[0]
                for key, val in keys.items():
                    x[key]
                popper = list_keyrename(popper, keys)
        except KeyError:
            pass
        data = popper
        if idx == 0:
            raw_data[var_store[0]] = data
        elif idx == 1:
            raw_data[var_store[0]][var_store[1]] = data
        else:
            pass
    return raw_data
