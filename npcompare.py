import argparse
import sys
import numpy as np
import cyrilload
import difflib

class NPComparer():

    def compareh(self, h1, h2):
        h1 = np.array(h1)
        h2 = np.array(h2)
        return np.inner(h1, h2)

    def comparev(self, v1, v2):
        v1 = v1.upper()
        v2 = v2.upper()
        if v1 == v2:
            return 1.0
        if v1 in v2:
            return min(0.9, len(v1) / 10)
        if v2 in v1:
            return min(0.8, len(v2) / 10)

    def comparel(self, v1, v2):
        sm = difflib.SequenceMatcher(lambda x: x in " \t.!?,;\n", v1.upper(), v2.upper())
        return sm.ratio()

    def comparep(self, p1, p2):
        res = []
        for cid in p1["l"].keys():
            h1 = p1["l"][cid]["h"]
            h2 = None
            w = p1["l"][cid]["w"]
            if cid in p2["l"]:
                h2 = p2["l"][cid]["h"]
            score = 0
            if h1 != None and h2 != None:
                score = self.compareh(h1,h2)
            elif h1 == None and h2 == None and cid in p2["l"]:
                score = self.comparev(p1["l"][cid]["val"], p2["l"][cid]["val"])
                if score == 1 and p1["l"][cid]["main"]:
                    w = 1.0
                elif score == 0 and p1["l"][cid]["main"]:
                    w = 0.1
            res.append([score, w])
        return res

    def comparepl(self, p1, p2):
        res = []
        for cid in p1["l"].keys():
            v1 = p1["l"][cid]["val"].upper()
            v2 = ""
            w = p1["l"][cid]["w"]
            if cid in p2["l"]:
                v2 = p2["l"][cid]["val"].upper()
            score = 0
            score = self.comparel(v1,v2)
            if len(v1) == 2:
                w /= 2
            elif len(v1) == 1:
                w /= 4
            res.append([score, w])
        return res

    def compare(self, p1, p2):
        wscores = self.comparep(p1, p2)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

    def compare2(self, p1, p2):
        wscores = self.comparepl(p1, p2)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

if __name__ == '__main__':
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
    comparer = NPComparer()
    res = comparer.comparep(p1, p2)
    print(res)
    print(comparer.compare(p1, p2))
    res = comparer.comparepl(p1, p2)
    print(res)
    print(comparer.compare2(p1, p2))


