import argparse
import use
import numpy as np
import npcompare
#import tensorflow_text

parser = argparse.ArgumentParser()
parser.add_argument("s1", help="Sentence")
parser.add_argument("s2", help="Sentence to compare")
args = parser.parse_args()
m = use.USE()
h1, h2 = m.hs([args.s1,args.s2])
score = np.inner(h1, h2)
print(score)
m = npcompare.NPComparer()
score = m.compvl(args.s1, args.s2)
print(score)





