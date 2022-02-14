import csv
import time
import cyrilload
import config
import logging
import tensorflow as tf
import absl
import argparse
from entities import Product, Car
from typing import Dict, List


class USE:
    """
    Google Universal Sentence Encoder
    """

    model = None

    def __init__(self):
        """
        Initialize USE model
        """
        if USE.model is None:
            t = time.perf_counter()
            print(f"Load TF USE model: {config.tf_use}")
            USE.model = tf.saved_model.load(config.tf_use)
            print(f"Loaded in {time.perf_counter() - t:.1f} s")
        absl.logging.set_verbosity(absl.logging.ERROR)

    def embed(self, inputs: List[str]) -> List[List[float]]:
        """
        Apply USE model
        :param inputs: list of sentences
        :return: list of h (512 floats) in Tensor types
        """
        return USE.model(inputs)

    def hs(self, inputs: List[str]) -> List[List[float]]:
        """
        Apply USE model
        :param inputs: list of sentences
        :return: list of h (512 floats) in numpy types
        """
        return self.embed(inputs).numpy()

    def h(self, x: str) -> List[float]:
        """
        Apply USE model
        :param x: A sentence
        :return: h : List of 512 floats
        """
        return self.hs([x])[0].tolist()


class NPParser:
    """
    File parser and indexer
    Not thread safe
    """

    def __init__(self):
        self.db: Dict[int, Product] = {}
        self.path = None
        self.use = USE()
        self.nbp = 0
        self.nbc = 0

    def parse(self, path: str) -> None:
        """
        Parser
        :param path: TXT file to parse
        """
        self.nbp = 0
        self.nbc = 0
        self.path = path
        t = time.perf_counter()
        logging.info(f"Parse {path}")
        try:
            with open(path) as f:
                r = csv.DictReader(f, delimiter="\t")
                for row in r:
                    pid = int(row["product_id"])
                    if pid not in self.db:
                        self.db[pid] = Product(pid)
                        if "familly_id" in row:
                            self.db[pid].fid = int(row["familly_id"])
                        self.nbp += 1
                        main = True
                    s = "" if row["valeur"] is None else row["valeur"].strip()
                    if len(s) > 0:
                        c = Car(int(row["carac_id"]), s, float(row["poids"]), main)
                        self.db[pid].l.append(c)
                    self.nbc += 1
                    main = False
        except Exception as ex:
            logging.fatal(f"npparse: error when parsing {path} {ex}")
            raise ex
        logging.info(f"Found {self.nbp} products and {self.nbc} characteristics in {time.perf_counter() - t:.1f} s")

    def normalize(self) -> None:
        """
        Normalize weights
        """
        logging.info(f"Normalize {self.nbc} weights")
        for p in self.db.keys():
            sum = 0
            for c in self.db[p].l:
                sum += c.w
            for c in self.db[p].l:
                c.w = c.w / sum

    def save(self, prefix="", method="pickle") -> None:
        """
        Save the db
        :param prefix: see cyrilload
        :param method: see cyrilload
        """
        try:
            t = time.perf_counter()
            name = self.path.split(".")[0]
            cyrilload.save(self.db, name, prefix, method)
            logging.info(f"Saved in {time.perf_counter() - t:.1f} s")
        except Exception as ex:
            logging.error(ex)

    def save_empty(self, path="data/empty"):
        db: Dict[int, Product] = {}
        cyrilload.save(db, path, method="pickle")
        cache = {}
        cyrilload.save(cache, path, prefix="nn", method="pickle")

    def h(self) -> None:
        """
        Use hashing
        """
        logging.info(f"Hashing with USE model")
        t = time.perf_counter()
        i = 0
        for pid in self.db.keys():
            if i % max(10, int(self.nbp / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbp} in {time.perf_counter() - t:.1f} s")
            self.h_product(self.db[pid])
            i += 1
        logging.info(f"Hashed in {time.perf_counter() - t:.1f} s")

    def h_product(self, p: Product):
        for c in p.l:
            if " " in c.val and len(c.val) > 4:
                c.h = self.use.h(c.val)
            else:
                c.h = None

    def delete(self, pid):
        del self.db[pid]

    def train(self, path: str, use2: bool = True):
        """
        Main method to parse, normalize, hash and save
        :param use2:
        :param path: The file to parse
        """
        try:
            logging.info("Training")
            self.parse(path)
            self.normalize()
            if use2:
                self.h()
            self.save(prefix="h")
        except Exception as ex:
            logging.error(f"Failed to train: {ex}")


if __name__ == '__main__':
    print("NP Products Parser")
    print("==================")
    print(f"V{config.version}")
    parser = argparse.ArgumentParser(description="TXT Parser to h.pickle")
    parser.add_argument("instance", help="Instance")
    parser.add_argument("-n", "--nohash", action="store_true", help="Not use USE hashing")
    parser.add_argument("-nn", "--nn", action="store_true", help="NN hashing")
    parser.add_argument("-e", "--empty", action="store_true", help="Create empty pickles")
    args = parser.parse_args()
    p = NPParser()
    if args.empty:
        p.save_empty()
    p.parse(f"data/{args.instance}.txt")  # Found 3904 products * 15
    p.normalize()
    if not args.nohash:
        p.h()  # 57s / 10000*5 soit 342s pour 100K*3, 12s / 3904*8 Always use USE
    p.save(prefix="h")
    if len(p.db.keys()) < 1000:
        p.save(prefix="h", method="jsonpickle")
    if args.nn:
        import npproductnearest
        use2 = len(p.db) < config.use2_limit
        logging.info(f"Indexer NN with use2: {use2}")
        nn = npproductnearest.NPNearestNN(f"data/{args.instance}.h.pickle", use2=use2)
        nn.train()
        nn.save()
