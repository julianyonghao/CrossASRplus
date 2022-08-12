import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

import sys
import utils
import os

from crossasr.crossasrmodi import CrossASRmodi

from crossasr.constant import CASUAL_DIR

if __name__ == "__main__":
    
    config = utils.readJson(sys.argv[1]) # read json configuration file

    tts = utils.getTTSS(config["tts"])
    asrs = utils.getASRS(config["asrs"])
    
    crossasr = CrossASRmodi(tts=tts, asrs=asrs, output_dir=config["output_dir"], recompute=True)

    cc_filename = "1140_00"
    filename = "1140_00"

    casual_dir = os.path.join(CASUAL_DIR, cc_filename)
    fpath = os.path.join(casual_dir, cc_filename + ".txt")
    file = open(fpath, "r")
    text = file.readlines()[0]
    file.close()

    crossasr.processText(text=text, filename=filename, cc_filename=cc_filename)
    crossasr.printResult(text=text, filename=filename)
