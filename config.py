import logging
import os
import tensorflow


debug = True
version = "0.0.2-POC"
port = 5000
indexer_port = 5001
product_h_file = "data/data.h.pickle"
product_data_file = "data/data.txt"
tf_use = "hubmodule/universal-sentence-encoder.4"
#tf_use = "hubmodule/universal-sentence-encoder-multilingual-large_3"
tf_fv = "hubmodule/feature-vector.4"
product_thresold = 0.5
take_ratio = 4
logging.basicConfig(filename=None, level=logging.INFO)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
model = "tensorflow.keras.applications.mobilenet_v2.MobileNetV2"
model = "tensorflow.keras.applications.resnet_v2.ResNet152V2"