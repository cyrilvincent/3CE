import time
import npimcomparer
import cyrilload
import config
import threading
import sys
from entities import NPImage
from typing import List
from npfalsepositives import NPFalsePositives

class NPImageNearest:
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
        self.fp = NPFalsePositives(path)
        if reset:
            self.reset()

    def reset(self)->None:
        """
        Reload the h.pickle file
        Reset the cache
        """
        t = time.perf_counter()
        self.db = cyrilload.load(self.path)
        with NPImageNearest.lock:
            NPImageNearest.cache = {}
        self.comp = npimcomparer.NPImageComparer()
        print(f"Loaded {len(self.db[0])} images in {time.perf_counter() - t:.1f} s")

    def get_im_by_iid(self, id:int)->NPImage:
        return self.db[0][id]

    def get_iids_by_pid(self, id:int)->List[int]:
        return self.db[1][id]

    def get_iids(self):
        return list(self.db[0].keys())

    def get_pids(self):
        return list(self.db[1].keys())

    def search_by_im(self, id:int, take=10, thresold = 0.75)->List[List[float]]:
        if id in NPImageNearest.cache.keys():
            return NPImageNearest.cache[id][:take]
        else:
            im = self.get_im_by_iid(id)
            res = []
            for k in self.db[0].keys():
                im2 = self.get_im_by_iid(k)
                if im.id != im2.id:
                    if not self.fp.match(im.id, im2.id):
                        score = self.comp.compare(im, im2)
                        if score > thresold:
                            res.append([k, score])
            res.sort(key = lambda x : x[1], reverse = True)
            if self.caching:
                with NPImageNearest.lock:
                    NPImageNearest.cache[id] = res
            res = res[:take]
            return res

    def search_by_product(self, pid:int, take=10, thresold = 0.75):
        iids = self.get_iids_by_pid(pid)
        print(f"Found {len(iids)} images: {iids}")
        res = []
        for iid in iids:
            res.append(self.search_by_im(iid, take * 2, thresold))
        dico = {}
        for pres in res:
            for t in pres:
                im = self.get_im_by_iid(t[0])
                for id in im.pids:
                    if id != pid:
                        if id not in dico:
                            dico[id] = t[1]
                        else:
                            dico[id]=max(t[1], dico[id]) + 0.01
                            if dico[id] > 1.0:
                                dico[id] = 1.0
        l = []
        for k in dico.keys():
            l.append([k, dico[k]])
        l.sort(key = lambda x : x[1], reverse=True)
        l = l[:take]
        return l

if __name__ == '__main__':
    print("NPImageNearest")
    print("==============")
    np = NPImageNearest("data/imagemock.h.pickle")
    byproduct = len(sys.argv) > 1 and sys.argv[1] == "--product"

    res = np.search_by_product(6, 10, 0.75)
    print(res)

    #Recherche par image
    if not byproduct:
        print(np.get_iids())
        while True:
            id = int(input("ImageID: "))
            t = time.perf_counter()
            try:
                im = np.get_im_by_iid(id)
                print(f'Image {id} {im.path}')
                res = np.search_by_im(id)
                image_scores_to_html(im, res)
            except Exception as ex:
                print(f"Image {id} does not exist", ex)
                res=[]
            print(res)
            print(f"Found {len(res)} images(s) in {time.perf_counter() - t:.3f} s")  # 0.003s/63 0.2s/4000 0.5s/10000 5s/100000
            for im2 in res:
                print(f'ID {im2[0]} at {im2[1] * 100:.0f}% "{np.get_im_by_iid(im2[0]).name}" {np.comp.comp(im, np.get_im_by_iid(im2[0]))} ')
            print()

    else:
        print(np.get_pids())
        while True:
            id = int(input("ProductID: "))
            t = time.perf_counter()
            try:
                res = np.search_by_product(id)
            except Exception as ex:
                print(f"Product {id} does not exist", ex)
                res=[]
            print(res)
            print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.3f} s")  # 0.003s/63 0.2s/4000 0.5s/10000 5s/100000
            print()


