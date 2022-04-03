import base64
import csv
import time
from io import BytesIO

import cyrilload
import config
import imagehash
import entities
import numpy as np
import os
import tensorflow as tf
import argparse
from typing import Dict, List
from PIL import Image
from absl import logging
from np_image_barcode import NpImageBarcode
from np_image_ocr import NpImageOcr
from np_image_color_detect import ColorDetect, dictionary10


class NPImageService:
    """
    https://pypi.org/project/ImageHash/
    """

    model = None

    def __init__(self): # sortir le path d'ici dans une méthode load
        self.path = None
        if NPImageService.model is None:
            t = time.perf_counter()
            print(f"Load TF FV model: ")
            NPImageService.model = tf.saved_model.load(config.tf_fv)
            print(f"Loaded in {time.perf_counter() - t:.1f} s")
            logging.set_verbosity(logging.ERROR)
        self.pil = None
        self.size = None
        self.tfimg = None
        self.color_detect = ColorDetect(dictionary10)

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
        # if self.tfimg is None:
        #     self.tfimg = self.load_img(self.path)
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
        return s

    def color(self):
        self.color_detect.load(self.path)
        res = self.color_detect.predict()
        return res[0][0]

    def load_tfimg(self, path):
        img = tf.io.read_file(path)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize_with_pad(img, 224, 224)
        img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        return img

    def load_tfimg_from_base64(self, b64: str):
        img = tf.io.decode_base64(b64)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize_with_pad(img, 224, 224)
        img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        return img

    def load(self, path):
        self.path = path
        self.pil = Image.open(path)
        self.size = os.stat(path)[6]
        self.tfimg = self.load_tfimg(path)

    def load_from_base64(self, b64: str):
        self.pil = Image.open(BytesIO(base64.b64decode(b64)))
        self.size = self.pil.size
        self.tfimg = self.load_tfimg(b64)


class NPImageParser:
    """
    Image parser and indexer
    Not thread safe
    """

    def __init__(self):
        self.dbi: Dict[int, entities.NPImage] = {}
        self.dbp: Dict[int, List[int]] = {}
        self.db = [self.dbi, self.dbp]
        self.path = None
        self.nbi = 0
        self.num_row = 1

    def parse(self, path: str, encoding="utf-8") -> None:
        """
        Parser
        :param path: TXT file to parse
        """
        self.path = path
        self.nbi = 0
        t = time.perf_counter()
        print(f"Parse {path}")
        with open(path, encoding=encoding) as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                self.num_row += 1
                ipath = row["image_path"]
                if ipath is not None:
                    ipath = ipath.strip().replace("\\","/").replace(".eps", ".png")
                    if ipath != "#N/A" and ipath != "":
                        iid = int(row["image_id"]) # bug
                        iid = self.num_row
                        if iid not in self.dbi:
                            self.dbi[iid] = entities.NPImage(iid, ipath, int(row["family_id"]))
                            self.nbi += 1
                        pid = int(row["product_id"])
                        if pid not in self.dbi[iid].pids:
                            self.dbi[iid].pids.append(pid)
                        if pid not in self.dbp:
                            self.dbp[pid] = []
                        if iid not in self.dbp[pid]:
                            self.dbp[pid].append(iid)
                else:
                    print(f"No image_path at row {self.num_row}")

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

    def h(self, impath, dh=True, fv=True, ean=True, ocr=True, color=True) -> None:
        """
        Use hashing
        """
        print(f"Hashing")
        t = time.perf_counter()
        i = 0
        for k in self.dbi.keys():
            if i % 10 == 0:
                print(f"Hash {i + 1}/{self.nbi} in {time.perf_counter() - t:.0f} s")
            im = self.dbi[k]
            try:
                ih = NPImageService()
                ih.load(impath + im.path)
                print(im.path[(im.path.rindex("/") + 1):])
                im.size = ih.size
                im.ah = ih.ah()  # 8x8 7.8s/1000
                if dh:
                    im.dh = ih.dh()  # 8x8 0.7s/1000
                if fv:
                    im.fv = ih.fv()  # Tensorflow Feature Vector 1792x1 22s/1000
                if ean:
                    im.sean, im.iean = ih.ean()
                if color:
                    im.color = ih.color()
                    print(im.color)
                if ocr:
                    try:
                        im.ocr = ih.ocr()
                        if im.ocr is not None:
                            print(im.ocr)
                    except Exception as ex:
                        print(f"Warning: OCR {im}: {ex}")
            except Exception as ex:
                print(f"Error: {im}: {ex}")
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
    p.parse(f"data/{args.instance}-image.txt", encoding="utf-8-sig")
    count = len(p.dbi)
    p.save()
    p.save(method="jsonpickle")
    dh = count < 400000
    fv = count < 100000
    ean = False and count < 50000
    ocr = count < 1000
    color = True
    p.h(f"{config.image_path}/{args.instance}/", dh=dh, fv=fv, ean=ean, ocr=ocr, color=color)
    # 305 in 9.7s, 32s/1000, 320s/10000, 3200s/100000
    # ean in 18.7s
    p.save(prefix="h")


