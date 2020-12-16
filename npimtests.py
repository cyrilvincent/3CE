import unittest
import numpy as np
import config
import cyrilload
from entities import NPImage
from npimparser import NPImageService, NPImageParser
from npimcomparer import NPImageComparer
from npimnearest import NPImageNearest, NPImageNearestPool


class ImageTests(unittest.TestCase):

    def test_config(self):
        print(f"V{config.version}")

    def test_npimage(self):
        np = NPImage(1, "tests/images/ski.jpg",0)
        self.assertEqual("JPG", np.ext)
        self.assertEqual("SKI.JPG",np.name)

    def test_npimageservice(self):
        np = NPImageService("tests/images/ski.jpg")
        self.assertEqual(484720,np.size)
        self.assertIsNotNone(np.pil)
        self.assertEqual("00000000fcffffff", str(np.ah()))
        self.assertEqual("f0e8f0d0d8cce6f0", str(np.dh()))
        self.assertEqual("00001000feffffff", str(np.wh()))
        self.assertEqual(1792, len(np.fv()))

    def test_npimageparser(self):
        np = NPImageParser()
        np.parse("tests/data-image.txt")
        self.assertEqual(6, len(np.dbi))
        np.save("parse","jsonpickle")
        np.h("tests/images")
        np.save("h")

    def test_npimcomparer_comp(self):
        db = cyrilload.load("tests/data-image.h.pickle")
        i1 = db[0][106]
        i2 = db[0][109]
        np = NPImageComparer()
        score = np.diff(i1, i2)
        self.assertEqual(1, score["dah"])
        self.assertEqual(1, score["dfv"])

    def test_npimcomparer(self):
        db = cyrilload.load("tests/data-image.h.pickle")
        i1 = db[0][106]
        i2 = db[0][109]
        np = NPImageComparer()
        score = np.compare(i1, i2)
        self.assertEqual(1, score)

    def test_npimnearest_byimage(self):
        np = NPImageNearest("tests/data-image.h.pickle")
        score = np.search_by_im(106)
        self.assertEqual(109, score[0][0])
        self.assertEqual(107, score[1][0])
        self.assertAlmostEqual(0.84, score[1][1], delta=1e-2)
        score = np.search_by_im(110)
        self.assertEqual(111, score[0][0])
        self.assertAlmostEqual(0.81, score[0][1], delta=1e-2)

    def test_npimnearest_byproduct(self):
        np = NPImageNearest("tests/data-image.h.pickle")
        score = np.search_by_product(53)
        self.assertEqual(54, score[0][0])
        self.assertAlmostEqual(1.0, score[0][1], delta=1e-2)

    def test_npimnearest_falsepositive(self):
        np = NPImageNearest("tests/data-image.h.pickle")
        np.fp.add(106, 109)
        score = np.search_by_im(106)
        self.assertEqual(107, score[0][0])
        np.fp.reset()
        np.reset()
        score = np.search_by_im(106)
        self.assertEqual(109, score[0][0])

    def test_pool(self):
        config.image_h_file = "tests/{instance}-image.h.pickle"
        pool = NPImageNearestPool()
        np = pool.get_instance("data")
        score = np.search_by_product(53)
        self.assertEqual(54, score[0][0])

    def test_nn(self):
        config.image_h_file = "tests/{instance}-image.h.pickle"
        pool = NPImageNearestPool()
        np = pool.get_instance_nn("data")
        np.train()
        self.assertEqual(2, len(np.np.cache))
        res = np.predict()
        self.assertEqual(2, len(res))

    def test_family(self):
        config.image_h_file = "tests/{instance}-image.h.pickle"
        pool = NPImageNearestPool()
        np = pool.get_instance("data")
        score = np.search_families(107)
        self.assertEqual(1, list(score.keys())[0])


if __name__ == '__main__':
    unittest.main()
