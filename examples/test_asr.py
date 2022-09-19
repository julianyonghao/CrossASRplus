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
    asr = utils.getASRS(config["asrs"])
    target_asr = utils.getASR(config["target_asr"])
    estimator = utils.getEstimator(config["estimator"])

    # file = open(os.path.join("/mnt/f/casual_data/Casual_Data_LJ/transcription/", "LJ001-0001.txt"))
    # text = file.readlines()
    # print(text)
    crossasr = CrossASRmodi(tts=tts, asr=asr, estimator=estimator, target_asr=target_asr, **utils.parseConfig(config))

    corpus_fpath = os.path.join(config["corpus_fpath"], "transcription")
    texts = utils.readDirAsCorpus(corpus_fpath=corpus_fpath)
    crossasr.processCorpus(texts=texts)
    # crossasr.printStatistic()


    
