from typing import List

class CyrilLWC:

    def __init__(self, s:str):
        self.score = 0
        self.s1 = s
        self.h1 = self.hash(s)
        self.s2 = None
        self.h2 = None

    def hash(self, s)->List[str]:
        s = s.strip().upper().replace(",", " ").replace("'", " ").replace("!", " ").replace(";", " ").replace(":", " ").replace("?", " ").replace('"', " ").replace("\t", " ")
        l:List[str] = s.split(" ")
        l.sort(key = lambda x : -len(x))
        return l

    def compare(self, s2:str)->int:
        self.s2 = s2
        self.h2 = s2.strip().upper()
        for s in self.h1:
            if len(s) > 0 and s in self.h2:
                self.score += len(s) + 1
            else:
                break

    @property
    def precision(self):
        return min(1.0,self.score / max(len(self.s1), len(self.s2)))

    @property
    def recall(self):
        return min(1.0, self.score / len(self.s1))

if __name__ == '__main__':
    s = "Hello World! a bb ccc dddd eeeee ffffff"
    c = CyrilLWC(s)
    c.hash(s)
    print(c.h1)
    c.compare(s)
    print(c.score)
    print(len("Hello World! a bb ccc dddd eeeee ffffff"))
    print(c.precision)
    print(c.recall)


