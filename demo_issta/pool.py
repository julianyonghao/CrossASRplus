
from tts.espeak import Espeak
from tts.casual import Casual


from asr.deepspeech import DeepSpeech
from asr.vosk import Vosk
from asr.wav2vec2 import Wav2Vec2

tts_pool = [Espeak(), Casual()]
asr_pool = [Wav2Vec2(), Vosk()]
