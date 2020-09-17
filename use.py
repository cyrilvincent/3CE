import tensorflow as tf
import numpy as np
import time
from absl import logging
from typing import List
import config

class USE:
    """
    Google Universal Sentence Encoder
    """

    model = None

    def __init__(self):
        """
        Initialize USE model
        """
        if USE.model == None:
            t = time.perf_counter()
            print(f"Load TF USE model: {config.use}")
            USE.model = tf.saved_model.load(config.use)
            print(f"Loaded in {time.perf_counter() - t:.1f} s")
        logging.set_verbosity(logging.ERROR)

    def embed(self, inputs:List[str])->List[List[float]]:
        """
        Apply USE model
        :param inputs: list of sentences
        :return: list of h (512 floats) in Tensor types
        """
        return USE.model(inputs)

    def hs(self, inputs:List[str])->List[List[float]]:
        """
        Apply USE model
        :param inputs: list of sentences
        :return: list of h (512 floats) in numpy types
        """
        return self.embed(inputs).numpy()

    def h(self, input:str)->List[float]:
        """
        Apply USE model
        :param input: A sentence
        :return: h : List of 512 floats
        """
        return self.hs([input])[0].tolist()

if __name__ == '__main__':
    l = ["La télécommande ne marche pas", "La télécommande ne fonctionne pas correctement","Je marche avec des pas dans la rue"]
    use = USE()
    hs = use.hs(l)
    print(hs)
    print(np.inner(hs[0], hs[1]))
    print(np.inner(hs[0], hs[2]))


