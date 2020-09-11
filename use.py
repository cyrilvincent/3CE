import tensorflow as tf
import numpy as np
import time
from absl import logging
import os

#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

"""
Universal Sentence Encoder
"""
class USE:

    model = None

    def __init__(self):
        if USE.model == None:
            t = time.perf_counter()
            print("Load TF model")
            USE.model = tf.saved_model.load("hubmodule/universal-sentence-encoder.4")
            print(f"Loaded in {time.perf_counter() - t:.1f} s")
        logging.set_verbosity(logging.ERROR)

    def embed(self, inputs):
        return USE.model(inputs)

    def hs(self, inputs):
        return self.embed(inputs).numpy()



if __name__ == '__main__':
    l = ["La télécommande ne marche pas", "La télécommande ne fonctionne pas correctement","Je marche avec des pas dans la rue"]
    use = USE()
    hs = use.hs(l)
    print(hs)
    print(use.compare(hs[0], hs[1]))
    print(use.compare(hs[0], hs[2]))


