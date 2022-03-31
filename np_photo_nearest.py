import time
import np_image_comparer
import cyrilload
import config
import threading
import logging
import argparse
from entities import NPImage
from typing import List
from np_false_positives import NPFalsePositives
from entities import NPImage
from np_image_parser import NPImageService
from np_image_nearest import NPImageNearest


class NPPhotoNearest:
    """
    High level class, main program
    """

    lock = threading.RLock()

    def __init__(self, path, caching=True, reset=True):
        """
        Found pids nearest
        :param path: the path of the .h.pickle index file
        :param caching: enabling cache
        """
        self.path = path
        self.caching = caching
        self.cache = {}
        self.fp = NPFalsePositives(path)
        self.db = None
        self.comp = None
        if reset:
            self.reset()

    def reset(self) -> None:
        """
        Reload the h.pickle file
        Reset the cache
        """
        t = time.perf_counter()
        try:
            self.db = [{}, {}]
            self.db = cyrilload.load(self.path)
        except FileNotFoundError:
            logging.warning(f"File not found {self.path}")
            cyrilload.save(self.db, self.path.split(".")[0], prefix="h", method="pickle")
        except Exception as ex:
            logging.error(f"Cannot open {self.path}: {ex}")
        with NPImageNearest.lock:
            self.cache = {}
        self.comp = npimcomparer.NPImageComparer()
        print(f"Loaded {len(self.db[0])} images in {time.perf_counter() - t:.1f} s")

    @property
    def length(self):
        return len(self.db[0])

    def get_im_by_iid(self, id: int) -> NPImage:
        return self.db[0][id]

    def get_iids_by_pid(self, id: int) -> List[int]:
        return self.db[1][id]

    def get_iids(self):
        return list(self.db[0].keys())

    def get_pids(self):
        return list(self.db[1].keys())

    def search_by_im(self, id: int, take=10, threshold=config.image_threshold, fast=False) -> List[List[float]]:
        if id in self.cache.keys():
            return self.cache[id][:take]
        else:
            im = self.get_im_by_iid(id)
            res = []
            for k in self.db[0].keys():
                im2 = self.get_im_by_iid(k)
                if im.id != im2.id:
                    if not self.fp.match(im.id, im2.id):
                        score = self.comp.compare(im, im2, fast)
                        if score > threshold:
                            res.append([k, score])
            res.sort(key=lambda x: x[1], reverse=True)
            if self.caching:
                with NPImageNearest.lock:
                    self.cache[id] = res
            res = res[:take]
            return res

    def search_by_product(self, pid: int, take=10, thresold=config.image_threshold, fast=False):
        iids = self.get_iids_by_pid(pid)
        print(f"Found {len(iids)} images: {iids}")
        res = []
        for iid in iids:
            res.append(self.search_by_im(iid, take * 2, thresold, fast))
        dico = {}
        for pres in res:
            for t in pres:
                im = self.get_im_by_iid(t[0])
                for id in im.pids:
                    if id != pid:
                        if id not in dico:
                            dico[id] = t[1]
                        else:
                            dico[id] = max(t[1], dico[id]) + 0.01
                            if dico[id] > 1.0:
                                dico[id] = 1.0
        l = []
        for k in dico.keys():
            l.append([k, dico[k]])
        l.sort(key=lambda x: x[1], reverse=True)
        l = l[:take]
        return l

    def search_families(self, iid: int, take=10, thresold=config.image_threshold, fast=False):
        dico = {}
        res = self.search_by_im(iid, take, thresold, fast)
        for t in res:
            im = self.get_im_by_iid(t[0])
            if im.fid not in dico:
                dico[im.fid] = t[1]
            else:
                dico[im.fid] = min(1.0, max(t[1], dico[im.fid]) + 0.02)
        return dico


class NPImageNearestPool:

    def __init__(self):
        self.pool = {}
        for instance in config.pool:
            path = config.image_h_file.replace("{instance}", instance)
            self.pool[instance] = NPImageNearestNN(path)

    def get_instance(self, instance: str):
        return self.get_instance_nn(instance).np

    def get_instance_nn(self, instance: str):
        if instance in self.pool:
            return self.pool[instance]
        else:
            msg = f"Instance {instance} does not exist"
            logging.error(msg)
            raise ValueError(msg)

    def __getitem__(self, item):
        return self.get_instance_nn(item)

    @property
    def comp(self):
        return self.pool[config.pool[0]].comp

    def reset(self):
        for k in self.pool.keys():
            self.pool[k].reset()


class NPImageNearestNN:

    def __init__(self, path):
        self.np = NPImageNearest(path)
        self.path = path

    def reset(self):
        self.np.reset()

    def save(self):
        cyrilload.save(self.np.cache, self.np.path.replace(".h.pickle", ".nn"))

    def load(self):
        self.np.cache = cyrilload.load(self.np.path.replace(".h.pickle", ".nn.pickle"))

    def train(self, threshold=config.image_nn_threshold, fast=False):
        np = NPImageNearest(self.path)
        t = time.perf_counter()
        i = 0
        for k in np.db[0].keys():
            if i % max(10, int(len(self.np.db[0]) / 100)) == 0:
                print(f"NN {i + 1} / {len(self.np.db[0])} in {time.perf_counter() - t:.1f} s")
            i += 1
            res = np.search_by_im(k, threshold=threshold, fast=fast)
            if len(res) > 0:
                self.np.search_by_im(k, fast=False)

    def predict(self, threshold=config.image_nn_threshold):
        res = {}
        for k in self.np.cache.keys():
            for l in self.np.cache[k]:
                if l[1] > threshold:
                    if l[0] not in res:
                        res[l[0]] = []
                    res[l[0]].append(l)
        return res


# chuv tests/images/07323190073177_BOITE_01.jpg
# chuv tests/images/biogel_photoshop.jpg
if __name__ == '__main__':
    print("NPPhotoNearest")
    print("==============")
    parser = argparse.ArgumentParser(description="Search nearests images or products")
    parser.add_argument("instance", help="Instance")
    parser.add_argument("path", help="path")
    args = parser.parse_args()
    print(f"Search nearests on {args.instance}")
    t = time.perf_counter()
    im = NPImage(0, args.path, None)
    s = NPImageService()
    s.load(args.path)
    im.size = s.size
    im.ah = s.ah()
    im.fv = s.fv()
    im.sean, im.iean = s.ean()
    im.ocr = s.ocr()
    n = NPImageNearest(f"data/{args.instance}-image.h.pickle")
    res = n.search_by_npim(im, threshold=0.5)
    print(res[0])
    id = res[0][0]
    npi = n.get_im_by_iid(id)
    print(im - npi)
    print(npi.ocr)

    # [(x, n.db[0][x]) for x in n.db[0] if n.db[0][x].sean is not None]
    # [(267062, 30382903006008_BOITE_01.JPG), (267065, 30382903007005_BOITE_01.JPG), (266756, 07310791080062_BOITE_01.JPG), (266761, 07323190073115_BOITE_01.JPG), (266762, 07323190073146_BOITE_01.JPG), (266763, 07323190073177_BOITE_01.JPG), (266765, 07323190073238_BOITE_01.JPG), (266766, 07323190073269_BOITE_01.JPG), (266745, 05060097931996_BOITE_01.JPG), (266748, 05060097932023_BOITE_01.JPG), (266739, 05060097931255_BOITE_01.JPG), (266740, 05060097931262_BOITE_01.JPG), (266741, 05060097931279_BOITE_01.JPG), (266742, 05060097931286_BOITE_01.JPG), (266744, 05060097931309_BOITE_01.JPG), (266769, 07323190084128_BOITE_01.JPG), (266771, 07323190084227_BOITE_01.JPG), (267058, 20884523003564_BOITE_01.JPG)]


