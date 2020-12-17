import logging
import os

debug = True
version = "1.1.0-DEV"
port = 5000
indexer_port = 5001
pool = ["chuv"]
product_h_file = "data/{instance}.h.pickle"
product_data_file = "data/{instance}.txt"
image_h_file = "data/{instance}-image.h.pickle"
image_data_file = "data/{instance}-image.txt"
tf_use = "hubmodule/universal-sentence-encoder.4"
#tf_use = "hubmodule/universal-sentence-encoder-multilingual-large_3"
tf_fv = "hubmodule/feature-vector.4"
product_thresold = 0.5
product_nn_thresold = 0.9
image_thresold = 0.82
image_nn_thresold = 0.92
use2_limit = 150000
product_nn_limit = 1000000
logging.basicConfig(filename=None, level=logging.INFO)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"