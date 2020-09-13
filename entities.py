class Product:

    def __init__(self, id):
        self.id = id
        self.l = []

class Cat:

    def __init__(self, id, val, w=1.0, main=False):
        self.id = id
        self.val = val
        self.w = w
        self.main = main
