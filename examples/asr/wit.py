from crossasr.asr import ASR

from constant import WIT_CLIENT_TOKEN
import utils

class Wit(ASR):

    def __init__(self, name="wit"):
        self.name = name

    def recognizeAudio(self, audio_fpath: str) -> str:
        return utils.witRecognizeAudio(audio_fpath, WIT_CLIENT_TOKEN)