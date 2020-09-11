import argparse
import sys
import numpy as np
import cyrilload
import difflib

class NPComparer():

    def comph(self, h1, h2):
        h1 = np.array(h1)
        h2 = np.array(h2)
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

    def compvl(self, v1, v2):
        sm = difflib.SequenceMatcher(lambda x: x in " \t.!?,;\n", v1.upper(), v2.upper())
        return sm.ratio()

    def compp(self, p1, p2):
        res = []
        for cid in p1["l"].keys():
            h1 = p1["l"][cid]["h"]
            h2 = None
            w = p1["l"][cid]["w"]
            if cid in p2["l"]:
                h2 = p2["l"][cid]["h"]
            score = 0
            if h1 != None and h2 != None:
                score = self.comph(h1, h2)
                if p1["l"][cid]["main"]:
                    w = 1.0 if score > 0.5 else 0.1
            elif h1 == None and h2 == None and cid in p2["l"]:
                score = self.compv(p1["l"][cid]["val"], p2["l"][cid]["val"])
                if score == 1 and p1["l"][cid]["main"]:
                    w = 1.0
                elif score == 0 and p1["l"][cid]["main"]:
                    w = 0.1
            elif p1["l"][cid]["main"]:
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
            score = self.compvl(v1, v2)
            if p1["l"][cid]["main"] and score < 0.5:
                w = 0.1
            elif p1["l"][cid]["main"] and score > 0.5:
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

    def diff(self, p1, p2):
        s1 = ""
        s2 = ""
        for k in p1["l"].keys():
            s1 += p1["l"][k]["val"] + "\n"
        for k in p2["l"].keys():
            s2 += p1["l"][k]["val"] + "\n"
        d = difflib.Differ()
        ss = d.compare(s1.splitlines(1), s2.splitlines(1))
        return list(ss)

def display(p1, p2, res):
    limit = 40
    i = 0
    ks = list(p1["l"].keys())
    for r in res:
        k = ks[i]
        s = f"CID:{k} match {res[i][0] * 100:.0f}% * {res[i][1]:0.2f} \""
        if k in p1['l']:
            s += f"{p1['l'][k]['val'][:limit]}"
            if len(p1['l'][k]['val']) > limit:
                s+="..."
        s += '" vs "'
        if k in p2['l']:
            s += f"{p2['l'][k]['val'][:limit]}"
            if len(p2['l'][k]['val']) > limit:
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


