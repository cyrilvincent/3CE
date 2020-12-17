import cyrilload
import argparse
import numpy as np
import threading
import config

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
    parser = argparse.ArgumentParser(description="Add id1 & id2 to blacklist")
    parser.add_argument("instance", type=str, help="instance")
    parser.add_argument("id1", type=int, help="id 1", default=-1)
    parser.add_argument("id2", type=int, help="id 2", default=-1)
    parser.add_argument("-r","--remove", action="store_true", help="Remove id1 & id2 from blacklist")
    parser.add_argument("-c", "--clear", action="store_true", help="Clear the blacklist")
    parser.add_argument("-l", "--list", action="store_true", help="List the blacklist")
    parser.add_argument("-m", "--match", action="store_true", help="Check if id1 & id2 are in the list")
    args = parser.parse_args()
    fp = NPFalsePositives(config.image_h_file.replace("{instance}",args.instance))
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
        print(f"Add {args.id1} {args.id2} to FP {args.instance}")
        fp.add(args.id1, args.id2)
        fp.db = cyrilload.load(config.image_h_file.replace("{instance}",args.instance))
        fp.save()
    print(fp.set)


