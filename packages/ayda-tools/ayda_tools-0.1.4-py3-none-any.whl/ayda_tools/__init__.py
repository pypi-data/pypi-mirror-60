import os
from getpass import getuser
import json


class AydaConfig:
    def __init__(self):
        self.AYDA_CONFIG_PATH = "/home/{}/.ayda/aydarc".format(getuser())
        self.AYDA_DATA_PATH = ""

    def update(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])


config = AydaConfig()
if os.path.exists(config.AYDA_CONFIG_PATH):
    config.update(**json.load(open(config.AYDA_CONFIG_PATH)))

config.AYDA_DATA_PATH = os.environ.get("AYDA_DATA_PATH", config.AYDA_DATA_PATH)
