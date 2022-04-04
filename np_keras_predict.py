import base64

import numpy as np
import tensorflow.keras as keras
import tensorflow as tf
import os
from typing import Tuple


class NpKerasPredict:

    labels = ["02-Chauffage_PAC", "Entrees_Air_Bouches", "04-Ventilation_Double_Flux_Individuelle_Purification_Air",
       "05-Ventilation_Simple_Flux_Individuelle_Purification_Air", "06-Ventilation_Simple_Flux_Centralisee",
       "07-Centrales_Traitement_Air", "08-Desenfumage_Compartimentage", "09-Reseaux",
       "10-Reglages_Regulation_Debit_Mesure", "11-Diffusion_Air", "12-Aspiration_Centralisee",
       "13-Mesure_Connectivite"]

    def __init__(self):
        self.model = keras.models.load_model("h5/resnet152v2_12_50_4_61.h5")
        self.image = None

    def load(self, path, target_size=(224, 224)):
        self.image = keras.preprocessing.image.load_img(path, target_size=target_size)
        self.image = keras.preprocessing.image.img_to_array(self.image)

    def load_from_b64(self, b64: str, target_size=(224, 224), url_safe=True):
        if not url_safe:
            b64 = b64.replace("+", "-").replace("/", "_")
        img = tf.io.decode_base64(b64)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, target_size, method="nearest")
        img = keras.preprocessing.image.img_to_array(img)
        self.image = img

    def load_from_np(self, np_array):
        self.image = np_array

    def normalize(self):
        # self.image *= 1. / 255
        self.image /= 127.5
        self.image -= 1.
        self.image = self.image.reshape((1, self.image.shape[0], self.image.shape[1], self.image.shape[2]))

    def predict(self):
        res = self.model.predict(self.image)[0]
        return res


if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    path = 'tests/images/aldes_cyril1.jpg'
    print(path)
    with open(path, "rb") as f:
        bytes = f.read()
        # b64 = base64.urlsafe_b64encode(bytes).decode("ascii")
        b64 = base64.b64encode(bytes).decode("ascii")
        print(b64)

    npkp = NpKerasPredict()
    # npkp.load(path)
    npkp.load_from_b64(b64, url_safe=False)
    npkp.normalize()
    res = npkp.predict()
    index = np.argmax(res)
    print(index, res[index])
    print(npkp.labels[index])