import argparse
import sys
import numpy as np
import cyrilload
import difflib
import config
from entities import Image
from typing import Iterable, List
from npcompare import NPComparer

class NPImageComparer():
    """
    Compare to products
    """
    weights={"ah":1.0,"dh":0.1,"ph":0.1,"wh":0.9,"wdh":0.7,"name":0.3}

    def comp(self, i1:Image, i2:Image)->List[List[float]]:
        dico =  i1 - i2
        np = NPComparer()
        dico["dname"] = np.compvl(i1.name.split(".")[0], i2.name.split(".")[0])
        return dico

    def compare(self, i1:Image, i2:Image)->List[List[float]]:
        score = i1.size - i2.size
        if score == 1:
            return 1.0
        score = 1 - (i1.ah - i2.ah) / 64
        # if score > 0.9 or score < 0.2:
        #     return score
        res = [[score, NPImageComparer.weights["ah"]]]
        if i1.wh is not None and i2.wh is not None:
            score = 1 - (i1.wh - i2.wh) / 64
            res.append([score, NPImageComparer.weights["wh"]])
            #if score < 0.8 and score > 0.3:
        if i1.dh is not None and i2.dh is not None:
            score = 1 -(i1.dh - i2.dh) / 64
            res.append([score, NPImageComparer.weights["dh"]])
            #if score < 0.7 and score > 0.4:
        if i1.ph is not None and i2.ph is not None:
            score = 1 - (i1.ph - i2.ph) / 64
            res.append([score, NPImageComparer.weights["ph"]])
        if i1.wdh is not None and i2.wdh is not None:
            score = 1 - (i1.wdh - i2.wdh) / 196
            res.append([score, NPImageComparer.weights["wdh"]])
        score = sum([x[0] * x[1] for x in res]) / sum([x[1] for x in res])
        if score < 0.8 and score > 0.5:
            np = NPComparer()
            vscore = np.compvl(i1.name.split(".")[0], i2.name.split(".")[0])
            if vscore > score:
                score = (sum([x[0] * x[1] for x in res]) + vscore * NPImageComparer.weights["name"]) / (sum([x[1] for x in res]) + NPImageComparer.weights["name"])
        return score

if __name__ == '__main__':
    print("NPImageCompare")
    print("==============")
    parser = argparse.ArgumentParser()
    parser.add_argument("id1", help="Image id")
    parser.add_argument("id2", help="Image id to compare")
    args = parser.parse_args()
    db = cyrilload.load("data/imagemock.h.pickle")
    i1 = db[int(args.id1)]
    if i1 == None:
        print(f"{args.id1} does not exist")
        sys.exit(1)
    i2 = db[int(args.id2)]
    if i2 == None:
        print(f"{args.id2} does not exist")
        sys.exit(2)
    print(f"Compare image {i1.name} and {i2.name}")
    comparer = NPImageComparer()
    res = comparer.comp(i1, i2)
    print(res)
    print(comparer.compare(i1, i2))



