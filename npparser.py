import csv
import pickle
import json
import time
import use
import cyrilload
from entities import Product, Cat
from typing import Dict

class NPParser:

    def __init__(self):
        self.db:Dict[str,Product] = {}
        self.path = None

    def parse(self, path):
        self.path = path
        self.nbp = 0
        self.nbc = 0
        t = time.perf_counter()
        print(f"Parse {path}")
        with open(path) as f:
            r = csv.DictReader(f)
            for row in r:
                pid = row["pid"]
                if pid not in self.db:
                    self.db[pid] = Product(pid)#{"l":{}}
                    self.nbp += 1
                    main = True
                s = row["val"].strip()
                if len(s) > 0:
                    # c = {
                    #         "val":s,
                    #         "main":main,
                    #         "w":float(row["weight"]),
                    #         "h":None
                    #     }
                    c = Cat(row["cid"],s,float(row["weight"]),main)
                    main = False #Move after if
                    #self.db[pid]["l"][row["cid"]] = c
                    self.db[pid].l.append(c)
                    self.nbc += 1
        print(f"Found {self.nbp} products and {self.nbc} characteristics in {time.perf_counter() - t:.1f} s")

    def normalize(self):
        print(f"Normalize {self.nbc} weigths")
        for p in self.db.keys():
            sum = 0
            #cs = self.db[p]["l"]
            # for cid in cs.keys():
            #     sum += cs[cid]["w"]
            # for cid in cs.keys():
            #     cs[cid]["w"] = cs[cid]["w"] / sum
            for c in self.db[p].l:
                sum += c.w
            for c in self.db[p].l:
                c.w = c.w / sum

    def save(self, prefix="", method="pickle"):
        t = time.perf_counter()
        name = self.path.split(".")[0]
        cyrilload.save(self.db, name,prefix,method)
        print(f"Saved in {time.perf_counter() - t:.1f} s")

    def load(self, path):
        t = time.perf_counter()
        self.path = path
        self.db = cyrilload.load(path)
        self.nbp = len(self.db.keys())
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def h(self):
        print(f"Hashing with USE model")
        model = use.USE()
        t = time.perf_counter()
        i = 0
        for p in self.db.keys():
            if i % max(10,int(self.nbp / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbp} in {time.perf_counter() - t:.1f} s")
            #cs = self.db[p]["l"]
            #vals = []
            # for cid in cs.keys():
            #     vals.append(cs[cid]["val"])
            #     hs = model.hs(vals)
            #j = 0
            # for cid in cs.keys():
            #     if " " in cs[cid]["val"]:
            #         cs[cid]["h"] = hs[j].tolist()
            #     j+=1
            for c in self.db[p].l:
                if " " in c.val: # A changer si main contient un espace
                    #c.h = model.hs([c.val])[0].tolist()
                    c.h = model.h(c.val)
            i+=1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")

if __name__ == '__main__':
    print("NP Products Parser")
    print("==================")
    p = NPParser()
    p.parse("data/data.csv")
    p.normalize()
    p.save()
    p.save(method="jsonpickle")
    p.h() #230s / 10000
    p.save(prefix="h")
    if len(p.db.keys()) < 1000:
        p.save(prefix="h", method="jsonpickle")



