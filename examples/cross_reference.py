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
    asr = utils.getASR(config["asr"])
    
    crossasr = CrossASRmodi(tts=tts, asr=asr, output_dir=config["output_dir"], recompute=True)

    cc_filename = "LJ001-0001"

    # casual_dir = os.path.join(CASUAL_DIR, cc_audio_type)
    casual_dir = os.path.join(CASUAL_DIR, "Casual_Data_LJ")
    fpath = os.path.join(casual_dir, "transcription", cc_filename + ".txt")
    audio_fpath = os.path.join(casual_dir, "audio")
    file = open(fpath, "r")
    text = file.readlines()[0]
    file.close()

    cases, execution_time = crossasr.processText(text=text, filename=cc_filename, cc_dir=audio_fpath)
    crossasr.printResult(text=text, filename=cc_filename)

