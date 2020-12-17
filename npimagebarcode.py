from pyzbar import pyzbar
import cv2
import time
import argparse
import keras_ocr


class NpImageBarcode:

    def predict(self, path):
        image = cv2.imread(path)
        barcodes = pyzbar.decode(image)
        if len(barcodes) == 0:
            return None
        data = barcodes[0].data.decode("utf-8")
        return data


class NpImageOcr:
    pipeline = keras_ocr.pipeline.Pipeline()

    def predict(self, path):
        images = [keras_ocr.tools.read(url) for url in [path]]
        prediction_groups = NpImageOcr.pipeline.recognize(images)
        res = [p[0] for p in prediction_groups[0]]
        return list(dict.fromkeys(res))

    def predict_string(self, path, limit=10):
        res = self.predict(path)
        return " ".join(res[:limit])

# images/chuv/Articles/Image/07323190073177_BOITE_01.JPG
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Barcode and OCR reader")
    parser.add_argument("path", help="Image path")
    args = parser.parse_args()
    np = NpImageBarcode()
    t = time.perf_counter()
    res = np.predict(args.path)
    print(res)
    print(f"Found in {time.perf_counter() - t:.3f}s")
    np = NpImageOcr()
    np.predict(args.path)
    t = time.perf_counter()
    res = np.predict(args.path)
    print(res)
    print(" ".join(res[:10]))
    print(f"Found in {time.perf_counter() - t:.1f}s")
