import time
import cyrilload
import config
from npproductnearest import NPNearest

__version__ = config.version

print("NPPredict")
print("=========")
print(f"V{__version__}")
np = NPNearest("../../data/data.h.pickle")
while True:
    s = input("Enter a sentence: ")
    best = (None, 0)
    for k in np.db.keys():
        p = np.get_by_id(k)
        score = np.comp.compvl(s, p.l[0].val)
        if score > best[1]:
            best = (p, score)
    val = [c.val for c in best[0].l if c.id == 995]
    print(f"Predict carac 955 {val} at {best[1]*100:.0f}%")


