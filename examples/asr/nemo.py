from crossasr.asr import ASR

import utils

class Nemo(ASR):

    def __init__(self, name="nemo"):
        self.name = name

    def recognizeAudio(self, audio_fpath: str) -> str:
        return utils.nemoRecognizeAudio(audio_fpath)
