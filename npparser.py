import csv
import pickle
import json
import time
import use

class NPParser:

    def __init__(self):
        self.db = {}
        self.path = None

    def parse(self, path):
        self.path = path
        self.nbp = 0
        self.nbc = 0
        t = time.perf_counter()
        print(f"Parse {path}")
        with open(path) as f:
            r = csv.DictReader(f)
            for row in r:
                pid = row["pid"]
                if pid not in self.db:
                    self.db[pid] = {"l":{}}
                    self.nbp += 1
                    main = True
                s = row["val"].strip()
                if len(s) > 0:
                    c = {
                            "val":s,
                            "main":main,
                            "w":float(row["weight"]),
                            "h":None
                        }
                    main = False
                    self.db[pid]["l"][row["cid"]] = c
                    self.nbc += 1
        print(f"Found {self.nbp} products and {self.nbc} characteristics in {time.perf_counter() - t:.1f} s")

    def normalize(self):
        print(f"Normalize {self.nbc} weigths")
        for p in self.db.keys():
            sum = 0
            cs = self.db[p]["l"]
            for cid in cs.keys():
                sum += cs[cid]["w"]
            for cid in cs.keys():
                cs[cid]["w"] = cs[cid]["w"] / sum

    def save(self, prefix="", method="pickle"):
        t = time.perf_counter()
        name = self.path.split(".")[0]
        if prefix != "":
            name += f".{prefix}"
        if method == "pickle":
            name += ".pickle"
        elif method == "json":
            name += ".json"
        elif method == "pretty":
            name += ".pretty.json"
        else:
            raise ValueError(f"Unknown method {method}")
        print(f"Save {name}")
        if method == "pickle":
            with open(name,"wb") as f:
                pickle.dump(self.db, f)
        else:
            with open(name,"w") as f:
                if method == "pretty" and self.nbp > 1000:
                    f.write("Too big!")
                else:
                    json.dump(self.db, f,indent = 4 if method == "pretty" else None)
        print(f"Saved in {time.perf_counter() - t:.1f} s")

    def load(self, path):
        t = time.perf_counter()
        self.path = path
        ext = path.split(".")[-1]
        print(f"Load {path}")
        if ext == "pickle":
            with open(path,"rb") as f:
                self.db = pickle.load(f)
        elif ext == "json":
            with open(path) as f:
                self.db = json.load(f)
        else:
            raise ValueError(f"Unknow extension {ext}")
        self.nbp = len(self.db.keys())
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def h(self):
        print(f"Hashing with USE model")
        model = use.USE()
        t = time.perf_counter()
        i = 0
        for p in self.db.keys():
            if i % max(10,int(self.nbp / 100)) == 0:
                print(f"Hash {i + 1}/{self.nbp} in {time.perf_counter() - t:.1f} s")
            cs = self.db[p]["l"]
            vals = []
            for cid in cs.keys():
                vals.append(cs[cid]["val"])
                hs = model.hs(vals)
            j = 0
            for cid in cs.keys():
                if " " in cs[cid]["val"]:
                    cs[cid]["h"] = hs[j].tolist()
                j+=1
            i+=1
        print(f"Hashed in {time.perf_counter() - t:.1f} s")

if __name__ == '__main__':
    print("NP Products Parser")
    print("==================")
    p = NPParser()
    p.parse("data/mock100.csv")
    #p.normalize()
    p.save()
    p.save(method="json")
    p.save(method="pretty")
    p.h() #275s / 10000
    p.save(prefix="h")
    p.save(prefix="h", method="json")
    p.save(prefix="h", method="pretty")



