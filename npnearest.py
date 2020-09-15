import time
import npcompare
import cyrilload

class NPNearest:

    def __init__(self, path):
        self.path = path
        self.reset()

    def reset(self):
        t = time.perf_counter()
        self.db = cyrilload.load(self.path)
        self.cache = {}
        self.comp = npcompare.NPComparer()
        for k in list(self.db.keys())[:2]:
            self.search(k)
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def get_by_id(self, pid):
        return self.db[pid]

    def searchl(self, pid, pid2s):
        res = []
        for pid2 in pid2s:
            p = self.get_by_id(pid)
            p2 = self.get_by_id(pid2)
            score = self.comp.comparel(p, p2)
            res.append([pid2, score])
        return res

    def search(self, pid, take=10):
        if pid in self.cache.keys():
            return self.cache[pid][:take]
        else:
            p = self.get_by_id(pid)
            res1 = []
            for k in self.db.keys():
                p2 = self.get_by_id(k)
                if p.id != p2.id:
                    score = self.comp.compare(p, p2)
                    if score > 0.4:
                        res1.append([k, score])
            res1.sort(key = lambda x : x[1], reverse = True)
            res1 = res1[:(take * 4)]
            #print(res1)
            res2 = self.searchl(p.id, [p2[0] for p2 in res1])
            #print(res2)
            res = []
            for x in zip(res1, res2):
                v = (x[0][1] + x[1][1]) / 2
                res.append([x[0][0], v])
            res.sort(key=lambda x: x[1], reverse=True)
            res = [r for r in res if r[1] >= 0.5]
            res = res[:take]
            self.cache[pid] = res
            return res

if __name__ == '__main__':
    print("NPNearest")
    print("=========")
    np = NPNearest("data/data.h.pickle")
    while True:
        pid = int(input("PID: "))
        t = time.perf_counter()
        try:
            res = np.search(pid,10)
        except KeyError:
            print(f"Product {pid} does not exist")
            res=[]
        print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.1f} s") #1.7s / 10000*5 7s / 100K*2
        for p in res:
            print(f"PID {p[0]} at {p[1]*100:.0f}%")

