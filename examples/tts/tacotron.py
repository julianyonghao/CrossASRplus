import os
from crossasr.tts import TTS
import utils

class Tacotron(TTS):

    def __init__(self, name="tacotron"):
        TTS.__init__(self, name=name)

    def generateAudio(self, text: str, audio_fpath: str):
        utils.tacotronGenerateAudio(text, audio_fpath)