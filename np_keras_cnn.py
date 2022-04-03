import tensorflow.keras as keras
import tensorflow as tf
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
tf.random.set_seed(0)
path = "images/catalogues_aldes/ai2"

batchSize = 1
epochs = 20
nb_classes = 12

def Chollet():
    model = keras.models.Sequential()
    model._name = "chollet"
    model.add(keras.layers.Conv2D(32, (3, 3), input_shape=(150, 150, 3)))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

    # 64, 64, 32

    model.add(keras.layers.Conv2D(32, (3, 3)))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    # 32, 32, 32

    model.add(keras.layers.Conv2D(64, (3, 3)))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    # 16, 16, 64

    # Dense
    model.add(keras.layers.Flatten())
    # 4096
    model.add(keras.layers.Dense(64))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(nb_classes))
    model.add(keras.layers.Activation('softmax'))
    return model, 150

def Cyril():
    model = keras.models.Sequential()
    model._name = "cyril"
    model.add(keras.layers.Conv2D(32, (3, 3), input_shape=(224, 224, 3), padding="same"))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    # 112, 112, 32

    model.add(keras.layers.Conv2D(64, (3, 3)))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    # 56, 56, 64

    model.add(keras.layers.Conv2D(128, (3, 3)))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    # 28, 28, 128

    model.add(keras.layers.Conv2D(128, (3, 3)))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    # 14, 14, 128

    # Dense
    model.add(keras.layers.Flatten())
    # 25088
    model.add(keras.layers.Dense(512))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(256))
    model.add(keras.layers.Activation('relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(nb_classes))
    model.add(keras.layers.Activation('softmax'))
    return model, 224

model, target_size = Chollet()
name = model.name


trainset = keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255,
                                                        rotation_range=20,
                                                        # width_shift_range=0.05,
                                                        # height_shift_range=0.05,
                                                        # brightness_range=(0.8, 1.2),
                                                        shear_range=0.2,
                                                        zoom_range=0.1,
                                                        validation_split=0.2)

model.summary()

model.compile(loss='categorical_crossentropy',
              metrics=['accuracy'])

trainGenerator = trainset.flow_from_directory(
        path,
        target_size=(target_size, target_size),
        subset = 'training',
        class_mode="categorical",
        batch_size=batchSize)

validationGenerator = trainset.flow_from_directory(
        path,
        target_size=(target_size, target_size),
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




