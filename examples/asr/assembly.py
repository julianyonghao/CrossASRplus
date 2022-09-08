from crossasr.asr import ASR
import utils

class Assembly(ASR):
    def __init__(self, name="assembly"):
        ASR.__init__(self, name=name)

    def recognizeAudio(self, audio_fpath: str) -> str:
        #utils.assemblyRecognizeAudio(audio_fpath)
        transcription = utils.assemblyRecognizeAudio(audio_fpath)
        return transcription

