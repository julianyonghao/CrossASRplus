from crossasr.asr import ASR

import utils

class Pocket(ASR):

    def __init__(self, name="pocket"):
        self.name = name

    def recognizeAudio(self, audio_fpath: str) -> str:
        return utils.pocketRecognizeAudio(audio_fpath)
