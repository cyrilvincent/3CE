import argparse
import sys
import numpy as np
import cyrilload
import difflib
from entities import Product, Cat

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
            return min(0.9, len(v1) / 10)
        if v2 in v1:
            return min(0.8, len(v2) / 10)
        return 0

    def compvl(self, v1, v2):
        sm = difflib.SequenceMatcher(lambda x: x in " \t.!?,;\n", v1.upper(), v2.upper())
        return sm.ratio()

    def compp(self, p1:Product, p2:Product):
        res = []
        #for cid in p1["l"].keys():
        for c in p1.l:
            h1 = c.h #p1["l"][cid]["h"]
            h2 = None
            w = c.w #p1["l"][cid]["w"]
            if p2.contains(c): #if cid in p2["l"]:
                h2 = p2.get_cat_by_id(c.id).h #p2["l"][cid]["h"]
            score = 0
            main = c.main #p1["l"][cid]["main"]
            if h1 != None and h2 != None:
                score = self.comph(h1, h2)
                # if main:
                #     w = 1.0 if score > 0.95 else 0.1
            #elif (h1 == None or h2 == None) and cid in p2["l"]:

            # A changer si main contient un espace
            elif (h1 == None or h2 == None) and p2.get_cat_by_id(c.id) != None:
                #score = self.compv(p1["l"][cid]["val"], p2["l"][cid]["val"])
                score = self.compv(c.val, p2.get_cat_by_id(c.id).val)
                if score == 1 and main:
                    w = 1.0
                elif score == 0 and main:
                    w = 0.1
            elif main:
                w = 0.1
            res.append([score, w])
        return res

    def comparepl(self, p1:Product, p2:Product):
        res = []
        #for cid in p1["l"].keys():
        for c in p1.l:
            v1 = c.val.upper() #p1["l"][cid]["val"].upper()
            v2 = ""
            w = c.w #p1["l"][cid]["w"]
            #if cid in p2["l"]:
            if p2.contains(c):
                v2 = p2.get_cat_by_id(c.id).val.upper() #p2["l"][cid]["val"].upper()
            score = self.compvl(v1, v2)
            # if p1["l"][cid]["main"] and score < 0.8:
            #     w = 0.1
            # elif p1["l"][cid]["main"] and score > 0.99:
            #     w = 1.0
            if c.main and score < 0.8:
                w = 0.1
            elif c.main and score > 0.99:
                w = 1.0
            elif len(v1) == 2:
                w /= 2
            elif len(v1) == 1:
                w /= 4
            res.append([score, w])
        return res

    def compare(self, p1, p2):
        wscores = self.compp(p1, p2)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

    def comparel(self, p1, p2):
        wscores = self.comparepl(p1, p2)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

    # def diff(self, p1, p2):
    #     s1 = ""
    #     s2 = ""
    #     for k in p1["l"].keys():
    #         s1 += p1["l"][k]["val"] + "\n"
    #     for k in p2["l"].keys():
    #         s2 += p1["l"][k]["val"] + "\n"
    #     d = difflib.Differ()
    #     ss = d.compare(s1.splitlines(1), s2.splitlines(1))
    #     return list(ss)

def display(p1:Product, p2:Product, res):
    print(res)
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
            s += p2.get_cat_by_id(c.id).val[:limit]
            if len(p2.get_cat_by_id(c.id).val) > limit:
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
    p1 = db[args.pid1]
    if p1 == None:
        print(f"{args.pid1} does not exist")
        sys.exit(1)
    p2 = db[args.pid2]
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
    print("Machine Learning Gestalt model:")
    res = comparer.comparepl(p1, p2)
    display(p1,p2,res)
    print(f"Gestalt Score: {comparer.comparel(p1, p2) * 100:.0f}%")
    print()
    print(f"Final Score: {max(comparer.compare(p1, p2), comparer.comparel(p1, p2)) * 100:.0f}%")


