# https://github.com/walton-wang929/Color_Recognition
import colorsys
import numpy as np
import cv2
import base64
import collections
from numpy.typing import NDArray
from typing import Optional, Dict, Tuple, List, OrderedDict

dictionary16 ={ # 16 colors
                    'white':([0, 0, 146], [180, 34, 255]), # /!\ Ce n'est pas du RGB mais du HSV
                    'black':([0, 0, 0], [180, 255, 26]),
                    'gray':([0, 0, 22], [180, 34, 146]), # Les angle H sont en degré sur 180 et non 360 mais S V en 255 et non en %
                    'light-red':([0,157, 25], [6,255,255]),
                    'light-Pink':([0,0, 25], [6,157,255]),
                    'orange':([6, 33, 168], [23, 255, 255]),
                    'brown':([6, 33, 25], [23, 255, 168]),
                    'yellow':([23, 33, 25], [32, 255, 255]),
                    'green':([32, 33, 25], [75, 255, 255]),
                    'blue-Green':([75, 33, 25], [90, 255, 255]),
                    'blue':([90,33, 45], [123, 255, 255]),
                    'purple':([123, 112, 25], [155, 255, 255]),
                    'light-Purple':([123, 33, 25], [155, 125, 255]),
                    'pink':([155,34, 25], [180,225,255]),
                    'deep-Pink':([175,0, 25], [180,157,255]),
                    'deep-red':([175,157, 25], [180,255,255]),
}

# https://www.rapidtables.com/convert/color/hsv-to-rgb.html
dictionary10 ={ # 9 colors
                    'white':([0, 0, 146], [180, 34, 255]),
                    'black': ([0, 0, 0], [180, 255, 63]),
                    'gray':([0, 0, 64], [180, 34, 145]),
                    'orange':([10, 38, 127], [20, 255, 255]),
                    'yellow':([18, 28, 32], [33, 255, 255]),
                    'green':([36, 25, 32], [88, 255, 255]),
                    'blue':([87, 32, 32], [120, 255, 255]), # ([87, 32, 17], [120, 255, 255]),
                    'purple':([138, 66, 32], [155, 255, 255]),
                    'red': ([0, 38, 127], [10, 255, 255]),
                    'red2':([170, 112, 127], [180,255,255]),
    # Original
    # 'White': ([0, 0, 116], [180, 57, 255]),
    # 'Light-red': ([0, 38, 56], [10, 255, 255]),
    # 'orange': ([10, 38, 71], [20, 255, 255]),
    # 'yellow': ([18, 28, 20], [33, 255, 255]),
    # 'green': ([36, 10, 33], [88, 255, 255]),
    # 'blue': ([87, 32, 17], [120, 255, 255]),
    # 'purple': ([138, 66, 39], [155, 255, 255]),
    # 'Deep-red': ([170, 112, 45], [180, 255, 255]),
    # 'black': ([0, 0, 0], [179, 255, 50]),
}


class ColorDetect:

    def __init__(self, color_dict: Dict[str, Tuple[List[int], List[int]]]):
        self.image: Optional[NDArray] = None
        self.hsv: Optional[NDArray] = None
        self.mask: Optional[NDArray] = None
        self.color_dict = color_dict
        self.rgb_dict: Dict[str, Tuple[int, int, int]] = {}
        self.color_count_dict: Dict[str, int] = {}
        self.shape = None
        self.size = 0
        self._make_rgb_dict()

    def _make_rgb_dict(self):
        for color in self.color_dict.keys():
            lower = self.color_dict[color][0]
            upper = self.color_dict[color][1]
            h = (lower[0] + upper[0]) / 2
            s = max(lower[1], upper[1])
            v = max(lower[2], upper[2])
            r, g, b = colorsys.hsv_to_rgb(h / 180, s / 255, v / 255)
            self.rgb_dict[color] = (int(np.round(r * 255)), int(np.round(g * 255)), int(np.round(b * 255)))

    def get_rgb(self, color: str):
        if self.rgb_dict is None or len(self.rgb_dict) != len(self.color_dict):
            self._make_rgb_dict()
        return self.rgb_dict[color]

    def load(self, path: str):
        self.image = cv2.imread(path)

    def load_from_base64(self, b64: str):
        bytes = base64.b64decode(b64.encode("ascii"))
        array = np.frombuffer(bytes, np.uint8)
        self.image = cv2.imdecode(array, cv2.IMREAD_COLOR)

    def load_from_np(self, image: NDArray):
        self.image = image

    def crop(self, ratio: float):
        height, width, channels = self.image.shape
        croph = int(height * ratio / 2)
        cropw = int(width * ratio / 2)
        if croph > 0 and cropw > 0:
            self.image = self.image[croph:-croph, cropw:-cropw]

    def blur(self, ksize: int):
        self.image = cv2.GaussianBlur(self.image, (ksize, ksize), 0)

    def create_mask(self, lower: List[int], upper: List[int], erode_dilate: int):
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        self.mask = cv2.inRange(self.hsv, lower, upper)
        if erode_dilate != 0:
            self.mask = cv2.erode(self.mask, None, iterations=erode_dilate)
            self.mask = cv2.dilate(self.mask, None, iterations=erode_dilate)

    def bw_ratio(self, ratio):
        if "white" in self.color_count_dict:
            self.color_count_dict["white"] *= ratio
        if "black" in self.color_count_dict:
            self.color_count_dict["black"] *= ratio
        if "gray" in self.color_count_dict:
            self.color_count_dict["gray"] *= 1 - ((1- ratio) / 2)

    def merge_reds(self):
        if "red2" in self.color_count_dict:
            self.color_count_dict["red"] += self.color_count_dict["red2"]
            self.color_count_dict["red2"] = 0

    def softmax(self) -> OrderedDict[str, int]:
        total = sum(self.color_count_dict.values())
        return collections.OrderedDict(
            {k: v / total for k, v in sorted(self.color_count_dict.items(), key=lambda item: item[1], reverse=True)})

    def predict(self, crop=0.2, blur=11, erode_dilate=3, bw_ratio=0.6) -> List[Tuple[str, float]]:
        # bw_ratio = 0.6 pour hashage, 0.8 ou 0.9 pour prediction
        if self.image is None:
            raise ValueError("No image loaded")
        self.shape = self.image.shape
        self.size = self.image.size
        self.crop(crop)
        if blur > 0:
            self.blur(blur)
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        for key, (lower, upper) in self.color_dict.items():
            self.create_mask(lower, upper, erode_dilate)
            count = cv2.countNonZero(self.mask)
            self.color_count_dict[key] = count
            self.merge_reds()
            self.bw_ratio(bw_ratio)
            # cv2.imwrite(f"tests/images/masks/test{key}_{count}.jpg", self.mask)
        res = self.softmax()
        colors = list(res)
        scores = list(res.values())
        return list(zip(colors, scores))

if __name__ == '__main__':
    path = 'tests/images/Velone-F400_Produit_001.png'
    print(path)
    with open(path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode("ascii")
    cd = ColorDetect(dictionary10)
    cd.load_from_base64(b64)
    res = cd.predict(crop=0.2, blur=11, erode_dilate=3, bw_ratio=0.8)
    print(res)
    print(f"the dominant color is: {res[0][0]} @{res[0][1] * 100:.0f}%")
    print(cd.get_rgb(res[0][0]))
    print(res[:3])
    print(cd.shape, cd.size)
