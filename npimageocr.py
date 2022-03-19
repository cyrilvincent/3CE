from pyzbar import pyzbar
import cv2
import time
import argparse
import keras_ocr
#
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class NpImageOcr:
    pipeline = keras_ocr.pipeline.Pipeline()

    def predict(self, path):
        images = [keras_ocr.tools.read(url) for url in [path]]
        prediction_groups = NpImageOcr.pipeline.recognize(images)
        res = [p[0] for p in prediction_groups[0]]
        return list(dict.fromkeys(res))

    def predict_string(self, path, limit=10, min=3):
        res = self.predict(path)
        s = ""
        for r in res[:limit]:
            if len(r) >= min:
                s = s + " " + r
        s = s.strip()
        if len(s) == 0:
            return None
        return s

# images/chuv/Articles/Image/07323190073177_BOITE_01.JPG 0.035s
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Barcode and OCR reader")
    parser.add_argument("path", help="Image path")
    args = parser.parse_args()
    np = NpImageOcr()
    np.predict(args.path)
    t = time.perf_counter()
    res = np.predict(args.path)
    print(res)
    print(" ".join(res[:10]))
    print(f"Found in {time.perf_counter() - t:.1f}s")
