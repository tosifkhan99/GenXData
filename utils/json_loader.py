import json


def read_json(filename):
    with open(filename, "r") as f:
        return json.load(f)
