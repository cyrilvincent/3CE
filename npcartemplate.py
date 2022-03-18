import config
import argparse
from entities import Car
from typing import List, Tuple, Dict
from npproductnearest import NPNearest


class NPCarTemplate:

    def __init__(self, np: NPNearest):
        self.np = np
        self.todo = "{{TODO}}"
        self.max_product = 20

    def search_longest_starts_with(self, s1: str, s2: str) -> str:
        res = len(s1)
        for i in range(1, len(s1) + 1):
            if not s2.startswith(s1[:i]):
                res = i - 1
                break
        return s1[:res]

    def search_longest_ends_with(self, s1: str, s2: str) -> str:
        res = len(s1)
        for i in range(len(s1) - 1, -1, -1):
            if not s2.endswith(s1[i:]):
                res = i + 1
                break
        return s1[res:]

    def search_match(self, s1, s2) -> Tuple[str, str]:
        pre = self.search_longest_starts_with(s1, s2)
        suf = self.search_longest_ends_with(s1, s2)
        if pre == suf:
            suf = ""
        return pre, suf

    def get_template_by_car(self, c1: Car, c2: Car) -> str:
        if c1.val == c2.val:
            return c1.val
        elif c1.val == "" or c2.val == "":
            return ""
        res = self.search_match(c1.val, c2.val)
        if res[0] == "" and res[1] == "":
            return ""
        elif len(res[1]) > 1 :
            return res[0] + self.todo + res[1]
        elif res[0] != c1.val:
            return res[0] + self.todo
        else:
            return res[0]

    def get_templates_from_cars(self, cars1: Dict[int, Car], cars2: Dict[int, Car]) -> Dict[int, str]:
        res: Dict[int, str]  = {}
        for cid in cars1.keys():
            if cid in cars2:
                res[cid] = self.get_template_by_car(cars1[cid], cars2[cid])
            else:
                res[cid] = cars1[cid].val
        return res

    def take_min_templates(self, res: Dict[int, str], templates: Dict[int, str]):
        for k in templates.keys():
            if self.todo in templates[k]:
                if self.todo not in res[k] or len(templates[k]) < len(res[k]):
                    res[k] = templates[k]
            elif templates[k] == "":
                res[k] = ""

    def cars_to_dict(self, l: List[Car]) -> Dict[int, Car]:
        cars: Dict[int, Car] = {}
        for c in l:
            cars[c.id] = c
        return cars

    def get_templates(self, fid: int) -> Dict[int, str]:
        pids = [k for k in self.np.db.keys() if self.np.db[k].fid == fid]
        if len(pids) < 2:
            return {}
        cars1 = self.cars_to_dict(self.np.db[pids[0]].l)
        cars2 = self.cars_to_dict(self.np.db[pids[1]].l)
        res = self.get_templates_from_cars(cars1, cars2)
        for i in range(2, min(self.max_product, len(pids))):
            carsi = self.cars_to_dict(self.np.db[pids[i]].l)
            templates = self.get_templates_from_cars(cars1, carsi)
            self.take_min_templates(res, templates)
        return res


if __name__ == '__main__':
    print("NP Car Template Maker")
    print("=====================")
    print(f"V{config.version}")
    parser = argparse.ArgumentParser(description="Car Template maker")
    parser.add_argument("instance", help="Instance")
    parser.add_argument("fid", help="Familly id", type=int)
    args = parser.parse_args()
    product_h_file = config.product_h_file.replace("{instance}", args.instance)
    npn = NPNearest(product_h_file)
    np = NPCarTemplate(npn)
    res = np.get_templates(args.fid)
    print(res)

    # chuv-light 1

