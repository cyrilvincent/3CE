import imagehash
import os
import numpy as np
from PIL import Image

class ShazImage:
    """
    https://pypi.org/project/ImageHash/
    """

    def __init__(self, path):
        self.path = path
        self.pil = Image.open(path)
        self.size = os.stat(path)[6]

    def ah(self):
        """
        #http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
        :return:
        """
        return imagehash.average_hash(self.pil)

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