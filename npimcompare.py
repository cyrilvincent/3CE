import argparse
import sys
import cyrilload
import config
import math
from entities import Image
from typing import Iterable, List
from npcompare import NPComparer

class NPImageComparer():
    """
    Compare to products
    """
    def __init__(self):
        self.weights={"ah":1.0,"dh":0.2,"ph":0.1,"wh":0.9,"wdh":0.7, "zh":0.9,"name":0.3}
        self.thresolds = {"ah": 0.79, "dh": 0.7, "ph": 0.69, "wh": 0.77, "wdh": 0.76, "zh": 0.78, "name": 0.3}
        # ah = average : good for all images but false negative for rephotoshop image
        # dh = ah but in gradients : bad for all image but the best for photshop image (lot of false negative, but very good positives)
        # ph = ah but in frequencies domain (cosine transform) : bad for all image but good for photoshop image (dh redundant to remove)
        # wh = ph with Fourier : cost a lot, good like ah
        # wdh = optimization of wh : cost++, good but lot of false positives

    def comp(self, i1:Image, i2:Image)->List[List[float]]:
        dico =  i1 - i2
        np = NPComparer()
        dico["dname"] = np.compvl(i1.name.split(".")[0], i2.name.split(".")[0])
        return dico

    def activation(self, x, thresold):
        res = ((math.tanh((x - thresold) * 3 * 0.5 / (1 - thresold)) + 1) / 2) * 7/5
        return res

    def compare(self, i1:Image, i2:Image, activation = True)->List[List[float]]:
        """
        https://tech.okcupid.com/evaluating-perceptual-image-hashes-okcupid/
        :param i1:
        :param i2:
        :return:
        """
        score = i1.size - i2.size
        if score == 1:
            return 1.0
        ascore = 1 - (i1.ah - i2.ah) / 64
        #score = (1 + ascore) / 2 if ascore > 0.78 else (0.5 + ascore) / 2
        score = ascore
        if activation:
            score = self.activation(ascore, self.thresolds["ah"])
        res = [[score, self.weights["ah"]]]
        if i1.zh is not None and i2.zh is not None:
            score = 1 - (i1.zh - i2.zh) / 64
            #score = (1 + score) / 2 if score > 0.78 else score / 2
            if activation:
                score = self.activation(score, self.thresolds["zh"])
            res.append([score, self.weights["zh"]])
        if i1.dh is not None and i2.dh is not None:
            score = 1 -(i1.dh - i2.dh) / 64
            #score = (1 + score) / 2 if score > 0.69 else ascore
            if activation:
                score = self.activation(score, self.thresolds["dh"])
            res.append([score, self.weights["dh"]])
        if i1.ph is not None and i2.ph is not None: # To remove
            score = 1 - (i1.ph - i2.ph) / 64
            #score = (1 + score) / 2 if score > 0.68 else ascore
            if activation:
                score = self.activation(score, self.thresolds["ph"])
            res.append([score, self.weights["ph"]])
        if i1.wh is not None and i2.wh is not None:
            score = 1 - (i1.wh - i2.wh) / 64
            #score = (1 + score) / 2 if score > 0.76 else score / 2
            if activation:
                score = self.activation(score, self.thresolds["wh"])
            res.append([score, self.weights["wh"]])
        if i1.wdh is not None and i2.wdh is not None:
            score = 1 - (i1.wdh - i2.wdh) / 196
            #score = (1 + score) / 2 if score > 0.76 else score / 2
            if activation:
                score = self.activation(score, self.thresolds["wdh"])
            res.append([score, self.weights["wdh"]])
        score = sum([x[0] * x[1] for x in res]) / sum([x[1] for x in res])
        if score < 0.8 and score > 0.5:
            np = NPComparer()
            vscore = np.compvl(i1.name.split(".")[0], i2.name.split(".")[0])
            if vscore > score:
                score = (sum([x[0] * x[1] for x in res]) + vscore * self.weights["name"]) / (sum([x[1] for x in res]) + self.weights["name"])
        # score *= 7/5 # 50% = 70% in npnearest
        # if score > 1:
        #     score = 1.0
        return score

if __name__ == '__main__':
    print("NPImageCompare")
    print("==============")
    parser = argparse.ArgumentParser()
    parser.add_argument("id1", help="Image id")
    parser.add_argument("id2", help="Image id to compare")
    args = parser.parse_args()
    db = cyrilload.load("data/imagemock.h.pickle")
    i1 = db[0][int(args.id1)]
    if i1 == None:
        print(f"{args.id1} does not exist")
        sys.exit(1)
    i2 = db[0][int(args.id2)]
    if i2 == None:
        print(f"{args.id2} does not exist")
        sys.exit(2)
    print(f"Compare image {i1.name} and {i2.name}")
    comparer = NPImageComparer()
    res = comparer.comp(i1, i2)
    print(res)
    print(comparer.compare(i1, i2, True))
    print(comparer.compare(i1, i2, False))



