import csv
import time
import cyrilload
import config
import imagehash
import entities
import numpy as np
import os
import tensorflow as tf
from typing import Dict
from PIL import Image
from absl import logging


class NPImageService:
    """
    https://pypi.org/project/ImageHash/
    """

    model = None

    def __init__(self, path):
        self.path = path
        if NPImageService.model is None:
            t = time.perf_counter()
            print(f"Load TF FV model: ")
            NPImageService.model = tf.saved_model.load(config.tf_fv)
            print(f"Loaded in {time.perf_counter() - t:.1f} s")
            logging.set_verbosity(logging.ERROR)
        self.pil = Image.open(path)
        self.size = os.stat(path)[6]
        self.tfimg = None

    def ah(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.average_hash(self.pil)

    def a2h(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.average_hash(self.pil, hash_size=16)

    def dh(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
        :return:
        """
        return imagehash.dhash(self.pil)

    def wh(self):
        """
        #https://fullstackml.com/wavelet-image-hash-in-python-3504fdd282b5
        :return:
        """
        return imagehash.whash(self.pil)

    def fv(self):
        """
        https://towardsdatascience.com/image-similarity-detection-in-action-with-tensorflow-2-0-b8d9a78b2509
        :return:
        """
        if self.tfimg is None:
            self.tfimg = self.load_img(self.path)
        features = NPImageService.model(self.tfimg)
        return np.squeeze(features)

    def load_img(self, path):
        img = tf.io.read_file(path)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize_with_pad(img, 224, 224)
        img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        return img


class NPImageParser:
    """
    Image parser and indexer
    Not thread safe
    """

    def __init__(self):
        self.dbi: Dict[int, entities.NPImage] = {}
        self.dbp: Dict[int, int] = {}
        self.db = [self.dbi, self.dbp]
        self.path = None
        self.nbi = 0

    def parse(self, path: str) -> None:
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
                    self.dbi[iid] = entities.NPImage(iid, row["image_path"], int(row["family_id"]))
                    self.nbi += 1
                pid = int(row["product_id"])
                if pid not in self.dbi[iid].pids:
                    self.dbi[iid].pids.append(pid)
                if pid not in self.dbp:
                    self.dbp[pid] = []
                if iid not in self.dbp[pid]:
                    self.dbp[pid].append(iid)
        print(f"Found {self.nbi} images in {time.perf_counter() - t:.1f} s")

    def save(self, prefix="", method="pickle") -> None:
        """
        Save the db
        :param prefix: see cyrilload
        :param method: see cyrilload
        """
        t = time.perf_counter()
        name = self.path.split(".")[0]
        cyrilload.save(self.db, name, prefix, method)
        print(f"Saved in {time.perf_counter() - t:.1f} s")

    def h(self, impath, dh=True, wh=False, a2h=False, fv=True) -> None:
        """
        Use hashing
        """
        print(f"Hashing with ImageHash model")
        t = time.perf_counter()
        i = 0
        for k in self.dbi.keys():
            if i % max(10, int(self.nbi / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbi} in {time.perf_counter() - t:.1f} s")
            im = self.dbi[k]
            try:
                ih = NPImageService(impath + im.path)
                im.size = ih.size
                im.ah = ih.ah()  # 8x8 64s/1000
                if dh:
                    im.dh = ih.dh()  # 8x8
                if wh:
                    im.wh = ih.wh()  # Haar 8x8 408s/1000
                if a2h:
                    im.a2h = ih.a2h()  # ah 16x16 <64s/1000?
                if fv:
                    im.fv = ih.fv()  # Tensorflow Feature Vector 1792x1 95s/1000
            except Exception as ex:
                print(f"Error with {im}: {ex}")
            i += 1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")

    def train(self, path: str):
        """
        Main method to parse, normalize, hash and save
        :param path: The file to parse
        """
        self.parse(path)
        self.h("images/")
        self.save(prefix="h")


if __name__ == '__main__':
    print("NP Images Parser")
    print("================")
    p = NPImageParser()
    p.parse("data/imagemock.txt")  # Found 63 images in 0s x
    count = len(p.dbi)
    p.save()
    p.save(method="jsonpickle")
    wh = count < 10000  # A virer ?
    dh = count < 50000
    a2h = count < 30000  # A virer donne trop de poids à ah ?
    fv = count < 100000
    p.h("images/", dh=dh, wh=wh, a2h=a2h, fv=fv)  # All 70s / 103 soit 12min / 1000 et 2h / 10000
    p.save(prefix="h")                                          # Sans wdh 32s / 63 soit 9 min / 1000 et <1.5h / 10000 et 15h
                                                                # Sans w*h 6.3s / 63 soit 100s / 1000 et 17 min / 10000 et <3h pour 100000
                                                                # Que ah + fv 10s / 63 soit 159s / 1000 et 27 min / 10000 et <5h pour 100000
                                                                # Que ah 4s / 63 soit 64s / 1000 et 11 min / 10000 et <2h pour 100000




