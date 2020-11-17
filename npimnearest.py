import time
import npimcomparer
import cyrilload
import config
import threading
from entities import Image
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
        print(f"Loaded in {time.perf_counter() - t:.1f} s")

    def get_im_by_id(self, id:int)->Image:
        return self.db[0][id]

    def get_product_by_id(self, id:int)->List[int]:
        return self.db[1][id]

    def search_by_im(self, id:int, take=10, thresold = 0.75)->List[List[float]]:
        if id in NPImageNearest.cache.keys():
            return NPImageNearest.cache[id][:take]
        else:
            im = self.get_im_by_id(id)
            res = []
            for k in self.db[0].keys():
                im2 = self.get_im_by_id(k)
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
        p = self.get_product_by_id(pid)
        res = []
        for iid in p:
            res.append(self.search_by_im(iid, take * 2, thresold))
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

def image_scores_to_html(im, scores):
    print(f"Generate outputs/output_{im.id}.html")
    with open(f"outputs/output_{im.id}.html","w") as f:
        f.write("<HTML><BODY><H1>NPShazimNearest</H1>\n")
        f.write(f"<p><a href='index.html'>Index</a>")
        f.write(f"<p>Search Nearests images of {im.id} {im.name} <a href='../images/{im.path}'><img src='../images/{im.path}' height=100 /></a>\n")
        f.write(f"<p>Found {len(scores)} image(s)\n")
        for t in res:
            im2 = np.get_im_by_id(t[0])
            f.write(f"<p>Image: {im2.id} <a href='output_{im2.id}.html'>{im2.name}</a> at {t[1]*100:.0f}%  <a href='../images/{im2.path}'><img src='../images/{im2.path}' height=100 /></a>\n")
            f.write(f"{npimcomparer.NPImageComparer().comp(im, im2)}")
        f.write("</BODY></HTML>")
    with open(f"outputs/index.html", "w") as f:
        f.write("<HTML><BODY><H1>NPShazimNearest Image Index</H1>\n")
        for i in range(5000):
            try:
                im = np.get_im_by_id(i)
                f.write(f"<a href='output_{i}.html'>output_{i}.html<img src='../images/{im.path}' height='50'/></a><br/>")
            except:
                pass
        f.write("</BODY></HTML>")


if __name__ == '__main__':
    print("NPImageNearest")
    print("==============")
    np = NPImageNearest("data/imagemock.h.pickle")
    for k in np.db[0]:
        im = np.get_im_by_id(k)
        res = np.search_by_im(k,10,0.75)
        image_scores_to_html(im, res)
    while True:
        id = int(input("ImageID: "))
        t = time.perf_counter()
        try:
            im = np.get_im_by_id(id)
            print(f'Image {id} {im.path}')
            res = np.search_by_im(id, 10, 0.5)
        except:
            print(f"image {id} does not exist")
            res=[]
        print(f"Found {len(res)} image(s) in {time.perf_counter() - t:.3f} s") #0.003s/63 0.2s/4000 0.5s/10000 5s/100000
        for im2 in res:
            print(f'ID {im2[0]} at {im2[1]*100:.0f}% "{np.get_im_by_id(im2[0]).name}" {np.comp.comp(im, np.get_im_by_id(im2[0]))} ')
        image_scores_to_html(im, res)
        print()

