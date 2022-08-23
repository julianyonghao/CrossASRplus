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

    crossasr = CrossASRmodi(tts=tts, asrs=asrs, estimator=estimator, **utils.parseConfig(config))
    #
    # corpus_fpath = os.path.join(config["output_dir"], config["corpus_fpath"])
    texts = utils.readDirAsCorpus(corpus_fpath=config["corpus_fpath"])
    # print(texts[0].getText())
    crossasr.processCorpus(texts=texts)
    # crossasr.printStatistic()


    
