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
                    'Light-red':([0,157, 25], [6,255,255]),
                    'Light-Pink':([0,0, 25], [6,157,255]),
                    'Orange':([6, 33, 168], [23, 255, 255]),
                    'Brown':([6, 33, 25], [23, 255, 168]),
                    'Yellow':([23, 33, 25], [32, 255, 255]),
                    'Green':([32, 33, 25], [75, 255, 255]),
                    'Blue-Green':([75, 33, 25], [90, 255, 255]),
                    'Blue':([90,33, 45], [123, 255, 255]),
                    'Purple':([123, 112, 25], [155, 255, 255]),
                    'Light-Purple':([123, 33, 25], [155, 125, 255]),
                    'Pink':([155,34, 25], [180,225,255]),
                    'Deep-Pink':([175,0, 25], [180,157,255]),
                    'Deep-red':([175,157, 25], [180,255,255]),
}

dictionary9 ={ # 9 colors
                    'white':([0, 0, 146], [180, 34, 255]),
                    'black': ([0, 0, 0], [180, 255, 26]),
                    'orange':([10, 38, 71], [20, 255, 255]),
                    'yellow':([18, 28, 20], [33, 255, 255]),
                    'green':([36, 10, 33], [88, 255, 255]),
                    'blue':([87,32, 17], [120, 255, 255]),
                    'purple':([138, 66, 39], [155, 255, 255]),
                    'red': ([0, 38, 56], [10, 255, 255]),
                    'red2':([170,112, 45], [180,255,255]),
}


class ColorDetect:

    def __init__(self, color_dict: Dict[str, Tuple[List[int], List[int]]]):
        self.image: Optional[NDArray] = None
        self.hsv: Optional[NDArray] = None
        self.mask: Optional[NDArray] = None
        self.color_dict = color_dict
        self.rgb_dict: Dict[str, Tuple[int, int, int]] = {}
        self.color_count_dict: Dict[str, int] = {}
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
        bytes = base64.b64decode(b64)
        array = np.frombuffer(bytes, np.uint8)
        self.image = cv2.imdecode(array, cv2.IMREAD_COLOR)

    def load_from_np(self, image: NDArray):
        self.image = image

    def crop(self, ratio=0.2):
        height, width, channels = self.image.shape
        croph = int(height * ratio / 2)
        cropw = int(width * ratio / 2)
        self.image = self.image[croph:-croph, cropw:-cropw]

    def blur(self, ksize=11):
        self.image = cv2.GaussianBlur(self.image, (ksize, ksize), 0)

    def create_mask(self, lower: List[int], upper: List[int], erode_dilate: int):
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        self.mask = cv2.inRange(self.hsv, lower, upper)
        if erode_dilate != 0:
            self.mask = cv2.erode(self.mask, None, iterations=erode_dilate)
            self.mask = cv2.dilate(self.mask, None, iterations=erode_dilate)

    def fine_tuning(self):
        if "red2" in self.color_count_dict:
            self.color_count_dict["red"] += self.color_count_dict["red2"]
            self.color_count_dict["red2"] = 0
        if "white" in self.color_count_dict:
            self.color_count_dict["white"] /= 2
        if "black" in self.color_count_dict:
            self.color_count_dict["black"] /= 3
        if "gray" in self.color_count_dict:
            self.color_count_dict["gray"] /= 1.5

    def softmax(self) -> OrderedDict[str, int]:
        total = sum(self.color_count_dict.values())
        return collections.OrderedDict(
            {k: v / total for k, v in sorted(self.color_count_dict.items(), key=lambda item: item[1], reverse=True)})

    def predict(self, blur=True, erode_dilate=3, fine_tuning=True) -> OrderedDict[str, int]:
        if self.image is None:
            raise ValueError("No image loaded")
        self.crop()
        if blur:
            self.blur()
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        for key, (lower, upper) in self.color_dict.items():
            self.create_mask(lower, upper, erode_dilate)
            count = cv2.countNonZero(self.mask)
            self.color_count_dict[key] = count
            if fine_tuning:
                self.fine_tuning()
        res = self.softmax()
        return res

if __name__ == '__main__':
    path = 'tests/images/tumblr1.jpg'
    print(path)
    b64 = None
    with open(path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes)
    cd = ColorDetect(dictionary9)
    cd.load_from_base64(b64)
    res = cd.predict()
    print(res)
    color = list(res)[0]
    score = list(res.values())[0]
    top3 = list(res)[:3]
    top3_score = list(res.values())[:3]
    print(f"the dominant color is: {color} @{score * 100:.0f}%")
    print(cd.get_rgb(color))
    print(top3)

