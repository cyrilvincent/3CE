import csv
import time
import cyrilload
import config
import imagehash
import entities
import numpy as np
import shazim
from typing import Dict
from PIL import Image


import os

class NPImageParser:
    """
    Image parser and indexer
    Not thread safe
    """

    def __init__(self):
        self.dbi:Dict[int, entities.Image] = {}
        self.dbp: Dict[int, int] = {}
        self.db = [self.dbi, self.dbp]
        self.path = None

    def parse(self, path:str)->None:
        """
        Parser
        :param path: TXT file to parse
        """
        self.path = path
        self.nbi = 0
        t = time.perf_counter()
        print(f"Parse {path}")
        with open(path) as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                iid = int(row["image_id"])
                if iid not in self.dbi:
                    self.dbi[iid] = entities.Image(iid, row["image_path"])
                    self.nbi += 1
                pid = int(row["product_id"])
                if pid not in self.dbi[iid].pids:
                    self.dbi[iid].pids.append(pid)
                if pid not in self.dbp:
                    self.dbp[pid] = []
                if iid not in self.dbp[pid]:
                    self.dbp[pid].append(iid)
        print(f"Found {self.nbi} images in {time.perf_counter() - t:.1f} s")

    def save(self, prefix="", method="pickle")->None:
        """
        Save the db
        :param prefix: see cyrilload
        :param method: see cyrilload
        """
        t = time.perf_counter()
        name = self.path.split(".")[0]
        cyrilload.save(self.db, name, prefix, method)
        print(f"Saved in {time.perf_counter() - t:.1f} s")

    def h(self, impath, dh = True, ph = True, wh = True, wdh=True, zh=True)->None:
        """
        Use hashing
        """
        print(f"Hashing with ImageHash model")
        t = time.perf_counter()
        i = 0
        for k in self.dbi.keys():
            if i % max(10,int(self.nbi / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbi} in {time.perf_counter() - t:.1f} s")
            im = self.dbi[k]
            ih = shazim.ShazImage(impath + im.path)
            im.size = ih.size
            im.ah = ih.ah()  # 8x8
            if dh:
                im.dh = ih.dh()  # 8x8
            if ph:
                im.ph = ih.ph()  # 8x8
            if wh:
                im.wh = ih.wh()  # Haar 8x8
            if wdh:
                im.wdh = ih.wdh()  # Daubechies 14x14
            if zh:
                im.zh = ih.zh()
            i+=1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")

    def train(self, path:str):
        """
        Main method to parse, normalize, hash and save
        :param path: The file to parse
        """
        self.parse(path)
        self.save(prefix="h")



if __name__ == '__main__':
    print("NP Images Parser")
    print("================")
    p = NPImageParser()
    #p.index(config.data_file)
    p.parse("data/imagemock.txt") #Found 63 images in 0s
    p.save()
    p.save(method="jsonpickle")
    count = len(p.dbi)
    wdh = count < 6000
    wh = count < 10000
    ph = False
    dh = count < 100000
    zh = count < 30000
    p.h("images/", dh = dh, ph = ph, wh = wh, wdh=wdh) #All 59s / 63 soit 16min / 1000 et <3h / 10000 32s
    p.save(prefix="h")                                          #Sans wdh 32s / 63 soit 9 min / 1000 et <1.5h / 10000 et 15h
                                                                #Sans w*h 6.3s / 63 soit 100s / 1000 et 17 min / 10000 et <3h pour 100000
                                                                #Que ah 4s / 63 soit 64s / 1000 et 11 min / 10000 et <2h pour 100000




