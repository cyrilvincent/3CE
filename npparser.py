import csv
import pickle
import json
import time
import use
import cyrilload
import config
from entities import Product, Car
from typing import Dict

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class NPParser: #Not thread safe

    def __init__(self):
        self.db:Dict[int,Product] = {}
        self.path = None

    def parse(self, path):
        self.path = path
        self.nbp = 0
        self.nbc = 0
        t = time.perf_counter()
        print(f"Parse {path}")
        with open(path) as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                pid = int(row["product_id"])
                if pid not in self.db:
                    self.db[pid] = Product(pid)
                    self.nbp += 1
                    main = True
                s = "" if row["valeur"] == None else row["valeur"].strip()
                if len(s) > 0:
                    c = Car(int(row["carac_id"]), s, float(row["poids"]), main)
                    self.db[pid].l.append(c)
                self.nbc += 1
                main = False
        print(f"Found {self.nbp} products and {self.nbc} characteristics in {time.perf_counter() - t:.1f} s")

    def normalize(self):
        print(f"Normalize {self.nbc} weigths")
        for p in self.db.keys():
            sum = 0
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
            for c in self.db[p].l:
                if " " in c.val and len(c.val) > 4:
                    c.h = model.h(c.val)
            i+=1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")

    def index(self, path):
        self.parse(path)
        self.normalize()
        self.h()
        self.save(prefix="h")

if __name__ == '__main__':
    print("NP Products Parser")
    print("==================")
    p = NPParser()
    #p.index(config.data_file)
    p.parse("data/data.txt") #Found 3904 products and 23342 characteristics (6 carac)
    p.normalize()
    p.save()
    p.save(method="jsonpickle")
    p.h() #230s / 10000*5 soit 38 minutes pour 100K*5, 48s / 3904*15
    p.save(prefix="h")
    if len(p.db.keys()) < 1000:
        p.save(prefix="h", method="jsonpickle")



