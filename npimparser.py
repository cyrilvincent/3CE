import csv
import time
import cyrilload
import config
import imagehash
import entities
import numpy as np
from typing import Dict
from PIL import Image


import os

class NPImageParser:
    """
    Image parser and indexer
    Not thread safe
    """

    def __init__(self):
        self.db:Dict[int,entities.Image] = {}
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
                if iid not in self.db:
                    self.db[iid] = entities.Image(iid,row["image_path"])
                    self.nbi += 1
                pid = int(row["product_id"])
                if pid not in self.db[iid].pids:
                    self.db[iid].pids.append(pid)
        print(f"Found {self.nbi} images in {time.perf_counter() - t:.1f} s")

    def save(self, prefix="", method="pickle")->None:
        """
        Save the db
        :param prefix: see cyrilload
        :param method: see cyrilload
        """
        t = time.perf_counter()
        name = self.path.split(".")[0]
        cyrilload.save(self.db, name,prefix,method)
        print(f"Saved in {time.perf_counter() - t:.1f} s")

    def h(self, impath, dh = True, ph = True, wh = True, wdh=True, zh=True)->None:
        """
        Use hashing
        """
        print(f"Hashing with ImageHash model")
        t = time.perf_counter()
        i = 0
        for k in self.db.keys():
            if i % max(10,int(self.nbi / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbi} in {time.perf_counter() - t:.1f} s")
            im = self.db[k]
            im.size = os.stat(impath+im.path)[6]
            pil = Image.open(impath+im.path)
            im.ah = imagehash.average_hash(pil)  # 8x8
            if dh:
                im.dh = imagehash.dhash(pil)  # 8x8
            if ph:
                im.ph = imagehash.phash(pil)  # 8x8
            if wh:
                im.wh = imagehash.whash(pil)  # Haar 8x8
            if wdh:
                im.wdh = imagehash.whash(pil, mode="db4")  # Daubechies 14x14
            if zh:
                im.zh = imagehash.average_hash(self.ztransform(pil))
            i+=1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")

    def index(self, path:str):
        """
        Main method to parse, normalize, hash and save
        :param path: The file to parse
        """
        self.parse(path)
        self.save(prefix="h")

    def alpharemover(self, image):
        if image.mode != 'RGBA':
            return image
        canvas = Image.new('RGBA', image.size, (255,255,255,255))
        canvas.paste(image, mask=image)
        return canvas.convert('RGB')

    def ztransform(self, image):
        image = self.alpharemover(image)
        image = image.convert("L").resize((8, 8), Image.ANTIALIAS)
        data = image.getdata()
        quantiles = np.arange(100)
        quantiles_values = np.percentile(data, quantiles)
        zdata = (np.interp(data, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
        image.putdata(zdata)
        return image

if __name__ == '__main__':
    print("NP Images Parser")
    print("================")
    p = NPImageParser()
    #p.index(config.data_file)
    p.parse("data/imagemock.txt") #Found 63 images in 0s
    p.save()
    p.save(method="jsonpickle")
    count = len(p.db)
    wdh = count < 5000
    wh = count < 100000
    ph = count < 10000 # Bad perf and dh redundant
    dh = count < 150000
    zh = count < 200000
    p.h("images/", dh = dh, ph = dh, wh = wh, wdh=wdh) #All 59s / 63 soit 16min / 1000 et <3h / 10000 32s
    p.save(prefix="h")                                          #Sans wdh 32s / 63 soit 9 min / 1000 et <1.5h / 10000 et 15h
                                                                #Sans w*h 6.3s / 63 soit 100s / 1000 et 17 min / 10000 et <3h pour 100000
                                                                #Que ah 4s / 63 soit 64s / 1000 et 11 min / 10000 et <2h pour 100000




