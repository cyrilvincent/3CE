import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dropout, Flatten, Dense
from tensorflow.keras import applications
import struct
import json
import bitstring
import base64

batch_size = 1

datagen = ImageDataGenerator(rescale=1. / 255)

model = applications.mobilenet_v2.MobileNetV2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))
x = model.output
x = Flatten()(x)

model = Model(inputs=model.input, outputs=x)

model.summary()


generator = datagen.flow_from_directory(
    "images",
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode=None,
    shuffle=False)

bn = model.predict(generator)
print("Save CSV")
with open('../images/mnbn.csv', 'w', newline='') as f:
    idx = 0
    for row in bn:
        s = generator.filenames[idx]
        idx += 1
        for i in row:
            s+=f",{float(i)}"
        s += "\n"
        f.write(s)
        print(s)

def diff(f1, f2):
    score = 0
    for i1, i2 in zip(f1, f2):
        score += abs(i1 - i2) ** 2
    return score ** 0.5

print(diff(bn[0], bn[0]))
print(diff(bn[0], bn[1]))
print(diff(bn[0], bn[2]))
print(diff(bn[0], bn[3]))
print(diff(bn[1], bn[2]))
print(diff(bn[1], bn[3]))
print(diff(bn[2], bn[3]))


