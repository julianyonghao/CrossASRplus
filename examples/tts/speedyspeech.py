import os
from crossasr.tts import TTS
import utils

#source: https://tts.readthedocs.io/en/latest/inference.html
# use this version of pytorch pyaudio: pip install torch==1.10.0+cu113 torchaudio==0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html

class Speedyspeech(TTS):

    def __init__(self, name="speedyspeech"):
        TTS.__init__(self, name=name)

    def generateAudio(self, text: str, audio_fpath: str):
        utils.speedyspeechGenerateAudio(text, audio_fpath)