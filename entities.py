from typing import List

class Product:

    def __init__(self, id):
        self.id = id
        self.l:List[Car] = []

    def get_car_by_id(self, id):
        for c in self.l:
            if c.id == id:
                return c
        return None

    def contains(self, c):
        return self.get_car_by_id(c.id) != None

    def __repr__(self):
        return f"P{self.id}"

class Car:

    def __init__(self, id, val, w=1.0, main=False):
        self.id = id
        self.val = val
        self.w = w
        self.main = main
        self.h = None

    def __repr__(self):
        return f"C{self.id}"

class Image:

    def __init__(self, path, size = 0):
        self.path = path
        self.size = size
        self.ah = None
        self.dh = None
        self.ph = None
        self.wh = None
        self.wdh = None
        self.pids = []
        self.ext = path.split(".")[-1]
        if "/" in path:
            self.name = path.split("/")[-1]
        else:
            self.name = path

    def __sub__(self, other):
        res = {"dah":None, "ddh":None,"dph":None,"dwh":None,"dwdh":None,"dsize":None,"dname":None}
        res["dsize"] = self.size == other.size
        res["dname"] = self.name == other.name
        if self.ah != None and other.ah != None:
            res["dah"] = (self.ah - other.ah) / len(self.ah.hash) ** 2
        if self.dh != None and other.dh != None:
            res["ddh"] = (self.dh - other.dh) / len(self.dh.hash) ** 2
        if self.ph != None and other.ph != None:
            res["dph"] = (self.ph - other.ph) / len(self.ph.hash) ** 2
        if self.wh != None and other.wh != None:
            res["dwh"] = (self.wh - other.wh) / len(self.wh.hash) ** 2
        if self.wdh != None and other.wdh != None:
            res["dwdh"] = (self.wdh - other.wdh) / len(self.wdh.hash) ** 2
        return res

    def __repr__(self):
        return f"I {self.name}"




