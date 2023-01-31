import os
from crossasr.tts import TTS
import utils

class GlowTTS(TTS):

    def __init__(self, name="glowtts"):
        TTS.__init__(self, name=name)

    def generateAudio(self, text: str, audio_fpath: str):
        utils.glowttsGenerateAudio(text, audio_fpath)