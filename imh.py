import imagehash
import os
import numpy as np
from PIL import Image

class ImageHashModel:

    def __init__(self, path):
        self.path = path
        self.pil = Image.open(path)
        self.size = os.stat(path)[6]

    def ah(self):
        return imagehash.average_hash(self.pil)

    def dh(self):
        return imagehash.dhash(self.pil)

    def ph(self):
        return imagehash.phash(self.pil)

    def wh(self):
        return imagehash.whash(self.pil)

    def wdh(self):
        return imagehash.whash(self.pil, mode="db4")

    def zh(self):
        return imagehash.average_hash(self.ztransform())

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