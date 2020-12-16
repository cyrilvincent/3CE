import cyrilload
import argparse
import numpy as np
import threading

class NPFalsePositives:

    lock = threading.RLock()
    set = set()

    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.fppath = dbpath.split(".")[0]
        self.load()

    def reset(self):
        with NPFalsePositives.lock:
            NPFalsePositives.set.clear()

    def save(self):
        cyrilload.save(NPFalsePositives.set, self.fppath, prefix="fp")
        #cyrilload.save(NPFalsePositives.set, self.fppath, prefix="fp", method="json")

    def load(self):
        try:
            NPFalsePositives.set = cyrilload.load(self.fppath + ".fp.pickle")
        except:
            NPFalsePositives.set = set()
            self.save()

    def add(self, id1, id2):
        try:
            with NPFalsePositives.lock:
                NPFalsePositives.set.add((min(id1, id2), max(id1, id2)))
        except:
            pass

    # def retrain(self, id1, id2, db): # Non fiable !
    #     im1 = db[0][id1]
    #     res1 = []
    #     for k in db[0].keys():
    #         im = db[0][k]
    #         if im1.id != im.id:
    #             score = (im1.ah - im.ah) / 64
    #             if score > 0.95:
    #                 res1.append(k)
    #     im2 = db[0][id2]
    #     res2 = []
    #     for k in db[0].keys():
    #         im = db[0][k]
    #         if im2.id != im.id:
    #             score = (im2.ah - im.ah) / 64
    #             if score > 0.95:
    #                 res2.append(k)
    #     res = list(np.intersect1d(res1, res2))
    #     res.append(id1)
    #     res.append(id2)
    #     for i in res:
    #         for j in res:
    #             if i != j:
    #                 #self.add(i, j)
    #                 print(i, j)

    def remove(self, id1, id2):
        try:
            with NPFalsePositives.lock:
                NPFalsePositives.set.remove((min(id1, id2), max(id1, id2)))
        except:
            pass

    def match(self, id1, id2):
        return (min(id1, id2), max(id1, id2)) in NPFalsePositives.set

if __name__ == '__main__':
    print("NP Ids False Positive")
    print("=====================")
    fp = NPFalsePositives("data/imagemock.h.pickle")
    print(fp.set)
    parser = argparse.ArgumentParser(description="Add id1 & id2 to blacklist")
    parser.add_argument("id1", type=int, help="id 1", default=-1)
    parser.add_argument("id2", type=int, help="id 2", default=-1)
    parser.add_argument("-r","--remove", action="store_true", help="Remove id1 & id2 from blacklist")
    parser.add_argument("-c", "--clear", action="store_true", help="Clear the blacklist")
    parser.add_argument("-l", "--list", action="store_true", help="List the blacklist")
    parser.add_argument("-m", "--match", action="store_true", help="Check if id1 & id2 are in the list")
    args = parser.parse_args()
    if args.clear:
        fp.reset()
        fp.save()
    elif args.remove:
        fp.remove(args.id1, args.id2)
        fp.save()
    elif args.match:
        print(fp.match(args.id1, args.id2))
    elif args.list:
        pass
    else:
        print(f"Add {args.id1} {args.id2} to FP")
        fp.add(args.id1, args.id2)
        db = cyrilload.load("data/imagemock.h.pickle")
        #fp.retrain(args.id1, args.id1, db)
        fp.save()
    print(fp.set)


