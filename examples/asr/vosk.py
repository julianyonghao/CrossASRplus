from crossasr.asr import ASR

import utils

class Vosk(ASR):

    def __init__(self, name="vosk"):
        self.name = name

    def recognizeAudio(self, audio_fpath: str) -> str:
        return utils.voskRecognizeAudio(audio_fpath)