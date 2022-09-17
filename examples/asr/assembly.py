from crossasr.asr import ASR

from constant import ASSEMBLY_TOKEN
import utils

class Assembly(ASR):
    def __init__(self, name="assembly"):
        ASR.__init__(self, name=name)

    def recognizeAudio(self, audio_fpath: str) -> str:
        transcription = utils.assemblyRecognizeAudio(audio_fpath, ASSEMBLY_TOKEN)
        return transcription

