import imagehash
import os
import numpy as np
import time
import tensorflow as tf
from absl import logging
from PIL import Image

class ShazImage:
    """
    https://pypi.org/project/ImageHash/
    """

    model = None

    def __init__(self, path):
        self.path = path
        if ShazImage.model == None:
            t = time.perf_counter()
            print(f"Load TF FV model: ")
            ShazImage.model = tf.saved_model.load("hubmodule/feature-vector.4")
            print(f"Loaded in {time.perf_counter() - t:.1f} s")
            logging.set_verbosity(logging.ERROR)
        self.pil = Image.open(path)
        self.size = os.stat(path)[6]
        self.tfimg = None

    def ah(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.average_hash(self.pil)

    def a2h(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.average_hash(self.pil, hash_size=16)

    def dh(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
        :return:
        """
        return imagehash.dhash(self.pil)

    def ph(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.phash(self.pil)

    def wh(self):
        """
        #https://fullstackml.com/wavelet-image-hash-in-python-3504fdd282b5
        :return:
        """
        return imagehash.whash(self.pil)

    def wdh(self):
        return imagehash.whash(self.pil, mode="db4")

    def zh(self):
        return imagehash.average_hash(self.ztransform())

    def fv(self):
        """
        https://towardsdatascience.com/image-similarity-detection-in-action-with-tensorflow-2-0-b8d9a78b2509
        :return:
        """
        if self.tfimg is None:
            self.tfimg = self.load_img(self.path)
        features = ShazImage.model(self.tfimg)
        return np.squeeze(features)

    def alpharemover(self, image):
        if image.mode != 'RGBA':
            return image
        canvas = Image.new('RGBA', image.size, (255,255,255,255))
        canvas.paste(image, mask=image)
        return canvas.convert('RGB')

    def ztransform(self):
        image = self.alpharemover(self.pil)
        image = image.convert("L").resize((8, 8), Image.ANTIALIAS)
        data = image.getdata()
        quantiles = np.arange(100)
        quantiles_values = np.percentile(data, quantiles)
        zdata = (np.interp(data, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
        image.putdata(zdata)
        return image

    def load_img(self, path):
        img = tf.io.read_file(path)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize_with_pad(img, 224, 224)
        img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        return img