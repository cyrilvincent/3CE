import logging
import os

debug = True
version = "1.0.0-DEV"
port = 5000
indexer_port = 5001
pool = ["data"]
product_h_file = "data/{instance}.h.pickle"
product_data_file = "data/{instance}.txt"
tf_use = "hubmodule/universal-sentence-encoder.4"
#tf_use = "hubmodule/universal-sentence-encoder-multilingual-large_3"
tf_fv = "hubmodule/feature-vector.4"
product_thresold = 0.5
image_thresold = 0.75
logging.basicConfig(filename=None, level=logging.INFO)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"