from typing import Iterable, List
import numpy as np

class PlagiatC:

    def __init__(self, s:str):
        self.score = 0
        self.s1 = s
        self.h1 = self.hash(s)
        self.s2 = None
        self.h2 = None

    def hash(self, s)->Iterable[str]:
        s = s.strip().upper().replace(",", " ").replace("'", " ").replace("!", " ").replace(";", " ").replace(":", " ").replace("?", " ").replace('"', " ").replace("\t", " ")
        l:List[str] = s.split(" ")
        return np.array(l)

    def compare(self, s2:str)->int:
        self.s2 = s2
        self.h2 = self.hash(s2)
        print(self.h1, self.h2)
        res = np.intersect1d(self.h1, self.h2)
        self.score = sum([len(x) for x in res])

    @property
    def precision(self):
        return min(1.0,self.score / max(len(self.s1), len(self.s2)))

    @property
    def recall(self):
        return min(1.0, self.score / len(self.s1))

if __name__ == '__main__':
    s = "Hello World! a bb ccc dddd eeeee ffffff"
    c = PlagiatC(s)
    print(c.hash(s))
    c.compare("Hello World! b bb xxxx dddd eeeee ffffff")
    print(c.score)
    print(c.precision)
    print(c.recall)


