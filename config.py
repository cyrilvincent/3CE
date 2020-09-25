import logging
import os

debug = True
version = "POC 0.1"
port = 5000
indexer_port = 5001
h_file = "data/data.h.pickle"
data_file = "data/data.txt"
use = "hubmodule/universal-sentence-encoder.4"
#use = "hubmodule/universal-sentence-encoder-multilingual-large_3"
score_thresold = 0.4 #0.6 for 100k
take_ratio = 4 #2 for 100k
logging.basicConfig(filename=None, level=logging.INFO)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"