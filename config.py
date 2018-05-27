"""
Created by Edward Schwalb
When using this config, please credit the author
"""
import json


class Config:
    def __init__(self,dct):
        for key in dct:
            if type(dct[key]) is dict:
                dct[key] = Config(dct[key])
            elif type(dct[key]) is list:
                dct[key] = [Config(i) if type(i) is dict else i for i in dct[key]]
        self.__dict__.update(dct)

def load_json_config(filename):
    return Config(json.load(open(filename, 'r')))
