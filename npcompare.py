import argparse
import sys
import numpy as np
import cyrilload
import difflib
from entities import Product, Car

class NPComparer():

    def comph(self, h1, h2):
        # h1 = np.array(h1)
        # h2 = np.array(h2)
        return np.inner(h1, h2)

    def compv(self, v1, v2):
        v1 = v1.upper()
        v2 = v2.upper()
        if v1 == v2:
            return 1.0
        if v1 in v2:
            return min(0.75, len(v1) / 10)
        if v2 in v1:
            return min(0.5, len(v2) / 10)
        return 0

    def compvl(self, v1, v2):
        try:
            n1 = float(v1)
            n2 = float(v2)
            if n1 == n2:
                score = 1
            else:
                score = (1 - min(1, (abs(n1 - n2) / n1))) / 2
            return score
        except:
            sm = difflib.SequenceMatcher(lambda x: x in " \t.!?,;\n", v1.upper(), v2.upper())
            return sm.ratio()

    def compp(self, p1:Product, p2:Product):
        res = []
        for c1 in p1.l:
            score = 0
            w = c1.w
            if p2.contains(c1):
                c2 = p2.get_car_by_id(c1.id)
                if c1.main:
                    score = self.compv(c1.val, c2.val)
                    if score > 0.99:
                        w = 2
                    else:
                        if c1.h != None and c2.h != None:
                            score = (score + self.comph(c1.h, c2.h)) / 2
                        if score < 0.8:
                            w = 0.1
                else:
                    if c1.h != None and c2.h != None:
                        score = self.comph(c1.h, c2.h)
                    else:
                        score = self.compv(c1.val, c2.val)
            else :
                w /= 2
            res.append([score, w])
        return res

    def comppl(self, p1:Product, p2:Product):
        res = []
        for c1 in p1.l:
            score = 0
            w = c1.w
            if p2.contains(c1):
                c2 = p2.get_car_by_id(c1.id)
                v1 = c1.val.upper()
                v2 = c2.val.upper()
                score = self.compvl(v1, v2)
                if c1.main:
                    if score > 0.99:
                        w = 2
                    elif score < 0.8:
                        w = 0.1
                w /= min(1, abs(3-len(v1)) + 1)
            else:
                w /= 2
            res.append([score, w])
        return res

    def compare(self, p1, p2):
        wscores = self.compp(p1, p2)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

    def comparel(self, p1, p2):
        wscores = self.comppl(p1, p2)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

def display(p1:Product, p2:Product, res):
    limit = 40
    i = 0
    total = sum([w[1] for w in res])
    for r in res:
        c = p1.l[i]
        s = f"CID:{c.id} match {res[i][0] * 100:.0f}% * {res[i][1] / total:0.2f} \""
        s += f"{c.val[:limit]}"
        if len(c.val) > limit:
            s += "..."
        s += '" vs "'
        if p2.contains(c):
            s += p2.get_car_by_id(c.id).val[:limit]
            if len(p2.get_car_by_id(c.id).val) > limit:
                s+="..."
        s += '"'
        print(s)
        i += 1

if __name__ == '__main__':
    print("NPCompare")
    print("=========")
    parser = argparse.ArgumentParser()
    parser.add_argument("pid1", help="Product id")
    parser.add_argument("pid2", help="Product id to compare")
    args = parser.parse_args()
    db = cyrilload.load("data/data.h.pickle")
    p1 = db[int(args.pid1)]
    if p1 == None:
        print(f"{args.pid1} does not exist")
        sys.exit(1)
    p2 = db[int(args.pid2)]
    if p2 == None:
        print(f"{args.pid2} does not exist")
        sys.exit(2)
    print(f"Compare products {p1.id} and {p2.id}")
    comparer = NPComparer()
    res = comparer.compp(p1, p2)
    print("Deep Learning Google DAN USE model:")
    display(p1,p2,res)
    print(f"USE Score: {comparer.compare(p1, p2)*100:.0f}%")
    print()
    print("Machine Learning Gestalt+Cyril model:")
    res = comparer.comppl(p1, p2)
    display(p1,p2,res) #[[1.0, 2.0], [1.0, 0.125], [0.2696548171045853, 0.125], [0.0, 0.125], [0, 0.0625], [0, 0.0625], [0, 0.0625]]
    print(f"Gestalt Score: {comparer.comparel(p1, p2) * 100:.0f}%")
    print()
    print(f"Final Score: {(comparer.compare(p1, p2) + comparer.comparel(p1, p2)) / 2 * 100:.0f}%")


