
class Config(dict):
    __getattr__, __setattr__ = dict.get, dict.__setitem__