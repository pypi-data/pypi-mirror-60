def jsonify_object_dict(obj):
    if isinstance(obj, list):
        return [jsonify_object_dict(obj_child) for obj_child in obj]
    else:
        json_obj = {}
        if (len(obj) == 1) and ("value" in obj):
            return obj.value
        for key, val in obj.items():
            if isinstance(val, str):
                if (key == "value") and (not val.strip()):
                    continue
                json_obj[key] = val
            elif isinstance(val, dict) and (len(val) == 1) and ("value" in val):
                json_obj[key] = val["value"]
            else:
                json_obj[key] = jsonify_object_dict(val)
    return json_obj
