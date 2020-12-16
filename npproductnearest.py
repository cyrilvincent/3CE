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


# noinspection SpellCheckingInspection
class NPNearest:
    """
    High level class, main program
    """

    lock = threading.RLock()

    def __init__(self, path, caching=True, reset=True):
        """
        Found pids nearest
        :param path: the path of the .h.pickle index file
        :param caching: enabling cache
        """
        self.path = path
        self.caching = caching
        self.cache = None
        self.db = None
        self.comp = None
        if reset:
            self.reset()

    @property
    def length(self):
        return len(self.db)

    @property
    def shape(self):
        return len(self.db), len(self.db[list(self.db.keys())[0]].l)

    @property
    def size(self):
        x, y = self.shape
        return x * y

    def reset(self) -> None:
        """
        Reload the h.pickle file
        Reset the cache
        """
        t = time.perf_counter()
        self.db = cyrilload.load(self.path)
        with NPNearest.lock:
            self.cache = {}
        self.comp = npproductcompare.NPComparer()
        # for k in list(self.db.keys())[:1]:
        #     self.search(k)
        logging.info(f"Loaded {len(self.db)} products in {time.perf_counter() - t:.1f} s")

    def __getitem__(self, pid: int) -> Product:
        """
        Get the product by pid
        :param pid: product's pid
        :return: The product
        """
        return self.db[pid]

    def search_gestalt(self, pid: int, pid2s: List[int], main=False) -> List[List[float]]:
        """
        Search nearest by Gestalt model
        :param main:
        :param pid: pid
        :param pid2s: Array of pid to search nearest
        :return: List[List[pid,score]]
        """
        res = []
        for pid2 in pid2s:
            p = self[pid]
            p2 = self[pid2]
            score = self.comp.compare_product_gestalt(p, p2, main)
            res.append([pid2, score])
        return res

    def search(self, pid: int, take=10, main=False, use2=True, fast=True) -> List[List[float]]:
        """
        The main search method
        Perf pb for 100k (7s)
        Put the cache in static, NPParser serialize the cache before h process, then run search on pids in cache
        :param fast:
        :param use2:
        :param pid: the product pid
        :param take: nb max product to return
        :param main: search on the main car only
        :return: List[List[pid,score]]
        """
        if pid in self.cache.keys():
            return self.cache[pid][:take]
        else:
            coef = 0.8 if use2 or fast else 0.5
            take_coef = 4 if use2 or fast else 65536
            p = self[pid]
            res1 = []
            for k in self.db.keys():
                p2 = self[k]
                if p.id != p2.id:
                    score = self.comp.compare_product(p, p2, main, use2)
                    if score > config.product_thresold * coef:
                        res1.append([k, score])
            res1.sort(key=lambda x: x[1], reverse=True)
            res1 = res1[:(take * take_coef)]
            res2 = self.search_gestalt(p.id, [p2[0] for p2 in res1], main)
            res = []
            for x in zip(res1, res2):
                if use2:
                    v = (x[0][1] + x[1][1]) / 2
                else:
                    v = x[1][1]
                res.append([x[0][0], v])
            res.sort(key=lambda x: x[1], reverse=True)
            res = [r for r in res if r[1] > config.product_thresold]
            if self.caching:
                with NPNearest.lock:
                    self.cache[pid] = res
            res = res[:take]
            return res

    def get_ids(self):
        return list(self.db.keys())


class NPNearestPool:

    def __init__(self):
        self.pool = {}
        for instance in config.pool:
            path = config.product_h_file.replace("{instance}", instance)
            self.pool[instance] = NPNearestNN(path, use2=True)

    def get_instance(self, instance: str):
        return self.get_instance_nn(instance).np

    def get_instance_nn(self, instance: str):
        if instance in self.pool:
            return self.pool[instance]
        else:
            msg = f"Instance {instance} does not exist"
            logging.error(msg)
            raise ValueError(msg)

    def __getitem__(self, item):
        return self.get_instance_nn(item)

    @property
    def comp(self):
        return self.pool[config.pool[0]].np.comp

    def reset(self):
        for k in self.pool.keys():
            self.pool[k].reset()


class NPNearestNN:

    def __init__(self, path, use2=True):
        self.np = NPNearest(path)
        self.path = path
        self.use2 = use2

    def reset(self):
        self.np.reset()

    def save(self):
        cyrilload.save(self.np.cache, self.np.path.replace(".h.pickle", ".nn"))

    def load(self):
        self.np.cache = cyrilload.load(self.np.path.replace(".h.pickle", ".nn.pickle"))

    def train(self):
        np = NPNearest(self.path, caching=False)
        t = time.perf_counter()
        i = 0
        for k in np.db.keys():
            if i % max(10, int(len(np.db) / 100)) == 0:
                print(f"NN {i + 1}/{len(np.db)} in {time.perf_counter() - t:.1f} s")
            i += 1
            res = np.search(k, use2=False)
            res = [l for l in res if l[1] > config.product_nn_thresold]
            if len(res) > 0:
                self.np.search(k, use2=self.use2)

    def predict(self):
        res = {}
        for k in self.np.cache.keys():
            for l in self.np.cache[k]:
                if l[1] > config.product_nn_thresold:
                    if l[0] not in res:
                        res[l[0]] = []
                    res[l[0]].append(l)
        return res


if __name__ == '__main__':
    print("NPNearest")
    print("=========")
    print(f"V{__version__}")
    main = False
    product_h_file = "data/data.h.pickle"
    try:
        main = sys.argv[1] == "--mainonly"
        if main:
            print("Main only")
        muse = sys.argv[1] == "--muse"
        if muse:
            product_h_file = product_h_file.replace(".h.", ".linux.h.")
    except:
        pass
    np = NPNearest(product_h_file)

    while True:
        pid = int(input("PID: "))
        t = time.perf_counter()
        try:
            p = np[pid]
            print(f'Product {pid} "{p.l[0].val[:60]}"')
            res = np.search(pid, 10, main, True)
        except:
            print(f"Product {pid} does not exist")
            res = []
        print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.1f} s")  # 1.7s / 10000*5 7s / 100K*2
        for p in res:
            print(f'PID {p[0]} at {p[1]*100:.0f}% "{np[int(p[0])].l[0].val[:60]}"')
        print()

        # use2=True
        # 3904*8 : 0.6s
        # 10000*8 : 1.7s
        # 15000*8 : 2.6s
        # 138461 : 3s
        # 50000*3 : 3.2s
        # 100000*8 : 17s
        # 100000*4 : 5s

        # use2=False
        # 3904*8 : 0.053
        # 1000*8 : 0.014s
        # 10000*8 : 0.14s
        # 15000*8 : 0.21s
        # 100000*8 : 1.4s
