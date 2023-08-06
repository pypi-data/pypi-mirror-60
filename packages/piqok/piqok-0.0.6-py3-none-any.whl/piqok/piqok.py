import json
from typing import Any


class Json:
    def __new__(cls, val):
        if type(val) is dict:
            return super().__new__(cls)

        if type(val) is list:
            return [Json(e) for e in val]

        return val

    def __init__(self, obj) -> None:
        self.__dict__['obj'] = obj

    def __getitem__(self, i):
        return Json(self.__dict__['obj'][i])

    def __getattr__(self, name):
        try:
            return Json(self.__dict__['obj'][name])
        except:
            raise AttributeError()

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__['obj'][name] = value

    def __str__(self):
        return json.dumps(self.obj, indent=2, sort_keys=True)

    def __call__(self):
        return self.__dict__['obj']
