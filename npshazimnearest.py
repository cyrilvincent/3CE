import time
import npshazim
import cyrilload
import config
from entities import Image
from typing import List
from npfalsepositives import ImFalsePositives

class ShazImageNearest:
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
        self.fp = ImFalsePositives(path)

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
        self.comp = npshazim.ShazImageComparer()
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def get_im_by_id(self, id:int)->Image:
        return self.db[0][id]

    def get_product_by_id(self, id:int)->List[int]:
        return self.db[1][id]

    def search_by_im(self, id:int, take=10)->List[List[float]]:
        if id in self.cache.keys():
            return self.cache[id][:take]
        else:
            im = self.get_im_by_id(id)
            res = []
            for k in self.db[0].keys():
                im2 = self.get_im_by_id(k)
                if im.id != im2.id:
                    if not self.fp.match(im.id, im2.id):
                        score = self.comp.compare(im, im2)
                        if score > 0.5:
                            res.append([k, score])
            res.sort(key = lambda x : x[1], reverse = True)
            if self.caching:
                self.cache[id] = res
            res = res[:take]
            return res

    def search_by_product(self, pid:int, take=10):
        p = self.get_product_by_id(pid)
        res = []
        for iid in p:
            res.append(self.search_by_im(iid, take * 2))
        dico = {}
        for pres in res:
            for t in pres:
                im = self.get_im_by_id(t[0])
                for id in im.pids:
                    if id != pid:
                        if id not in dico:
                            dico[id] = t[1]
                        dico[id]=max(t[1], dico[id]) + 0.01
                        if dico[id] > 1.0:
                            dico[id] = 1.0
        print(dico)
        l = []
        for k in dico.keys():
            l.append([k, dico[k]])
        l.sort(lambda x : x[1], reverse=True)
        l = l[:take]
        return l

    def image_scores_to_html(self, im, scores):
        with open(f"outputs/output_{im.id}.html","w") as f:
            f.write("<HTML><BODY><H1>NPShazimNearest</H1>\n")
            f.write(f"<p>Search Nearests images of {im.id} {im.name} <img src='../images/{im.path}' height=100 />\n")
            f.write(f"<p>Found {len(scores)} image(s)\n")
            for t in res:
                im2 = np.get_im_by_id(t[0])
                f.write(f"<p>Image: {im2.id} {im2.name} at {t[1]*100:.0f}%  <img src='../images/{im2.path}' height=100 />\n")
            f.write("</BODY></HTML>")

if __name__ == '__main__':
    print("NPImageNearest")
    print("==============")
    np = ShazImageNearest("data/imagemock.h.pickle")
    while True:
        id = int(input("ImageID: "))
        t = time.perf_counter()
        try:
            im = np.get_im_by_id(id)
            print(f'Image {id} {im.path}')
            res = np.search_by_im(id, 10)
        except:
            print(f"image {id} does not exist")
            res=[]
        print(f"Found {len(res)} image(s) in {time.perf_counter() - t:.3f} s") #0.003s/63 0.2s/4000 0.5s/10000 5s/100000
        for im2 in res:
            print(f'ID {im2[0]} at {im2[1]*100:.0f}% "{np.get_im_by_id(im2[0]).name}" {np.comp.comp(im, np.get_im_by_id(im2[0]))} ')
        np.image_scores_to_html(im, res)
        print()

