import random
import numpy as np
import json 
import os, subprocess
import gc
import torch
from pydub import AudioSegment
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import torch
import requests
import time
# from wit import Wit as WitAPI
# import nemo.collections.asr as nemo_asr

from pool import asr_pool, tts_pool

from tts.espeak import Espeak

from asr.deepspeech import DeepSpeech

from crossasr.text import Text
from crossasr.textmodi import TextModi

from estimator.huggingface import HuggingFaceTransformer

# from pocketsphinx import Decoder
import wave


WIT_ACCESS_TOKEN = os.getenv("WIT_ACCESS_TOKEN")

tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")


def getTTS(tts_name: str):
    for tts in tts_pool :
        if tts_name == tts.getName() :
            return tts
    raise NotImplementedError("There is a TTS name problem")

def getTTSS(tts_names):
    ttss = []
    for tts in tts_pool:
        for tts_name in tts_names :
            if tts_name == tts.getName():
                ttss.append(tts)
    if len(tts_names) == len(ttss) :
        return ttss
    raise NotImplementedError("There is an TTS name problem")


def getASR(asr_name: str):
    for asr in asr_pool:
        if asr_name == asr.getName():
            return asr
    raise NotImplementedError("There is a ASR name problem")


def getASRS(asr_names):
    asrs = []
    for asr in asr_pool:
        for asr_name in asr_names :
            if asr_name == asr.getName():
                asrs.append(asr)
    if len(asr_names) == len(asrs) :
        return asrs
    raise NotImplementedError("There is an ASR name problem")

def getEstimator(name: str):
    return HuggingFaceTransformer(name=name)

def set_seed(seed: int) :
    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def readJson(config_path: str):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def readCorpus(corpus_fpath: str) :
    file = open(corpus_fpath)
    corpus = file.readlines()
    texts = []
    i = 1
    for text in corpus:
        texts.append(Text(i, text[:-1]))
        i += 1
    return texts

def readDirAsCorpus(corpus_fpath: str) :
    texts = []
    for subdir, dirs, files in os.walk(corpus_fpath):
        for ori_file in files:
            try:
                file = open(os.path.join(corpus_fpath, ori_file))
                text = file.readlines()
                texts.append(TextModi(ori_file.split(".")[0], text[0]))
            except:
                continue
    return texts
    
def parseConfig(config):
    conf = {}
    for k,v in config.items() :
        if k != "tts" and k!= "asr" and k != "estimator" and k != "target_asr":
            conf[k] = v
    return conf


def espeakGenerateAudio(text, audio_fpath) :
    tempfile = audio_fpath.split(".")[0] + "-temp.wav"
    cmd = "espeak \"" + text + "\" --stdout > " + tempfile
    os.system(cmd)
    setting = " -acodec pcm_s16le -ac 1 -ar 16000 "
    os.system(f"ffmpeg -i {tempfile} {setting} {audio_fpath} -y")


def deepspeechRecognizeAudio(audio_fpath):
    cmd = "deepspeech --model asr_models/deepspeech/deepspeech-0.9.3-models.pbmm --scorer asr_models/deepspeech/deepspeech-0.9.3-models.scorer --audio " + audio_fpath

    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()

    transcription = out.decode("utf-8")[:-1]
    
    # print("DeepSpeech transcription: %s" % transcription)
    return transcription



def wav2vec2RecognizeAudio(audio_fpath) :
    audio_input, _ = sf.read(audio_fpath)

    # transcribe
    input_values = tokenizer(
        audio_input, return_tensors="pt").input_values
    # input_values = input_values.to(self.device)

    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = tokenizer.batch_decode(predicted_ids)[0]
    
    del audio_input, input_values, logits, predicted_ids
    torch.cuda.empty_cache()
    gc.collect()

    return transcription

def voskRecognizeAudio(audio_fpath):
    cmd = " vosk-transcriber -i " + audio_fpath

    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    transcription = out.decode("utf-8")[:-1]

    # print("DeepSpeech transcription: %s" % transcription)
    return transcription


def create_huggingface_estimator_by_name(name: str):
    # https://huggingface.co/transformers/custom_datasets.html
    return HuggingFaceTransformer(name=name)

def create_tts_by_name(name: str):
    return getTTS(name)


def create_asr_by_name(name: str):
    return getASR(name)


