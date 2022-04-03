import argparse
import sys
import cyrilload
from entities import NPImage
from typing import List
from np_product_compare import NPComparer


class NPImageComparer:
    """
    Compare to products
    """
    def __init__(self):
        self.weights = {"ah": 0.5, "dh": 0.2, "fv": 1.0, "name": 0.1, "ean": 0.5, "ocr": 0.5, "color": 0.2}
        # ah = average : good for all images but false negative for rephotoshop image
        # dh = ah but in gradients : bad for all image but the best for photoshop image (lot of false negative, but very good positives)
        # ph = ah but in frequencies domain (cosine transform) : bad for all image but good for photoshop image (dh redundant to remove)
        # wh = ph with Fourier : cost a lot, good like ah

    def diff(self, i1: NPImage, i2: NPImage) -> List[List[float]]:
        dico = i1 - i2
        return dico

    def compare(self, i1: NPImage, i2: NPImage, fast=False, name=True) -> float:
        """
        https://tech.okcupid.com/evaluating-perceptual-image-hashes-okcupid/
        http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
        http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        https://fullstackml.com/wavelet-image-hash-in-python-3504fdd282b5
        :param fast:
        :param i1:
        :param i2:
        :return:
        """
        # np = NPComparer()
        scores = i1 - i2
        if scores["dsize"] == 0:
            return 1.0
        if scores["dean"] == 1:
            return 1.0
        res = []
        if scores["dah"] is not None:
            res.append([scores["dah"], self.weights["ah"]])
        if scores["ddh"] is not None and not fast:
            res.append([scores["ddh"], self.weights["dh"]])
        if scores["dfv"] is not None and not fast:
            score = scores["dfv"]
            w = self.weights["fv"]
            if score > 0.9:
                w *= 1.5
            if score > 0.95:
                w *= 2
            res.append([score, w])
        if scores["dn"] is not None and name:
            score = scores["dn"]
            res.append([score, self.weights["name"]])
        if scores["dean"] is not None and not fast:
            score = scores["dean"]
            w = self.weights["ean"]
            if score > 0.9:
                w *= 2
            if score > 0.95:
                w *= 2
            res.append([score, w])
        if scores["docr"] is not None and not fast:
            score = scores["docr"]
            w = self.weights["ocr"]
            if score > 0.75:
                w *= 2
            if len(i2.ocr) > 7:
                w *= 2
            if score > 0.82 and len(i2.ocr) > 10:
                w *= 2
            if score > 0.9 and len(i2.ocr) > 10:
                w *= 4
            res.append([score, w])
        if scores["dc"] is not None:
            score = scores["dc"]
            res.append([score, self.weights["color"]])
        total = sum([x[1] for x in res])
        if total == 0:
            return 0
        score = sum([x[0] * x[1] for x in res]) / total
        return score


if __name__ == '__main__':
    print("NPImageCompare")
    print("==============")
    parser = argparse.ArgumentParser(description="Compare images id1 & id2")
    parser.add_argument("id1", help="Image id")
    parser.add_argument("id2", help="Image id to compare")
    args = parser.parse_args()
    db = cyrilload.load("data/chuv-image.h.pickle")
    i1 = db[0][int(args.id1)]
    if i1 is None:
        print(f"{args.id1} does not exist")
        sys.exit(1)
    i2 = db[0][int(args.id2)]
    if i2 is None:
        print(f"{args.id2} does not exist")
        sys.exit(2)
    print(f"Compare image {i1.name} and {i2.name}")
    comparer = NPImageComparer()
    res = comparer.diff(i1, i2)
    print(res)
    print(comparer.compare(i1, i2))

    # 266846 266849