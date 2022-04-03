import math
import difflib
from typing import List, Optional
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
        self.fid = None

    def get_car_by_id(self, id: int) -> Optional[Car]:
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

    def __init__(self, id: int, path: str, fid: Optional[int], size=0):
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
        self.ocr = None
        self.color = None
        self.pids = []
        self.ext = path.split(".")[-1].upper()
        self.name = path.split("/")[-1].upper()

    def __sub__(self, other):
        res = {"dah": None, "ddh": None, "dfv": None, "dsize": abs(self.size - other.size), "dn": None, "dean": None, "docr": None, "dc": None}
        if self.ah is not None and other.ah is not None:
            res["dah"] = 1 - (self.ah - other.ah) / len(self.ah.hash) ** 2
        if self.dh is not None and other.dh is not None:
            res["ddh"] = 1 - (self.dh - other.dh) / len(self.dh.hash) ** 2
        if self.fv is not None and other.fv is not None:
            res["dfv"] = 1 - spatial.distance.cosine(self.fv, other.fv)
        if self.iean is not None and other.iean is not None:
            if len(self.sean) == len(other.sean) and self.iean >= 10000 and other.iean >= 10000:
                res["dean"] = min(1.0, max(1 - math.log(abs(self.iean - other.iean + 0.1)) / 10, 0) + 0.01)
            else:
                res["dean"] = 0.0
        if self.ocr is not None and other.ocr is not None:
            res["docr"] = self.gestalt(self.ocr, other.ocr) if len(self.ocr) > 2 else 0
        if hasattr(other, "color") and self.color is not None and other.color is not None:
            res["dc"] = 1 if self.color == other.color else 0
        if self.name is not None and other.name is not None:
            res["dn"] = self.gestalt(self.name.split(".")[0], other.name.split(".")[0])
        return res

    def gestalt(self, s1: str, s2: str) -> float:
        sm = difflib.SequenceMatcher(None, s1.upper(), s2.upper())
        return sm.ratio()

    def __repr__(self):
        return f"{self.name}"
