import config
import tensorflow.keras as keras
import importlib
import logging
import time

class NpImageCategorize:

    module_MobileNetV2 = importlib.import_module("tensorflow.keras.applications.mobilenet_v2")
    module_VGG16 = importlib.import_module("tensorflow.keras.applications.vgg16")
    module_Xception = importlib.import_module("tensorflow.keras.applications.xception")

    def predict(self, path:str, model:str="MobileNetV2"):
        print(f"Predict with model {model}")
        self.module = eval(f"NpImageCategorize.module_{model}")
        size = 224
        if "ception" in model:
            size = 299
        model = eval(f"self.module.{model}()")
        image = keras.preprocessing.image.load_img(path, target_size=(size, size))
        image = keras.preprocessing.image.img_to_array(image)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        image = self.module.preprocess_input(image)
        predicts = model.predict(image)
        return predicts

    def labels(self, predicts):
        return self.module.decode_predictions(predicts)[0]

if __name__ == '__main__':

    print("NP Image Categorization")
    print("=======================")
    print(f"V{config.version}")
    cat = NpImageCategorize()
    predicts = cat.predict('images/mock/IMG_20160426_101138.jpg')
    t = time.perf_counter()
    predicts = cat.predict('images/mock/IMG_20160426_101138.jpg') #1.4s, 71%
    labels = cat.labels(predicts)
    print(labels)
    print(f"{labels[0][1]} {labels[0][2]*100:.1f}%")
    print(f"Predict in {time.perf_counter() - t:.1f} s")
    t = time.perf_counter()
    predicts = cat.predict('images/mock/IMG_20160426_101138.jpg',"VGG16") #1.8s, 71%
    labels = cat.labels(predicts)
    print(f"{labels[0][1]} {labels[0][2]*100:.1f}%")
    print(f"Predict in {time.perf_counter() - t:.1f} s")
    t = time.perf_counter()
    predicts = cat.predict('images/mock/IMG_20160426_101138.jpg',"Xception") #1.6s, 79%
    labels = cat.labels(predicts)
    print(f"{labels[0][1]} {labels[0][2]*100:.1f}%")
    print(f"Predict in {time.perf_counter() - t:.1f} s")


