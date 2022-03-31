import csv
import time
import cyrilload
import config
import imagehash
import entities
import numpy as np
import os
import tensorflow as tf
import argparse
from typing import Dict
from PIL import Image
from absl import logging
from npimagebarcode import NpImageBarcode
from npimageocr import NpImageOcr


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
        # Sortir les 3 lignes suivantes dans une méthode
        self.pil = Image.open(path) # im = Image.open(BytesIO(base64.b64decode(b64)))
        self.size = os.stat(path)[6]
        self.tfimg = None

    def ah(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.average_hash(self.pil)

    def dh(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
        :return:
        """
        return imagehash.dhash(self.pil)

    def fv(self):
        """
        https://towardsdatascience.com/image-similarity-detection-in-action-with-tensorflow-2-0-b8d9a78b2509
        :return:
        """
        if self.tfimg is None:
            self.tfimg = self.load_img(self.path)
        features = NPImageService.model(self.tfimg)
        return np.squeeze(features)

    def ean(self):
        np = NpImageBarcode()
        sean = np.predict(self.path)
        if sean is not None:
            print(f"Found EAN: {sean}")
        iean = np.parse_int(sean)
        return sean, iean

    def ocr(self):
        np = NpImageOcr()
        s = np.predict_string(self.path)
        if s is not None:
            print(f"Found OCR: {s}")
        return s

    def load_img(self, path):
        img = tf.io.read_file(path) # Peut être remplacé par tf.io.decode_base64
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
                ipath = row["Image-Path"].strip().replace("\\","/")
                if ipath != "#N/A" and ipath != "":
                    iid = int(row["Image-ID"])
                    if iid not in self.dbi:
                        self.dbi[iid] = entities.NPImage(iid, ipath, int(row["Famille-ID"]))
                        self.nbi += 1
                    pid = int(row["Product-ID"])
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

    def save_empty(self, path="data/empty-image"):
        db = [{}, {}]
        cyrilload.save(db, path, method="pickle")

    def h(self, impath, dh=True, fv=True, ean=True, ocr=True) -> None:
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
                im.ah = ih.ah()  # 8x8 7.8s/1000
                if dh:
                    im.dh = ih.dh()  # 8x8 0.7s/1000
                if fv:
                    im.fv = ih.fv()  # Tensorflow Feature Vector 1792x1 22s/1000
                if ean:
                    im.sean, im.iean = ih.ean()
                if ocr:
                    im.ocr = ih.ocr()
            except Exception as ex:
                logging.warning(f"Error with {im}: {ex}")
            i += 1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")


if __name__ == '__main__':
    print("NP Images Parser")
    print("================")
    parser = argparse.ArgumentParser(description="Image TXT Parser to h.pickle")
    parser.add_argument("instance", help="Instance")
    parser.add_argument("-p", "--path", help="Path to the txt file", default="data/data.txt")
    parser.add_argument("-e", "--empty", action="store_true", help="Create empty pickle")
    args = parser.parse_args()
    p = NPImageParser()
    if args.empty:
        p.save_empty()
    p.parse(f"data/{args.instance}-image.txt")
    count = len(p.dbi)
    p.save()
    p.save(method="jsonpickle")
    dh = count < 400000
    fv = count < 100000
    ean = count < 50000
    ocr = count < 1000
    p.h(f"{config.image_path}/{args.instance}/", dh=dh, fv=fv, ean=ean, ocr=ocr)
    # 305 in 9.7s, 32s/1000, 320s/10000, 3200s/100000
    # ean in 18.7s
    p.save(prefix="h")


