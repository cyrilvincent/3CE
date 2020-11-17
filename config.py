import logging
import os

debug = True
version = "0.0.2-POC"
port = 5000
indexer_port = 5001
h_file = "data/data.h.pickle"
data_file = "data/data.txt"
use = "hubmodule/universal-sentence-encoder.4"
#use = "hubmodule/universal-sentence-encoder-multilingual-large_3"
score_thresold = 0.4
take_ratio = 4
logging.basicConfig(filename=None, level=logging.INFO)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"