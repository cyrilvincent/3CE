import unittest
import numpy as np
import config
import cyrilload
from entities import Product, Car
from npproductparser import USE, NPParser
from npproductcompare import NPComparer
from npproductnearest import NPNearest

class ProductTests(unittest.TestCase):

    def test_config(self):
        print(f"V{config.version}")

    def test_car(self):
        p = Product(1)
        c1 = Car(1,"car1",1.0,True)
        c2 = Car(2,"car2",0.5)
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
        self.assertEqual((2,512), ls.shape)
        l = use.h(s1)
        self.assertEqual(512, len(l))
        score = np.inner(ls[0], ls[1])
        self.assertAlmostEqual(0.73,score, delta=1e-2)

    def test_parser(self):
        np = NPParser()
        np.parse("tests/data.txt")
        self.assertEqual(3, len(np.db))
        np.save("parse","jsonpickle")
        np.normalize()
        np.save("normalize","jsonpickle")
        np.h()
        np.save("h","jsonpickle")
        np.save("h")

    def test_npcompare_comph(self):
        use = USE()
        s1 = "L'herbe est verte"
        s2 = "Le gazon est vert"
        ls = use.hs([s1, s2])
        np = NPComparer()
        score = np.comph(ls[0], ls[1])
        self.assertAlmostEqual(0.73, score, delta=1e-2)

    def test_npcompare_compv(self):
        np = NPComparer()
        score = np.compv("abc","ABC")
        self.assertEqual(1.0, score)
        score = np.compv("abc","abcd")
        self.assertAlmostEqual(0.375, score, delta = 1e-2)

    def test_npcompare_compvl(self):
        np = NPComparer()
        score = np.compvl("3.14","3.14")
        self.assertEqual(1.0, score)
        score = np.compvl("3.14","3.0")
        self.assertAlmostEqual((1 - (0.14 / 3.14)) / 4, score, delta = 1e-2)
        s1 = "L'herbe est verte"
        s2 = "Le gazon est vert"
        score = np.compvl(s1, s2)
        self.assertAlmostEqual(0.65, score, delta = 1e-2)

    def test_npcompare_compp(self):
        db = cyrilload.load("tests/data.h.pickle")
        np = NPComparer()
        score = np.compp(db[164114], db[164115])
        self.assertEqual(6, len(score))
        self.assertAlmostEqual(0.52, score[0][0], delta = 1e-2)
        self.assertAlmostEqual(0.1, score[0][1], delta = 1e-2)

    def test_npcompare_comppl(self):
        db = cyrilload.load("tests/data.h.pickle")
        np = NPComparer()
        score = np.comppl(db[164114], db[164115])
        self.assertEqual(6, len(score))
        self.assertAlmostEqual(0.94, score[0][0], delta = 1e-2)
        self.assertAlmostEqual(0.29, score[0][1], delta = 1e-2)

    def test_npcompare_compare(self):
        db = cyrilload.load("tests/data.h.pickle")
        np = NPComparer()
        score = np.compare(db[164114], db[164115])
        self.assertAlmostEqual(0.62, score, delta = 1e-2)

    def test_npcompare_comparel(self):
        db = cyrilload.load("tests/data.h.pickle")
        np = NPComparer()
        score = np.comparel(db[164114], db[164115])
        self.assertAlmostEqual(0.92, score, delta = 1e-2)

    def test_npnearest_searchl(self):
        np = NPNearest("tests/data.h.pickle")
        l = np.get_ids()
        self.assertEqual(3, len(l))
        p = np.get_by_id(164114)
        self.assertEqual(164114, p.id)
        score = np.searchl(164114, [164115, 164113])
        self.assertEqual(164115, score[0][0])
        self.assertAlmostEqual(0.92, score[0][1], delta=1e-2)
        self.assertEqual(164113, score[1][0])
        self.assertAlmostEqual(0.67, score[1][1], delta=1e-2)

    def test_npnearest(self):
        np = NPNearest("tests/data.h.pickle")
        score = np.search(164114)
        self.assertEqual(164115, score[0][0])
        self.assertAlmostEqual(0.77, score[0][1], delta=1e-2)
        self.assertEqual(164113, score[1][0])
        self.assertAlmostEqual(0.58, score[1][1], delta=1e-2)









