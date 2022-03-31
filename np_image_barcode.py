from pyzbar import pyzbar
import cv2
import time
import argparse
import keras_ocr
#
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class NpImageBarcode:

    def predict(self, path):
        image = cv2.imread(path)
        barcodes = pyzbar.decode(image)
        if len(barcodes) == 0:
            return None
        data = barcodes[0].data.decode("utf-8")
        return data.upper()

    def parse_int(self, s):
        if s is None or len(s) < 12:
            return None
        res = 0
        nbl = 0
        for i in range(len(s)):
            try:
                nb = int(s[i])
            except:
                nb = 0
                nbl += 1
                if nbl > 3:
                    return None
            res = res * 10 + nb
        return res

# images/chuv/Articles/Image/07323190073177_BOITE_01.JPG 0.035s
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Barcode and OCR reader")
    parser.add_argument("path", help="Image path")
    args = parser.parse_args()
    np = NpImageBarcode()
    t = time.perf_counter()
    res = np.predict(args.path)
    print(res)
    print(f"Found in {time.perf_counter() - t:.3f}s")
