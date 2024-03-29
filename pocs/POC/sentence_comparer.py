import argparse
from pocs.POC import use
import numpy as np
import np_product_compare
#import tensorflow_text

parser = argparse.ArgumentParser()
parser.add_argument("s1", help="Sentence")
parser.add_argument("s2", help="Sentence to compare")
args = parser.parse_args()
m = use.USE()
h1, h2 = m.hs([args.s1,args.s2])
score = np.inner(h1, h2)
print(score)
m = npproductcompare.NPComparer()
score = m.compare_value_gestalt(args.s1, args.s2)
print(score)





