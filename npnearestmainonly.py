import time
import npcompare
import cyrilload
import config
from entities import Product
from typing import List
from npnearest import NPNearest

if __name__ == '__main__':
    print("NPNearestMainOnly")
    print("=================")
    np = NPNearest(config.h_file)
    while True:
        pid = int(input("PID: "))
        t = time.perf_counter()
        try:
            p = np.get_by_id(pid)
            print(f'Product {pid} "{p.l[0].val[:60]}"')
            res = np.search(pid,10,True)
        except KeyError:
            print(f"Product {pid} does not exist")
            res=[]
        print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.1f} s") #1.7s / 10000*5 7s / 100K*2
        for p in res:
            print(f'PID {p[0]} at {p[1]*100:.0f}% "{np.get_by_id(p[0]).l[0].val[:60]}"')
        print()

