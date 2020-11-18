import config
import tensorflow.keras as keras
import importlib

print("NP Image Categorization")
print("=======================")
print(f"V{config.version}")
# config.model = "tensorflow.keras.applications.mobilenet_v2.MobileNetV2"
# config.model = "tensorflow.keras.applications.resnet_v2.ResNet152V2"
# config.model = "tensorflow.keras.applications.vgg16.VGG16"
module = importlib.import_module(config.model[:config.model.rindex(".")])
s = config.model.split('.')[-1]
print(f"Model:{s}")
model = eval(f"module.{s}()")
image = keras.preprocessing.image.load_img('images/IMG_20160426_101138.jpg', target_size=(224, 224))
image = keras.preprocessing.image.img_to_array(image)
image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
image = module.preprocess_input(image)
predicts = model.predict(image)
labels = module.decode_predictions(predicts)
print(labels)
print(f"{labels[0][0][1]} {labels[0][0][2]*100:.1f}%")
