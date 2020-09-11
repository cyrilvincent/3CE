import argparse
import npparser
import sys
import numpy as np

class NPUSEComparer():

    def compareh(self, h1, h2):
        h1 = np.array(h1)
        h2 = np.array(h2)
        return np.inner(h1, h2)

    def comparev(self, v1, v2):
        v1 = v1.upper()
        v2 = v2.upper()
        if v1 == v2:
            return 1
        if v1 in v2:
            return min(0.9, len(v1) / 10)
        if v2 in v1:
            return min(0.8, len(v2) / 10)


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
                    w = 1
                elif score == 0 and p1["l"][cid]["main"]:
                    w = 0.1
            res.append([score, w])

        return res

    # def total(self, wscores):
    #     return sum([t[0]*t[1] for t in wscores])

parser = argparse.ArgumentParser()
parser.add_argument("pid1", help="Product id")
parser.add_argument("pid2", help="Product id to compare")
args = parser.parse_args()
p = npparser.NPParser()
p.load("data/data.h.pickle")
p1 = p.db[args.pid1]
if p1 == None:
    print(f"{args.pid1} does not exist")
    sys.exit(1)
p2 = p.db[args.pid2]
if p2 == None:
    print(f"{args.pid2} does not exist")
    sys.exit(2)
comparer = NPUSEComparer()
res = comparer.comparep(p1, p2)
print(res)
#print(comparer.total(res))


