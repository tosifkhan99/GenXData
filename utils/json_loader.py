import json


def read_json(filename):
    with open(filename) as f:
        return json.load(f)
