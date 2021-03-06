import argparse
import sys
import cyrilload
import math
import config
from entities import NPImage
from typing import List
from npproductcompare import NPComparer
from scipy import spatial


class NPImageComparer:
    """
    Compare to products
    """
    def __init__(self):
        self.weights = {"ah": 0.6, "dh": 0.4, "fv": 1.0, "name": 0.05, "ean": 0.1}
        # ah = average : good for all images but false negative for rephotoshop image
        # dh = ah but in gradients : bad for all image but the best for photoshop image (lot of false negative, but very good positives)
        # ph = ah but in frequencies domain (cosine transform) : bad for all image but good for photoshop image (dh redundant to remove)
        # wh = ph with Fourier : cost a lot, good like ah

    def diff(self, i1: NPImage, i2: NPImage) -> List[List[float]]:
        dico = i1 - i2
        np = NPComparer()
        dico["dn"] = round(np.compare_value_gestalt(i1.name.split(".")[0], i2.name.split(".")[0]), 3)
        return dico

    def compare(self, i1: NPImage, i2: NPImage, fast=False) -> List[List[float]]:
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
        np = NPComparer()
        score = i1.size - i2.size
        if score == 0:
            return 1.0
        if i1.sean is not None and i1.sean == i2.sean:
            return 0.99
        res = []
        ascore = 1 - (i1.ah - i2.ah) / 64
        res.append([ascore, self.weights["ah"]])
        if i1.dh is not None and i2.dh is not None and not fast:
            dscore = 1 - (i1.dh - i2.dh) / 64
            res.append([dscore, self.weights["dh"]])
        if i1.fv is not None and i2.fv is not None and not fast:
            score = 1 - spatial.distance.cosine(i1.fv, i2.fv)
            w = self.weights["fv"]
            if score > 0.9:
                w *= 1.5
            if score > 0.95:
                w *= 2
            res.append([score, w])
        score = sum([x[0] * x[1] for x in res]) / sum([x[1] for x in res])
        if 0.9 > score > 0.7 and not fast:
            vscore = np.compare_value_gestalt(i1.name.split(".")[0], i2.name.split(".")[0])
            score = score + vscore * self.weights["name"]
            if i1.iean is not None and i2.iean is not None:
                escore = max(1 - math.log(abs(i1.iean - i2.iean + 0.1)) / 10, 0)
                escore = escore + 0.1 if len(i1.sean) == len(i2.sean) else escore
                score = score + escore * self.weights["ean"]
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