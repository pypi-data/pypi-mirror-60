import sys
import json

from .config_class import Config


def load_json_config(filename):
    config = Config()

    with open(filename, "r") as f:
        d = json.load(f)
        config.update(d)

    return config

    