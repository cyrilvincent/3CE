from typing import List
from scipy import spatial


class Car:
    """
    Caracteristic entity
    """

    def __init__(self, id: int, val: str, w=1.0, main=False):
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

    def __init__(self, id: int):
        """
        Product(id)->Car
        :param id: id
        """
        self.id = id
        self.l: List[Car] = []

    def get_car_by_id(self, id: int) -> Car:
        """
        Return the car by cid
        :param id: cid
        :return: The car or None
        """
        for c in self.l:
            if c.id == id:
                return c
        return None

    def contains(self, c: Car) -> bool:
        """
        :param c: The car
        :return: bool
        """
        return self.get_car_by_id(c.id) is not None

    def __repr__(self):
        return f"P{self.id}"


class NPImage:
    """
    POC
    """

    def __init__(self, id, path, fid, size=0):
        """
        Image
        :param id: image id
        :param path: h file path
        :param size: image size
        :arg ah: average : good for all images but false negative for photoshop image
        :arg dh: like ah but works with gradients : bad for all image but the best for photoshop image (lot of false negative, but very good positives)
        :arg ph: like ah but in frequencies domain (cosine transform) : bad for all image but good for photoshop image (dh redundant to remove ?)
        :arg wh: like ph with better transform : cost a lot, good like ah
        :arg pids: product id list
        :arg name: image name
        :arg ext: image extension
        """
        self.fid = fid
        self.id = id
        self.path = path if path.startswith("./") else f"./{path}"
        self.size = size
        self.ah = None
        self.dh = None
        self.fv = None
        self.sean = None
        self.iean = None
        self.pids = []
        self.ext = path.split(".")[-1].upper()
        self.name = path.split("/")[-1].upper()

    def __sub__(self, other):
        res = {"dah": None, "ddh": None, "dfv": None, "dsize": abs(self.size - other.size), "dn": None, "dean": None}
        if self.ah is not None and other.ah is not None:
            res["dah"] = round(1 - (self.ah - other.ah) / len(self.ah.hash) ** 2, 3)
        if self.dh is not None and other.dh is not None:
            res["ddh"] = round(1 - (self.dh - other.dh) / len(self.dh.hash) ** 2, 3)
        if self.fv is not None and other.fv is not None:
            res["dfv"] = round(1 - spatial.distance.cosine(self.fv, other.fv), 3)
        if self.iean is not None and other.iean is not None:
            res["dean"] = abs(self.iean - other.iean)
        return res

    def __repr__(self):
        return f"{self.name}"
