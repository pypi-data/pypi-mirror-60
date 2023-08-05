def list_keyrename(data, keys):
    output_list = []

    for item in data:
        for key, value in keys.items():
            try:
                item.update({value: item.pop(key)})
            except KeyError as e:
                return f"KeyError: {e} key not exist."
        output_list.append(item)
    return output_list


def dict_keyrename(data, keys):
    for key, value in keys.items():
        try:
            data.update({value: data.pop(key)})
        except KeyError as e:
            return f"KeyError: {e} key not exist."
    return data
