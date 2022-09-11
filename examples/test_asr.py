import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

import os, sys
from crossasr.crossasrmodi import CrossASRmodi
import json
import utils

if __name__ == "__main__":

    config = utils.readJson(sys.argv[1]) # read json configuration file

    tts = utils.getTTSS(config["tts"])
    asrs = utils.getASRS(config["asrs"])
    estimator = utils.getEstimator(config["estimator"])

    # Initialize CrossASR class with parameters listed config_corpus.json
    crossasr = CrossASRmodi(tts=tts, asrs=asrs, estimator=estimator, **utils.parseConfig(config))

    # Read path to corpus
    texts = utils.readDirAsCorpus(corpus_fpath=config["corpus_fpath"])
    # print(texts[0].getText())

    # Process corpus as test cases
    crossasr.processCorpus(texts=texts)
    # crossasr.printStatistic()


    
