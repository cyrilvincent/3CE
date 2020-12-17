import keras_ocr
import time
import argparse

class NpImOcr:
    pipeline = keras_ocr.pipeline.Pipeline()

    def predict(self, path):
        images = [keras_ocr.tools.read(url) for url in [path]]
        prediction_groups = NpImOcr.pipeline.recognize(images)
        res = [p[0] for p in prediction_groups[0]]
        return list(dict.fromkeys(res))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OCR")
    parser.add_argument("path", help="Image path")
    args = parser.parse_args()
    np = NpImOcr()
    np.predict(args.path)
    t = time.perf_counter()
    res = np.predict(args.path)
    print(res)
    print(" ".join(res[:10]))
    print(f"Found in {time.perf_counter() - t:.1f}s")
