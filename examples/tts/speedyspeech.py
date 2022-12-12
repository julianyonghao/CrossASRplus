import os
from crossasr.tts import TTS
import utils

#source: https://tts.readthedocs.io/en/latest/inference.html

class Speedyspeech(TTS):

    def __init__(self, name="speedyspeech"):
        TTS.__init__(self, name=name)

    def generateAudio(self, text: str, audio_fpath: str):
        utils.speedyspeechGenerateAudio(text, audio_fpath)