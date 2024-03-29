import time
import np_product_compare
import cyrilload
import config
import threading
import logging
import argparse
from entities import Product
from typing import List


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
        try:
            self.db = {}
            self.db = cyrilload.load(self.path)
        except FileNotFoundError:
            logging.warning(f"File not found {self.path}")
            cyrilload.save(self.db, self.path.split(".")[0], prefix="h", method="pickle")
        except Exception as ex:
            logging.error(f"Cannot open {self.path}: {ex}")
        with NPNearest.lock:
            self.cache = {}
        self.comp = np_product_compare.NPComparer()
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

    def search(self, pid: int, threshold=config.product_threshold, take=10, main=False, use2=True, fast=True) -> List[List[float]]:
        """
        The main search method
        Perf pb for 100k (7s)
        Put the cache in static, NPParser serialize the cache before h process, then run search on pids in cache
        :param threshold:
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
            coef = 0.8 if use2 else 0.5
            take_coef = 4 if use2 or fast else 65536
            p = self[pid]
            res1 = []
            for k in self.db.keys():
                p2 = self[k]
                if p.id != p2.id:
                    score = self.comp.compare_product(p, p2, main, use2)
                    if score > threshold * coef:
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
            res = [r for r in res if r[1] > threshold]
            if self.caching:
                with NPNearest.lock:
                    self.cache[pid] = res
            res = res[:take]
            return res

    def get_ids(self):
        return list(self.db.keys())


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

    def train(self, threshold=config.product_nn_threshold):
        np = NPNearest(self.path, caching=False)
        t = time.perf_counter()
        i = 0
        for k in np.db.keys():
            if i % max(10, int(len(np.db) / 100)) == 0:
                print(f"NN {i + 1} / {len(np.db)} in {time.perf_counter() - t:.1f} s")
            i += 1
            res = np.search(k, threshold=threshold, use2=False)
            if len(res) > 0:
                self.np.search(k, use2=self.use2)

    def predict(self, threshold=config.product_nn_threshold):
        res = {}
        for k in self.np.cache.keys():
            for l in self.np.cache[k]:
                if l[1] > threshold:
                    if k not in res:
                        res[k] = []
                    res[k].append(l)
        return res

    def __repr__(self):
        return f"NN: {self.path}"


if __name__ == '__main__':
    print("NPNearest")
    print("=========")
    print(f"V{config.version}")
    parser = argparse.ArgumentParser(description="Product nearests")
    parser.add_argument("instance", help="Instance")
    parser.add_argument("-m", "--main", action="store_true", help="Compare main charac only")
    parser.add_argument("-u", "--muse", action="store_true", help="Use MUSE insted of USE")
    args = parser.parse_args()
    product_h_file = config.product_h_file.replace("{instance}", args.instance)
    np = NPNearest(product_h_file)

    while True:
        pid = int(input("PID: "))
        t = time.perf_counter()
        try:
            p = np[pid]
            print(f'Product {pid} "{p.l[0].val[:60]}"')
            res = np.search(pid, config.product_threshold, 10, args.main, True)
        except:
            print(f"Product {pid} does not exist")
            res = []
        print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.1f} s")  # 1.7s / 10000*5 7s / 100K*2
        for p in res:
            print(f'PID {p[0]} @ {p[1]*100:.0f}% "{np[int(p[0])].l[0].val[:60]}"')
        if len(res) > 0:
            print("Found 1 familly")
            print(f"FID {np[res[0][0]].fid} @ {res[0][1]*100:.0f}%")

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
