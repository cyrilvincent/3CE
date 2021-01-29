import unittest
import numpy as np
import config
import cyrilload
from entities import Product, Car
from npproductparser import USE, NPParser
from npproductcompare import NPComparer
from npproductnearest import NPNearest, NPNearestPool, NPNearestNN



class ProductTests(unittest.TestCase):

    pickle = "tests/data.h.pickle"

    def setUp(self) -> None:
        config.product_h_file = "tests/{instance}.h.pickle"
        config.pool = ["data"]

    def test_config(self):
        print(f"V{config.version}")

    def test_car(self):
        p = Product(1)
        c1 = Car(1, "car1", 1.0, True)
        c2 = Car(2, "car2", 0.5)
        p.l.append(c1)
        p.l.append(c2)
        self.assertTrue(p.contains(c1))
        c = p.get_car_by_id(1)
        self.assertEqual(c1, c)

    def test_use(self):
        use = USE()
        s1 = "L'herbe est verte"
        s2 = "Le gazon est vert"
        ls = use.hs([s1, s2])
        self.assertEqual((2, 512), ls.shape)
        l = use.h(s1)
        self.assertEqual(512, len(l))
        score = np.inner(ls[0], ls[1])
        self.assertAlmostEqual(0.73, score, delta=1e-2)

    def test_parser(self):
        np = NPParser()
        np.parse("tests/data.txt")
        self.assertEqual(3, len(np.db))
        np.save("parse", "jsonpickle")
        np.normalize()
        np.save("normalize", "jsonpickle")
        np.h()
        np.save("h", "jsonpickle")
        np.save("h")

    def test_npcompare_compare_h_use(self):
        use = USE()
        s1 = "L'herbe est verte"
        s2 = "Le gazon est vert"
        ls = use.hs([s1, s2])
        np = NPComparer()
        score = np.compare_h_use(ls[0], ls[1])
        self.assertAlmostEqual(0.73, score, delta=1e-2)

    def test_npcompare_compare_value_string_equality(self):
        np = NPComparer()
        score = np.compare_value_string_equality("abc", "ABC")
        self.assertEqual(1.0, score)
        score = np.compare_value_string_equality("abc", "abcd")
        self.assertAlmostEqual(0.375, score, delta=1e-2)

    def test_npcompare_compare_value_gestalt(self):
        np = NPComparer()
        score = np.compare_value_gestalt("3.14", "3.14")
        self.assertEqual(1.0, score)
        score = np.compare_value_gestalt("3.14", "3.0")
        self.assertAlmostEqual((1 - (0.14 / 3.14)) / 4, score, delta=1e-2)
        s1 = "L'herbe est verte"
        s2 = "Le gazon est vert"
        score = np.compare_value_gestalt(s1, s2)
        self.assertAlmostEqual(0.65, score, delta=1e-2)

    def test_npcompare_compare_product_to_scores(self):
        db = cyrilload.load(ProductTests.pickle)
        np = NPComparer()
        scores = np.compare_product_to_scores(db[164114], db[164115])
        self.assertEqual(6, len(scores))
        self.assertAlmostEqual(0.52, scores[0][0], delta=1e-2)
        self.assertAlmostEqual(0.1, scores[0][1], delta=1e-2)

    def test_npcompare_compare_product_gestalt_to_scores(self):
        db = cyrilload.load(ProductTests.pickle)
        np = NPComparer()
        scores = np.compare_product_gestalt_to_scores(db[164114], db[164115])
        self.assertEqual(6, len(scores))
        self.assertAlmostEqual(0.94, scores[0][0], delta=1e-2)
        self.assertAlmostEqual(0.29, scores[0][1], delta=1e-2)

    def test_npcompare_compare_product(self):
        db = cyrilload.load(ProductTests.pickle)
        np = NPComparer()
        score = np.compare_product(db[164114], db[164115])
        self.assertAlmostEqual(0.62, score, delta=1e-2)

    def test_npcompare_compare_product_gestalt(self):
        db = cyrilload.load(ProductTests.pickle)
        np = NPComparer()
        score = np.compare_product_gestalt(db[164114], db[164115])
        self.assertAlmostEqual(0.92, score, delta=1e-2)

    def test_npnearest_search_gestalt(self):
        np = NPNearest(ProductTests.pickle)
        l = np.get_ids()
        self.assertEqual(3, len(l))
        p = np[164114]
        self.assertEqual(164114, p.id)
        scores = np.search_gestalt(164114, [164115, 164113])
        self.assertEqual(164115, scores[0][0])
        self.assertAlmostEqual(0.92, scores[0][1], delta=1e-2)
        self.assertEqual(164113, scores[1][0])
        self.assertAlmostEqual(0.67, scores[1][1], delta=1e-2)

    def test_npnearest(self):
        np = NPNearest(ProductTests.pickle)
        scores = np.search(164114)
        self.assertEqual(164115, scores[0][0])
        self.assertAlmostEqual(0.77, scores[0][1], delta=1e-2)
        self.assertEqual(164113, scores[1][0])
        self.assertAlmostEqual(0.58, scores[1][1], delta=1e-2)

    def test_npnearest_false(self):
        np = NPNearest(ProductTests.pickle)
        scores = np.search(164114, use2=False)
        self.assertEqual(164115, scores[0][0])
        self.assertAlmostEqual(0.92, scores[0][1], delta=1e-2)
        self.assertEqual(164113, scores[1][0])
        self.assertAlmostEqual(0.67, scores[1][1], delta=1e-2)

    def test_float_value(self):
        np = NPNearest(ProductTests.pickle)
        p = np[164113]
        car = p.l[3]
        self.assertEqual(1012, car.id)
        self.assertEqual("1527-2", car.val)
        score = np.comp.compare_value_gestalt(car.val, "1525")
        self.assertEqual(0.6, score)

    def test_pool(self):
        np = NPNearestPool()
        npn = np["data"].np
        p = npn[164113]
        self.assertIsNotNone(p)

    def test_npnearestnn(self):
        np = NPNearestNN(ProductTests.pickle, use2=True)
        np.train()
        self.assertEqual(2, len(np.np.cache))
        np.save()
        np.load()
        self.assertEqual(2, len(np.np.cache))
        res = np.predict()
        self.assertEqual(0, len(res))

    def test_size(self):
        np = NPNearest(ProductTests.pickle)
        self.assertEqual(3, np.length)
        self.assertEqual((3, 8), np.shape)
        self.assertEqual(24, np.size)

    def test_compare_product_no_common_carac(self):
        np = NPComparer()
        p1 = Product(1)
        p2 = Product(2)
        res = np.compare_product(p1, p2)
        self.assertEqual(0, res)
        res = np.compare_product_gestalt(p1, p2)
        self.assertEqual(0, res)

    def test_save_empty(self):
        np = NPParser()
        np.save_empty("tests/empty")


if __name__ == '__main__':
    unittest.main()
