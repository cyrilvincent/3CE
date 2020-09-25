import csv
import pickle
import json
import time
import use
import cyrilload
import config
import logging
from entities import Product, Car
from typing import Dict

class NPParser:
    """
    File parser and indexer
    Not thread safe
    """

    def __init__(self):
        self.db:Dict[int,Product] = {}
        self.path = None

    def parse(self, path:str)->None:
        """
        Parser
        :param path: TXT file to parse
        """
        self.path = path
        self.nbp = 0
        self.nbc = 0
        t = time.perf_counter()
        logging.info(f"Parse {path}")
        try:
            with open(path) as f:
                r = csv.DictReader(f, delimiter="\t")
                for row in r:
                    pid = int(row["product_id"])
                    if pid not in self.db:
                        self.db[pid] = Product(pid)
                        self.nbp += 1
                        main = True
                    s = "" if row["valeur"] == None else row["valeur"].strip()
                    if len(s) > 0:
                        c = Car(int(row["carac_id"]), s, float(row["poids"]), main)
                        self.db[pid].l.append(c)
                    self.nbc += 1
                    main = False
        except Exception as ex:
            logging.FATAL(f"npparse: error when parsing {path} {ex}")
            raise ex
        logging.info(f"Found {self.nbp} products and {self.nbc} characteristics in {time.perf_counter() - t:.1f} s")

    def normalize(self)->None:
        """
        Normalize weigths
        """
        logging.info(f"Normalize {self.nbc} weigths")
        for p in self.db.keys():
            sum = 0
            for c in self.db[p].l:
                sum += c.w
            for c in self.db[p].l:
                c.w = c.w / sum

    def save(self, prefix="", method="pickle")->None:
        """
        Save the db
        :param prefix: see cyrilload
        :param method: see cyrilload
        """
        try:
            t = time.perf_counter()
            name = self.path.split(".")[0]
            cyrilload.save(self.db, name,prefix,method)
            logging.info(f"Saved in {time.perf_counter() - t:.1f} s")
        except Exception as ex:
            logging.error(ex)

    def h(self)->None:
        """
        Use hashing
        """
        logging.info(f"Hashing with USE model")
        model = use.USE()
        t = time.perf_counter()
        i = 0
        for p in self.db.keys():
            if i % max(10,int(self.nbp / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbp} in {time.perf_counter() - t:.1f} s")
            for c in self.db[p].l:
                if " " in c.val and len(c.val) > 4:
                    c.h = model.h(c.val)
            i+=1
        logging.info(f"Hashed in {time.perf_counter() - t:.1f} s")

    def train(self, path:str):
        """
        Main method to parse, normalize, hash and save
        :param path: The file to parse
        """
        try:
            logging.info("Trainting")
            self.parse(path)
            self.normalize()
            self.h()
            self.save(prefix="h")
        except Exception as ex:
            logging.error("Failed to train: "+ex)

if __name__ == '__main__':
    print("NP Products Parser")
    print("==================")
    p = NPParser()
    #p.train(config.data_file)
    p.parse("data/data.txt") #Found 3904 products * 15
    p.normalize()
    #p.save()
    #p.save(method="jsonpickle")
    p.h() #57s / 10000*5 soit 342s pour 100K*3, 12s / 3904*15
    p.save(prefix="h")
    if len(p.db.keys()) < 1000:
        p.save(prefix="h", method="jsonpickle")



