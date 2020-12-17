import unittest
import config
import cyrilload
from entities import NPImage
from npimparser import NPImageService, NPImageParser
from npimcomparer import NPImageComparer
from npimnearest import NPImageNearest, NPImageNearestPool
from npimagebarcode import NpImageBarcode, NpImageOcr


class ImageTests(unittest.TestCase):

    pickle = "tests/data-image.h.pickle"

    def setUp(self) -> None:
        config.image_h_file = "tests/{instance}-image.h.pickle"
        config.pool = ["data"]

    def test_npimage(self):
        np = NPImage(1, "tests/images/ski.jpg", 0)
        self.assertEqual("JPG", np.ext)
        self.assertEqual("SKI.JPG", np.name)

    def test_npimageservice(self):
        np = NPImageService("tests/images/ski.jpg")
        self.assertEqual(484720, np.size)
        self.assertIsNotNone(np.pil)
        self.assertEqual("00000000fcffffff", str(np.ah()))
        self.assertEqual("f0e8f0d0d8cce6f0", str(np.dh()))
        self.assertEqual(1792, len(np.fv()))

    def test_npimageparser(self):
        np = NPImageParser()
        np.parse("tests/data-image.txt")
        self.assertEqual(6, len(np.dbi))
        np.save("parse", "jsonpickle")
        np.h("tests/images")
        np.save("h")

    def test_npimcomparer_comp(self):
        db = cyrilload.load(ImageTests.pickle)
        i1 = db[0][106]
        i2 = db[0][109]
        np = NPImageComparer()
        score = np.diff(i1, i2)
        self.assertEqual(1, score["dah"])
        self.assertEqual(1, score["dfv"])

    def test_npimcomparer(self):
        db = cyrilload.load(ImageTests.pickle)
        i1 = db[0][106]
        i2 = db[0][109]
        np = NPImageComparer()
        score = np.compare(i1, i2)
        self.assertEqual(1, score)

    def test_npimnearest_byimage(self):
        np = NPImageNearest(ImageTests.pickle)
        score = np.search_by_im(106)
        self.assertEqual(109, score[0][0])
        self.assertEqual(107, score[1][0])
        self.assertAlmostEqual(0.84, score[1][1], delta=1e-2)
        score = np.search_by_im(107)
        self.assertEqual(106, score[0][0])
        self.assertAlmostEqual(0.85, score[0][1], delta=1e-2)

    def test_npimnearest_byproduct(self):
        np = NPImageNearest(ImageTests.pickle)
        score = np.search_by_product(53)
        self.assertEqual(54, score[0][0])
        self.assertAlmostEqual(1.0, score[0][1], delta=1e-2)

    def test_npimnearest_falsepositive(self):
        np = NPImageNearest(ImageTests.pickle)
        np.fp.add(106, 109)
        score = np.search_by_im(106)
        self.assertEqual(107, score[0][0])
        np.fp.reset()
        np.reset()
        score = np.search_by_im(106)
        self.assertEqual(109, score[0][0])

    def test_pool(self):
        pool = NPImageNearestPool()
        np = pool.get_instance("data")
        score = np.search_by_product(53)
        self.assertEqual(54, score[0][0])

    def test_nn(self):
        pool = NPImageNearestPool()
        np = pool.get_instance_nn("data")
        np.train()
        self.assertEqual(2, len(np.np.cache))
        res = np.predict()
        self.assertEqual(2, len(res))

    def test_family(self):
        pool = NPImageNearestPool()
        np = pool.get_instance("data")
        score = np.search_families(107)
        self.assertEqual(1, list(score.keys())[0])

    def test_barcode(self):
        np = NpImageBarcode()
        res = np.predict("tests/images/07323190073177_BOITE_01.JPG")
        self.assertEqual("0107323190073177172205281019F011", res)
        res = np.predict("tests/images/ski.jpg")
        self.assertIsNone(res)

    def test_ocr(self):
        np = NpImageOcr()
        res = np.predict_string("tests/images/07323190073177_BOITE_01.JPG")
        self.assertEqual("biogel indicator underglove pi surgical with coating blue polyisoprene used", res)
        res = np.predict_string("tests/images/ski.jpg")
        self.assertEqual("", res)


if __name__ == '__main__':
    unittest.main()
