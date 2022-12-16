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
    asr = utils.getASRS(config["asr"])
    target_asr = utils.getASR(config["target_asr"])
    
    crossasr = CrossASRmodi(tts=tts, asr=asr, output_dir=config["output_dir"], recompute=True, target_asr = target_asr, audio_type=config["audio_type"])

    cc_filename = "LJ001-0001"

    # casual_dir = os.path.join(CASUAL_DIR, cc_audio_type)
    casual_dir = os.path.join("casual_data/Casual_Data_LJ/")
    fpath = os.path.join(casual_dir, "transcription", cc_filename + ".txt")
    casual_audio_dir = os.path.join(casual_dir, "audio")
    file = open(fpath, "r")
    text = file.readlines()[0]
    file.close()

    cases = crossasr.processText(text=text, filename=cc_filename, cc_dir=casual_audio_dir)
    print(cases)
    # crossasr.printResult(text=text, filename=cc_filename)

