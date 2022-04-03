import tensorflow.keras as keras
import tensorflow as tf
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
tf.random.set_seed(0)
path = "images/aldes/Catalogue_Aldes/ai2"
model = keras.applications.mobilenet_v2.MobileNetV2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))
model = keras.applications.vgg16.VGG16(include_top=False, weights="imagenet", input_shape=(224, 224, 3))
# model = keras.applications.resnet_v2.ResNet152V2(include_top=False, weights="imagenet", input_shape=(224, 224, 3))



batchSize = 4
epochs = 50
nb_classes = 12
name = model.name

trainset = keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255,
                                                        rotation_range=20,
                                                        # width_shift_range=0.05,
                                                        # height_shift_range=0.05,
                                                        brightness_range=(0.8, 1.2),
                                                        shear_range=0.2,
                                                        zoom_range=0.1,
                                                        validation_split=0.2)

for layer in model.layers:
    layer.trainable = False

x = model.output
x = keras.layers.Flatten()(x)
x = keras.layers.Dense(2048, activation="relu")(x)
x = keras.layers.Dropout(0.5)(x)
x = keras.layers.Dense(1024, activation="relu")(x)
x = keras.layers.Dropout(0.5)(x)
x = keras.layers.Dense(nb_classes, activation="softmax")(x)

model = keras.models.Model(inputs=model.input, outputs=x)

model.summary()

model.compile(loss='categorical_crossentropy',
              metrics=['accuracy'])



trainGenerator = trainset.flow_from_directory(
        path,
        target_size=(224, 224),
        subset = 'training',
        class_mode="categorical",
        batch_size=batchSize)

validationGenerator = trainset.flow_from_directory(
        path,
        target_size=(224, 224),
        subset='validation',
        class_mode="categorical",
        batch_size=batchSize)

model.fit(
        trainGenerator,
        epochs=epochs,
        validation_data=validationGenerator,
)

score = model.evaluate(validationGenerator)
model.save(f'h5/{name}_{nb_classes}_{epochs}_{batchSize}_{int(score[1]*100)}.h5')




