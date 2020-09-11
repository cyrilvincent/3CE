import npparser
import sys
import numpy as np
import time
import pickle
import npcompare

class NPNearest:

    def __init__(self, path):
        t = time.perf_counter()
        print(f"Load {path}")
        with open(path, "rb") as f:
            self.db = pickle.load(f)
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def get_by_id(self, pid):
        return self.db[pid]

    def search(self, p, take=10):
        res = []
        comp = npcompare.NPComparer()
        for k in self.db.keys():
            p2 = self.get_by_id(k)
            if p != p2:
                score = comp.compare(p, p2)
                if score > 0.5:
                    res.append([k, score])
        res.sort(key = lambda x : x[1], reverse = True)
        return res[:take]

if __name__ == '__main__':
    print("NPNearest")
    print("=========")
    np = NPNearest("data/mock.h.pickle")
    while True:
        pid = input("PID: ")
        p = np.get_by_id(pid)
        res = np.search(p)
        print(res)

