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

def images_to_html():
    with open(f"outputs/iindex.html", "w") as f:
        f.write("<HTML><BODY><H1>NP Image Nearest Index</H1>\n")
        for iid in np.db[0].keys():
            im = np.get_im_by_iid(iid)
            f.write(f"<a href='ioutput_{iid}.html'>Image {iid} <img src='../images/{im.path}' height='50'/></a><br/>\n")
        f.write("</BODY></HTML>")
    # for pid in np.db[1].keys():
    #     scores = np.search_by_product(pid)
    #     product_scores_to_html(pid, scores)

# def image_scores_to_html(im, scores):
#     print(f"Generate outputs/imoutput_{im.id}.html")
#     with open(f"outputs/imoutput_{im.id}.html","w") as f:
#         f.write("<HTML><BODY><H1>NP Image Nearest</H1>\n")
#         f.write(f"<p><a href='iindex.html'>Index</a>")
#         f.write(f"<p>Search Nearests images of {im.id} {im.name} <a href='../images/{im.path}'><img src='../images/{im.path}' height=100 /></a>\n")
#         f.write(f"<p>Found {len(scores)} image(s)\n")
#         for t in res:
#             im2 = np.get_im_by_iid(t[0])
#             f.write(f"<p>Image: {im2.id} <a href='imoutput_{im2.id}.html'>{im2.name}</a> at {t[1]*100:.0f}%  <a href='../images/{im2.path}'><img src='../images/{im2.path}' height=100 /></a>\n")
#             f.write(f"{npimcomparer.NPImageComparer().comp(im, im2)}")
#         f.write("</BODY></HTML>")
#     with open(f"outputs/iindex.html", "w") as f:
#         f.write("<HTML><BODY><H1>NP Image Nearest Image Index</H1>\n")
#         for k in np.db[0].keys():
#             im = np.db[0][k]
#             f.write(f"<a href='output_{i}.html'>imoutput_{i}.html<img src='../images/{im.path}' height='50'/></a><br/>")
#         f.write("</BODY></HTML>")

def products_to_html():
    with open(f"outputs/pindex.html", "w") as f:
        f.write("<HTML><BODY><H1>NP Product Nearest by image Index</H1>\n")
        for pid in np.db[1].keys():
            f.write(f"<a href='poutput_{pid}.html'>Product {pid}</a> ")
            for iid in np.db[1][pid]:
                im = np.db[0]
                f.write(f"<a href='ioutput_{iid}.html'><img src='../images/{im.path}' height='50'/></a> ")
            f.write("<br/>\n")
        f.write("</BODY></HTML>")
    # for pid in np.db[1].keys():
    #     scores = np.search_by_product(pid)
    #     product_scores_to_html(pid, scores)



def product_scores_to_html(pid, scores):
    print(f"Generate outputs/poutput_{pid}.html")
    # with open(f"outputs/poutput_{im.id}.html","w") as f:
    #     f.write("<HTML><BODY><H1>NP Product by image Nearest</H1>\n")
    #     f.write(f"<p><a href='pindex.html'>Index</a>")
    #     f.write(f"<p>Search Nearests images of {im.id} {im.name} <a href='../images/{im.path}'><img src='../images/{im.path}' height=100 /></a>\n")
    #     f.write(f"<p>Found {len(scores)} image(s)\n")
    #     for t in res:
    #         im2 = np.get_im_by_iid(t[0])
    #         f.write(f"<p>Image: {im2.id} <a href='output_{im2.id}.html'>{im2.name}</a> at {t[1]*100:.0f}%  <a href='../images/{im2.path}'><img src='../images/{im2.path}' height=100 /></a>\n")
    #         f.write(f"{npimcomparer.NPImageComparer().comp(im, im2)}")
    #     f.write("</BODY></HTML>")



if __name__ == '__main__':
    print("NPImageNearest")
    print("==============")
    np = NPImageNearest("data/imagemock.h.pickle")
    byproduct = len(sys.argv) > 1 and sys.argv[1] == "--product"

    res = np.search_by_product(6, 10, 0.75)
    print(res)

    #Recherche par image
    if not byproduct:
        while True:
            id = int(input("ImageID: "))
            t = time.perf_counter()
            try:
                im = np.get_im_by_iid(id)
                print(f'Image {id} {im.path}')
                res = np.search_by_im(id, 10, 0.75)
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
        while True:
            id = int(input("ProductID: "))
            t = time.perf_counter()
            try:
                res = np.search_by_product(id, 10, 0.75)
            except Exception as ex:
                print(f"Product {id} does not exist", ex)
                res=[]
            print(res)
            print(f"Found {len(res)} product(s) in {time.perf_counter() - t:.3f} s")  # 0.003s/63 0.2s/4000 0.5s/10000 5s/100000
            print()


