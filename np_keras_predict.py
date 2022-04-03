import numpy as np
import tensorflow.keras as keras
import tensorflow as tf
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
tf.random.set_seed(0)

dir = ["02-Chauffage_PAC", "Entrees_Air_Bouches", "04-Ventilation_Double_Flux_Individuelle_Purification_Air",
       "05-Ventilation_Simple_Flux_Individuelle_Purification_Air", "06-Ventilation_Simple_Flux_Centralisee",
       "07-Centrales_Traitement_Air", "08-Desenfumage_Compartimentage", "09-Reseaux",
       "10-Reglages_Regulation_Debit_Mesure", "11-Diffusion_Air", "12-Aspiration_Centralisee",
       "13-Mesure_Connectivite"]

model = keras.models.load_model("h5/resnet152v2_12_50_4_61.h5")
img = keras.preprocessing.image.load_img("tests/images/aldes_cyril2.jpg", target_size=(224, 224))
img = keras.preprocessing.image.img_to_array(img)
img *= 1. / 255
img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
res = model.predict(img)[0] # image 0, output 0
print(np.argmax(res), res[np.argmax(res)])
print(dir[np.argmax(res)])