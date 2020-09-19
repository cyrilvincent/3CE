import time
import npcompare
import cyrilload
import config
import sys
from entities import Product
from typing import List

class NPNearest:
    """
    High level class, main program
    """

    def __init__(self, path, caching = True, reset = True):
        """
        Found pids nearest
        :param path: the path of the .h.pickle index file
        :param caching: enabling cache
        """
        self.path = path
        self.caching = caching
        if reset:
            self.reset()

    def reset(self)->None:
        """
        Reload the h.pickle file
        Reset the cache
        """
        t = time.perf_counter()
        self.db = cyrilload.load(self.path)
        self.cache = {}
        self.comp = npcompare.NPComparer()
        # for k in list(self.db.keys())[:2]:
        #     self.search(k)
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def get_by_id(self, pid:int)->Product:
        """
        Get the product by pid
        :param pid: product's pid
        :return: The product or None
        """
        return self.db[pid]

    def searchl(self, pid:int, pid2s:List[int], main = False)->List[List[float]]:
        """
        Search nearest by Gestalt model
        :param pid: pid
        :param pid2s: Array of pid to search nearest
        :return: List[List[pid,score]]
        """
        res = []
        for pid2 in pid2s:
            p = self.get_by_id(pid)
            p2 = self.get_by_id(pid2)
            score = self.comp.comparel(p, p2, main)
            res.append([pid2, score])
        return res

    def search(self, pid:int, take=10, main=False)->List[List[float]]:
        """
        The main search method
        Perf pb for 100k (7s)
        Put the cache in static, NPParser serialize the cache before h process, then run search on pids in cache
        :param pid: the product pid
        :param take: nb max product to return
        :param main: search on the main car only
        :return: List[List[pid,score]]
        """
        if pid in self.cache.keys():
            return self.cache[pid][:take]
        else:
            p = self.get_by_id(pid)
            res1 = []
            for k in self.db.keys():
                p2 = self.get_by_id(k)
                if p.id != p2.id:
                    score = self.comp.compare(p, p2, main)
                    if score > config.score_thresold:
                        res1.append([k, score])
            res1.sort(key = lambda x : x[1], reverse = True)
            res1 = res1[:(take * config.take_ratio)]
            #print(res1)
            res2 = self.searchl(p.id, [p2[0] for p2 in res1], main)
            #print(res2)
            res = []
            for x in zip(res1, res2):
                v = (x[0][1] + x[1][1]) / 2
                res.append([x[0][0], v])
            res.sort(key=lambda x: x[1], reverse=True)
            res = [r for r in res if r[1] > 0.5]
            if self.caching:
                self.cache[pid] = res
            res = res[:take]
            return res


if __name__ == '__main__':
    print("NPNearest")
    print("=========")
    main = False
    try:
        main = sys.argv[1] == "-mainonly"
        if main:
            print("Main only")
    except:
        pass
    np = NPNearest(config.h_file)
    while True:
        pid = int(input("PID: "))
        t = time.perf_counter()
        try:
            p = np.get_by_id(pid)
            print(f'Product {pid} "{p.l[0].val[:60]}"')
            res = np.search(pid,10,main)
        except:
            print(f"Product {pid} does not exist")
            res=[]
        print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.1f} s") #1.7s / 10000*5 7s / 100K*2
        for p in res:
            print(f'PID {p[0]} at {p[1]*100:.0f}% "{np.get_by_id(p[0]).l[0].val[:60]}"')
        print()

