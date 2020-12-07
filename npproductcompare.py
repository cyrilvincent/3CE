import argparse
import sys
import numpy as np
import cyrilload
import difflib
import config
from entities import Product, Car
from typing import Iterable, List

__version__ = config.version

class NPComparer():
    """
    Compare to products
    """

    def compare_h_use(self, h1:Iterable[float], h2:Iterable[float])->float:
        """
        Use model compare two hash of 512 floats
        :param h1: h1
        :param h2: h2
        :return: The score
        """
        # h1 = np.array(h1)
        # h2 = np.array(h2)
        return np.inner(h1, h2)

    def compare_value_string_equality(self, v1:str, v2:str)->float:
        """
        Compare 2 string values
        :param v1: v1
        :param v2: v2
        :return: the score
        """
        v1 = v1.upper()
        v2 = v2.upper()
        if v1 == v2:
            return 1.0
        nb = 0
        for i in range(min(len(v1), len(v2))):
            if v1[i] == v2[i]:
                nb+=1
            else:
                break
        return (nb / max(len(v1), len(v2))) / 2

    def compare_value_gestalt(self, v1:str, v2:str)->float:
        """
        Compare 2 strings with Gestalt model
        :param v1: v1
        :param v2: v2
        :return: The score
        """
        try:
            n1 = float(v1)
            n2 = float(v2)
            if n1 == n2:
                score = 1
            else:
                score = (1 - min(1, (abs(n1 - n2) / n1))) / len(v1)
            return score
        except:
            sm = difflib.SequenceMatcher(lambda x: x in " \t.!?,;\n", v1.upper(), v2.upper())
            return sm.ratio()

    def compare_product_to_scores(self, p1:Product, p2:Product, main=False)->List[List[float]]:
        """
        Compare 2 products with the USE model
        :param p1: p1
        :param p2: p2
        :return: List[List[cid,score]]
        """
        res = []
        for c1 in p1.l:
            score = 0
            w = c1.w
            if p2.contains(c1):
                c2 = p2.get_car_by_id(c1.id)
                if c1.main:
                    score = self.compare_value_string_equality(c1.val, c2.val)
                    if score > 0.99:
                        w = 2
                    else:
                        if c1.h != None and c2.h != None:
                            score = (score + self.compare_h_use(c1.h, c2.h)) / 2
                        if score < 0.8:
                            w = 0.1
                else:
                    if c1.h != None and c2.h != None:
                        score = self.compare_h_use(c1.h, c2.h)
                    else:
                        score = self.compare_value_string_equality(c1.val, c2.val)
            else :
                w /= 2
            if not main or c1.main:
                res.append([score, w])
        return res

    def compare_product_gestalt_to_scores(self, p1:Product, p2:Product, main = False)->List[List[float]]:
        """
        Compare 2 products with the Gestalt model
        :param p1: p1
        :param p2: p2
        :return: List[List[cid,score]]
        """
        res = []
        for c1 in p1.l:
            score = 0
            w = c1.w
            if p2.contains(c1):
                c2 = p2.get_car_by_id(c1.id)
                v1 = c1.val.upper()
                v2 = c2.val.upper()
                score = self.compare_value_gestalt(v1, v2)
                if c1.main:
                    if score > 0.99:
                        w = 2
                    elif score < 0.8:
                        w = 0.1
                w /= min(1, abs(3-len(v1)) + 1)
            else:
                w /= 2
            if not main or c1.main:
                res.append([score, w])
        return res

    def compare_product(self, p1:Product, p2:Product, main=False)->float:
        """
        Main method with use model
        :param p1: p1
        :param p2: p2
        :return: The score
        """
        wscores = self.compare_product_to_scores(p1, p2, main)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

    def compare_product_gestalt(self, p1:Product, p2:Product, main = False)->float:
        """
        Main compare method for Gestalt model
        :param p1: p1
        :param p2: p2
        :return: The score
        """
        wscores = self.compare_product_gestalt_to_scores(p1, p2, main)
        return sum([t[0]*t[1] for t in wscores]) / sum(t[1] for t in wscores)

def display(p1:Product, p2:Product, res):
    limit = 40
    i = 0
    total = sum([w[1] for w in res])
    for r in res:
        c = p1.l[i]
        s = f"CID:{c.id} match {res[i][0] * 100:.0f}% * {res[i][1] / total:0.2f} \""
        s += f"{c.val[:limit]}"
        if len(c.val) > limit:
            s += "..."
        s += '" vs "'
        if p2.contains(c):
            s += p2.get_car_by_id(c.id).val[:limit]
            if len(p2.get_car_by_id(c.id).val) > limit:
                s+="..."
        s += '"'
        print(s)
        i += 1

if __name__ == '__main__':
    print("NPCompare")
    print("=========")
    print(f"V{__version__}")
    parser = argparse.ArgumentParser(description="Compare pid1 & pid2")
    parser.add_argument("pid1", help="Product id")
    parser.add_argument("pid2", help="Product id to compare")
    parser.add_argument("-m","--muse", action="store_true", help="Use MUSE insted of USE")
    args = parser.parse_args()
    product_h_file = "data/data.h.pickle"
    if args.muse:
        product_h_file = product_h_file.replace(".h.", ".linux.h.")
    db = cyrilload.load(product_h_file)
    p1 = db[int(args.pid1)]
    if p1 == None:
        print(f"{args.pid1} does not exist")
        sys.exit(1)
    p2 = db[int(args.pid2)]
    if p2 == None:
        print(f"{args.pid2} does not exist")
        sys.exit(2)
    print(f"Compare products {p1.id} and {p2.id}")
    comparer = NPComparer()
    res = comparer.compare_product_to_scores(p1, p2)
    print("Deep Learning Google DAN USE model:")
    display(p1,p2,res)
    print(f"USE Score: {comparer.compare_product(p1, p2) * 100:.0f}%")
    print()
    print("Machine Learning Gestalt+Cyril model:")
    res = comparer.compare_product_gestalt_to_scores(p1, p2)
    display(p1,p2,res)
    print(f"Gestalt Score: {comparer.compare_product_gestalt(p1, p2) * 100:.0f}%")
    print()
    print(f"Final Score: {(comparer.compare_product(p1, p2) + comparer.compare_product_gestalt(p1, p2)) / 2 * 100:.0f}%")


