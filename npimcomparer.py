import argparse
import sys
import cyrilload
from entities import NPImage
from typing import List
from npproductcompare import NPComparer
from scipy import spatial


class NPImageComparer:
    """
    Compare to products
    """
    def __init__(self):
        self.weights = {"ah": 1.0, "dh": 1.0, "wh": 1.0, "fv": 3.0, "name": 0.1}
        # ah = average : good for all images but false negative for rephotoshop image
        # dh = ah but in gradients : bad for all image but the best for photoshop image (lot of false negative, but very good positives)
        # ph = ah but in frequencies domain (cosine transform) : bad for all image but good for photoshop image (dh redundant to remove)
        # wh = ph with Fourier : cost a lot, good like ah

    def diff(self, i1: NPImage, i2: NPImage) -> List[List[float]]:
        dico = i1 - i2
        np = NPComparer()
        dico["dn"] = round(np.compare_value_gestalt(i1.name.split(".")[0], i2.name.split(".")[0]), 3)
        return dico

    def compare(self, i1: NPImage, i2: NPImage, fast = False) -> List[List[float]]:
        """
        https://tech.okcupid.com/evaluating-perceptual-image-hashes-okcupid/
        http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
        http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        https://fullstackml.com/wavelet-image-hash-in-python-3504fdd282b5
        :param i1:
        :param i2:
        :return:
        """
        np = NPComparer()
        score = i1.size - i2.size
        if score == 0:
            return 1.0  # perfect
        res = []
        if i1.dh is not None and i2.dh is not None and not fast:
            dscore = 1 - (i1.dh - i2.dh) / 64
            if dscore > 0.84:  # Lot of false negative but perfect positives
                return (1 + dscore) / 2
            res.append([dscore, self.weights["dh"]])
        ascore = 1 - (i1.ah - i2.ah) / 64
        res.append([ascore, self.weights["ah"]])
        if i1.wh is not None and i2.wh is not None and not fast:
            score = 1 - (i1.wh - i2.wh) / 64  # Good like ah but expensive
            res.append([score, self.weights["wh"]])
        if i1.fv is not None and i2.fv is not None and not fast:
            score = 1 - spatial.distance.cosine(i1.fv, i2.fv)
            w = self.weights["fv"]
            if score > 0.9:
                w *= 2
            if score > 0.95:
                w *= 5
            res.append([score, w])
        score = sum([x[0] * x[1] for x in res]) / sum([x[1] for x in res])
        if 0.8 > score > 0.5:
            vscore = np.compare_value_gestalt(i1.name.split(".")[0], i2.name.split(".")[0])
            score = score + vscore * self.weights["name"]
        return score


if __name__ == '__main__':
    print("NPImageCompare")
    print("==============")
    parser = argparse.ArgumentParser(description="Compare images id1 & pid2")
    parser.add_argument("id1", help="Image id")
    parser.add_argument("id2", help="Image id to compare")
    args = parser.parse_args()
    db = cyrilload.load("data/mock-image.h.pickle")
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