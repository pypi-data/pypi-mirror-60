from abc import ABCMeta, abstractmethod
import importlib
config = {}

class CAUtil:
    def __init__(self):
        self.config = config

    def init(self):
        print(config)
        return "a"

class EmailUtilInterface(CAUtil):
    def send(self):
        return None

def get_resource(resource_name):
    cls_name = config[resource_name]['vendor']
    cls = importlib.import_module('src.utils.{}.{}'.format(resource_name,cls_name))
    cls = getattr(cls, cls_name)
    obj = cls()
    return obj

def cautil_init(config_file_path):
    print(config_file_path)
    config['Email'] = {'vendor':'SendInBlue'}
    return None