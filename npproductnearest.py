import time
import npproductcompare
import cyrilload
import config
import sys
import threading
import logging
from entities import Product
from typing import List

__version__ = config.version

class NPNearest:
    """
    High level class, main program
    """

    cache = {}
    lock = threading.RLock()

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
        with NPNearest.lock:
            NPNearest.cache = {}
        self.comp = npproductcompare.NPComparer()
        for k in list(self.db.keys())[:1]:
            self.search(k)
        logging.info(f"Loaded {len(self.db)} products in {time.perf_counter() - t:.1f} s")

    def get_by_id(self, pid:int)->Product:
        """
        Get the product by pid
        :param pid: product's pid
        :return: The product
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
        if pid in NPNearest.cache.keys():
            return NPNearest.cache[pid][:take]
        else:
            p = self.get_by_id(pid)
            res1 = []
            for k in self.db.keys():
                p2 = self.get_by_id(k)
                if p.id != p2.id:
                    score = self.comp.compare(p, p2, main)
                    if score > config.product_thresold * 0.8:
                        res1.append([k, score])
            res1.sort(key = lambda x : x[1], reverse = True)
            res1 = res1[:(take * config.take_ratio)]
            res2 = self.searchl(p.id, [p2[0] for p2 in res1], main)
            res = []
            for x in zip(res1, res2):
                v = (x[0][1] + x[1][1]) / 2
                res.append([x[0][0], v])
            res.sort(key=lambda x: x[1], reverse=True)
            res = [r for r in res if r[1] > config.product_thresold]
            if self.caching:
                with NPNearest.lock:
                    NPNearest.cache[pid] = res
            res = res[:take]
            return res

def scores_to_html(p, scores):
    print(f"Generate outputs/output_{p.id}.html")
    # with open(f"outputs/index.html", "w") as f:
    #     f.write('<HTML><HEAD></HEAD><BODY><H1>NPNearest Products Index</H1>\n')
    #     for k in np.db.keys():
    #         try:
    #             p = np.get_by_id(k)
    #             f.write(f"<a href='output_{k}.html'>output_{k}.html</a>: {np.db[k].l[0].val}<br/>")
    #         except:
    #             pass
    #     f.write("</BODY></HTML>")
    with open(f"outputs/output_{p.id}.html","w") as f:
        f.write('<HTML><HEAD></HEAD><BODY><H1>NPNearest</H1>\n')
        f.write(f"<p><a href='index.html'>Index</a>")
        f.write(f"<p>Search Nearests products of {p.id}\n")
        f.write(f"<p>Found {len(scores)} product(s)\n")
        for t in res:
            p2 = np.get_by_id(t[0])
            f.write(f"<p>Product: <a href='output_{p2.id}.html'>{p2.id}</a> at {t[1]*100:.0f}% \n")
            f.write((f"(USE: {np.comp.compare(p, p2)*100:.0f}%, Gestalt: {np.comp.comparel(p, p2)*100:.0f}%)"))
            f.write(f"<table border='1'><tr><td>cid</td><td>{p.id} values</td><td>{p2.id} values</td><td>Score USE</td><td>Weights USE</td><td>Scores Gestalt</td><td>Weights Gestalt</td></tr>\n")
            res2 = np.comp.compp(p, p2)
            total2 = sum([w[1] for w in res2])
            res3 = np.comp.comppl(p, p2)
            total3 = sum([w[1] for w in res3])
            i = 0
            for t in res2:
                c = p.l[i]
                c2 = p2.get_car_by_id(c.id)
                f.write(f"<tr><td>{c.id}</td><td>{'' if c is None else c.val}</td><td>{'' if c2 is None else c2.val}</td>")
                f.write(f"<td>{t[0]*100:.0f}%</td><td>{t[1] / total2:.2f}</td><td>{res3[i][0]*100:.0f}%</td><td>{res3[i][1] / total3:.2f}</td></tr>\n")
                i+=1
            f.write(f"</table>")
        f.write("</BODY></HTML>")


if __name__ == '__main__':
    print("NPNearest")
    print("=========")
    print(f"V{__version__}")
    main = False
    try:
        main = sys.argv[1] == "--mainonly"
        if main:
            print("Main only")
        muse = sys.argv[1] == "--muse"
        if muse:
            config.product_h_file = config.product_h_file.replace(".h.", ".linux.h.")
    except:
        pass
    np = NPNearest(config.product_h_file)
    # for k in np.db.keys():
    #     p = np.get_by_id(k)
    #     res = np.search(k, 10)
    #     scores_to_html(p, res)
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

