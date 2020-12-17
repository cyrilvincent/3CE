from pyzbar import pyzbar
import cv2
import time
import argparse

class NpImBarcode:

    def predict(self, path):
        image = cv2.imread(path)
        barcodes = pyzbar.decode(image)
        if len(barcodes) == 0:
            return None
        data = barcodes[0].data.decode("utf-8")
        return data

#"images/chuv/Articles/Image/07323190073177_BOITE_01.JPG"
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Barcode reader")
    parser.add_argument("path", help="Image path")
    args = parser.parse_args()
    np = NpImBarcode()
    t = time.perf_counter()
    res = np.predict(args.path)
    print(res)
    print(f"Found in {time.perf_counter() - t:.3f}s")
