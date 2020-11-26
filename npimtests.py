import unittest
import numpy as np
import config
import cyrilload
from entities import NPImage
from npimparser import NPImageService, NPImageParser
from npimcomparer import NPImageComparer
from npimnearest import NPImageNearest


class ImageTests(unittest.TestCase):

    def test_config(self):
        print(f"V{config.version}")

    def test_npimage(self):
        np = NPImage(1, "tests/images/ski.jpg")
        self.assertEqual("JPG", np.ext)
        self.assertEqual("SKI.JPG",np.name)

    def test_npimageservice(self):
        np = NPImageService("tests/images/ski.jpg")
        self.assertEqual(484720,np.size)
        self.assertIsNotNone(np.pil)
        self.assertEqual("00000000fcffffff", str(np.ah()))
        self.assertEqual("00000000000000000000010000000000fd80fffcfdffff3fffffffffffffffff", str(np.a2h()))
        self.assertEqual("f0e8f0d0d8cce6f0", str(np.dh()))
        self.assertEqual("c13b0cf35b2cb2c9", str(np.ph()))
        self.assertEqual("00001000feffffff", str(np.wh()))
        self.assertEqual("00000000000000000003003e3ffe03fffffffffffffffffff", str(np.wdh()))
        self.assertEqual(1792, len(np.fv()))

    def test_npimageparser(self):
        np = NPImageParser()
        np.parse("tests/image.txt")
        self.assertEqual(6, len(np.dbi))
        np.save("parse","jsonpickle")
        np.h("tests/images")
        np.save("h")

    def test_npimcomparer_comp(self):
        db = cyrilload.load("tests/image.h.pickle")
        i1 = db[0][106]
        i2 = db[0][109]
        np = NPImageComparer()
        score = np.diff(i1, i2)
        self.assertEqual(1, score["dah"])
        self.assertEqual(1, score["dfv"])

    def test_npimcomparer(self):
        db = cyrilload.load("tests/image.h.pickle")
        i1 = db[0][106]
        i2 = db[0][109]
        np = NPImageComparer()
        score = np.compare(i1, i2)
        self.assertEqual(1, score)

    def test_npimnearest_byimage(self):
        np = NPImageNearest("tests/image.h.pickle")
        score = np.search_by_im(106)
        self.assertEqual(109, score[0][0])
        self.assertEqual(107, score[1][0])
        self.assertAlmostEqual(0.87, score[1][1], delta = 1e-2)
        score = np.search_by_im(110)
        self.assertEqual(111, score[0][0])
        self.assertAlmostEqual(0.77, score[0][1], delta=1e-2)

    def test_npimnearest_byproduct(self):
        np = NPImageNearest("tests/image.h.pickle")
        score = np.search_by_product(53)
        self.assertEqual(54, score[0][0])
        self.assertAlmostEqual(1.0, score[0][1], delta = 1e-2)

    def test_npimnearest_falsepositive(self):
        np = NPImageNearest("tests/image.h.pickle")
        np.fp.add(106,109)
        score = np.search_by_im(106)
        self.assertEqual(107, score[0][0])
        np.fp.reset()
        np.reset()
        score = np.search_by_im(106)
        self.assertEqual(109, score[0][0])

if __name__ == '__main__':
    unittest.main()








