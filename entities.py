from typing import List

class Product:

    def __init__(self, id):
        self.id = id
        self.l:List[Cat] = []

    def get_cat_by_id(self, id):
        for c in self.l:
            if c.id == id:
                return c
        return None

    def contains(self, c):
        return self.get_cat_by_id(c.id) != None

    def __repr__(self):
        return f"P{self.id}"

class Cat:

    def __init__(self, id, val, w=1.0, main=False):
        self.id = id
        self.val = val
        self.w = w
        self.main = main
        self.h = None

    def __repr__(self):
        return f"C{self.id}"
