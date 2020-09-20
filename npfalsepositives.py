import cyrilload
import argparse
import numpy as np

class ImFalsePositives:

    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.fppath = dbpath.split(".")[0]
        self.load()

    def reset(self):
        self.set = set()

    def save(self):
        cyrilload.save(self.set, self.fppath, prefix="fp")
        cyrilload.save(self.set, self.fppath, prefix="fp", method="json")

    def load(self):
        self.set = cyrilload.load(self.fppath+".fp.pickle")

    def add(self, id1, id2):
        try:
            self.set.add((min(id1, id2), max(id1, id2)))
        except:
            pass

    def retrain(self, id1, id2, db): # Non fiable !
        im1 = db[0][id1]
        res1 = []
        for k in db[0].keys():
            im = db[0][k]
            if im1.id != im.id:
                score = (im1.ah - im.ah) / 64
                if score > 0.9:
                    res1.append(k)
        im2 = db[0][id2]
        res2 = []
        for k in db[0].keys():
            im = db[0][k]
            if im2.id != im.id:
                score = (im2.ah - im.ah) / 64
                if score > 0.9:
                    res2.append(k)
        res = list(np.intersect1d(res1, res2))
        res.append(id1)
        res.append(id2)
        for i in res:
            for j in res:
                if i != j:
                    #self.add(i, j)
                    print(i, j)

    def remove(self, id1, id2):
        try:
            self.set.remove((min(id1, id2), max(id1, id2)))
        except:
            pass

    def match(self, id1, id2):
        return (min(id1, id2), max(id1, id2)) in self.set

if __name__ == '__main__':
    print("NP Image False Positive")
    print("=======================")
    fp = ImFalsePositives("data/imagemock.h.pickle")
    print(fp.set)
    parser = argparse.ArgumentParser()
    parser.add_argument("id1", type=int, help="Image id 1")
    parser.add_argument("id2", type=int, help="Image id 2")
    args = parser.parse_args()
    #fp.reset()
    print(f"Add {args.id1} {args.id2} to FP")
    #fp.add(args.id1, args.id2)
    db = cyrilload.load("data/imagemock.h.pickle")
    fp.retrain(args.id1, args.id1, db)
    #fp.remove(1,2)
    fp.save()
    print(fp.set)


