import time
import npimcompare
import cyrilload
import config
from entities import Image
from typing import List

class NPImageNearest:
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
        self.comp = npimcompare.NPImageComparer()
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def get_by_id(self, id:int)->Image:
        return self.db[id]


    def search(self, id:int, take=10, activation = True)->List[List[float]]:
        if id in self.cache.keys():
            return self.cache[id][:take]
        else:
            im = self.get_by_id(id)
            res = []
            for k in self.db.keys():
                im2 = self.get_by_id(k)
                if im.id != im2.id:
                    score = self.comp.compare(im, im2, activation)
                    if score > 0.5:
                        res.append([k, score])
            res.sort(key = lambda x : x[1], reverse = True)
            if self.caching:
                self.cache[id] = res
            res = res[:take]
            return res


if __name__ == '__main__':
    print("NPImageNearest")
    print("==============")
    np = NPImageNearest("data/imagemock.h.pickle")
    while True:
        id = int(input("ImageID: "))
        t = time.perf_counter()
        try:
            im = np.get_by_id(id)
            print(f'Image {id} {im.path}')
            res = np.search(id,10, True)
        except:
            print(f"image {id} does not exist")
            res=[]
        print(f"Found {len(res)} image(s) in {time.perf_counter() - t:.3f} s") #0.003s/63 0.2s/4000 0.5s/10000 5s/100000
        for im2 in res:
            print(f'ID {im2[0]} at {im2[1]*100:.0f}% "{np.get_by_id(im2[0]).name}" {np.comp.comp(im, np.get_by_id(im2[0]))} ')
        print()

