import json


class Json:
    def __new__(cls, val):
        return val if type(val) not in [list, dict] else super().__new__(cls)

    def __init__(self, obj) -> None:
        self.obj = obj

    def __getitem__(self, i):
        return Json(self.obj[i])

    def __getattr__(self, name):
        return Json(self.obj[name])

    def __str__(self):
        return json.dumps(self.obj, indent=2, sort_keys=True)
