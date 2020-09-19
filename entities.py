from typing import List


class Car:
    """
    Caracterristic entity
    """

    def __init__(self, id:int, val:str, w=1.0, main=False):
        """
        Car(id,val,w,main)
        :param id: cid
        :param val: value
        :param w: weight [0,1]
        :param main: The first car
        """
        self.id = id
        self.val = val
        self.w = w
        self.main = main
        self.h = None

    def __repr__(self):
        return f"C{self.id}"

class Product:
    """
    Product entity
    """

    def __init__(self, id:int):
        """
        Product(id)->Car
        :param id: id
        """
        self.id = id
        self.l:List[Car] = []

    def get_car_by_id(self, id:int)->Car:
        """
        Return the car by cid
        :param id: cid
        :return: The car or None
        """
        for c in self.l:
            if c.id == id:
                return c
        return None

    def contains(self, c:Car)->bool:
        """
        :param c: The car
        :return: bool
        """
        return self.get_car_by_id(c.id) != None

    def __repr__(self):
        return f"P{self.id}"


class Image:
    """
    POC
    """

    def __init__(self, id, path, size = 0):
        """
        Image
        :param id: image id
        :param path: h file path
        :param size: image size
        :arg ah: average : good for all images but false negative for photoshop image
        :arg dh: like ah but works with gradients : bad for all image but the best for photoshop image (lot of false negative, but very good positives)
        :arg ph: like ah but in frequencies domain (cosine transform) : bad for all image but good for photoshop image (dh redundant to remove ?)
        :arg wh: like ph with better transform : cost a lot, good like ah
        :arg wdh: optimization of wh : cost++, good but lot of false positives
        :arg zh: ah with z-scaler
        :arg pids: product id list
        :arg name: image name
        :arg ext: image extension
        """
        self.id = id
        self.path = path if path.startswith("./") else f"./{path}"
        self.size = size
        self.ah = None
        self.dh = None
        self.ph = None
        self.wh = None
        self.wdh = None
        self.zh = None
        self.pids = []
        self.ext = path.split(".")[-1]
        self.name = path.split("/")[-1].upper()

    def __sub__(self, other):
        res = {"dah":None, "ddh":None,"dph":None,"dwh":None,"dwdh":None, "dzh":None,"dsize":None,"dname":None}
        res["dsize"] = abs(self.size - other.size)
        if self.ah is not None and other.ah is not None:
            res["dah"] = 1 - (self.ah - other.ah) / len(self.ah.hash) ** 2
        if self.dh is not None and other.dh is not None:
            res["ddh"] = 1 - (self.dh - other.dh) / len(self.dh.hash) ** 2
        if self.ph is not None and other.ph is not None:
            res["dph"] = 1 - (self.ph - other.ph) / len(self.ph.hash) ** 2
        if self.wh is not None and other.wh is not None:
            res["dwh"] = 1 - (self.wh - other.wh) / len(self.wh.hash) ** 2
        if self.wdh is not None and other.wdh is not None:
            res["dwdh"] = 1 - (self.wdh - other.wdh) / len(self.wdh.hash) ** 2
        if self.zh is not None and other.zh is not None:
            res["dzh"] = 1 - (self.zh - other.zh) / len(self.zh.hash) ** 2
        return res

    def __repr__(self):
        return f"{self.name}"




