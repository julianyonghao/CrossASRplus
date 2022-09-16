import random
import numpy as np
import json 
import os, subprocess
import gc
import torch
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer


import soundfile as sf
import torch
import requests
import time

from gtts import gTTS

from crossasr.textmodi import TextModi
from tts.rv import ResponsiveVoice
from tts.google import Google
from tts.espeak import Espeak
from tts.festival import Festival

from asr.deepspeech import DeepSpeech
from asr.deepspeech2 import DeepSpeech2
from asr.wav2letter import Wav2Letter
from asr.wit import Wit
from asr.wav2vec2 import Wav2Vec2

from estimator.huggingface import HuggingFaceTransformer

from pool import asr_pool, tts_pool
from crossasr.text import Text

from wit import Wit as WitAPI

import nemo.collections.asr as nemo_asr

WIT_ACCESS_TOKEN = os.getenv("WIT_ACCESS_TOKEN")
wit_client = WitAPI("CNNRVCTEC667JGLJGFYHR2PL67HBNUQD")

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
        if k != "tts" and k!= "asrs" and k != "estimator":
            conf[k] = v
    return conf


def googleGenerateAudio(text, audio_fpath):
    tempfile = audio_fpath.split(".")[0] + "-temp.mp3"
    googleTTS = gTTS(text, lang='en-us')
    googleTTS.save(tempfile)
    setting = " -acodec pcm_s16le -ac 1 -ar 16000 "
    os.system(f"ffmpeg -i {tempfile} {setting} {audio_fpath} -y")

def rvGenerateAudio(text, audio_fpath):
    tempfile = audio_fpath.split(".")[0] + "-temp.mp3"
    cmd = "rvtts --voice english_us_male --text \"" + text + "\" -o " + tempfile
    os.system(cmd)
    setting = " -acodec pcm_s16le -ac 1 -ar 16000 "
    os.system(f"ffmpeg -i {tempfile} {setting} {audio_fpath} -y")

def festivalGenerateAudio(text:str, audio_fpath:str):
    cmd = "festival -b \"(utt.save.wave (SayText \\\"" + \
        text + "\\\") \\\"" + audio_fpath + "\\\" 'riff)\""
    os.system(cmd)

def espeakGenerateAudio(text, audio_fpath) :
    tempfile = audio_fpath.split(".")[0] + "-temp.wav"
    cmd = "espeak \"" + text + "\" --stdout > " + tempfile
    os.system(cmd)
    setting = " -acodec pcm_s16le -ac 1 -ar 16000 "
    os.system(f"ffmpeg -i {tempfile} {setting} {audio_fpath} -y")

def getCCVoice(file_name, audio_fpath):
    raise NotImplementedError

def deepspeechRecognizeAudio(audio_fpath):
    cmd = "deepspeech --model asr_models/deepspeech/deepspeech-0.9.3-models.pbmm --scorer asr_models/deepspeech/deepspeech-0.9.3-models.scorer --audio " + audio_fpath

    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()

    transcription = out.decode("utf-8")[:-1]
    
    # print("DeepSpeech transcription: %s" % transcription)
    return transcription


def deepspeech2RecognizeAudio(audio_fpath) :
    cmd = "docker exec -it deepspeech2 curl http://localhost:5000/transcribe?fpath=" + audio_fpath

    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    transcription = out.decode("utf-8").split("\n")[-2]
    transcription = transcription[:-1]

    # print("DeepSpeech2 transcription: %s" % transcription)
    return transcription

def wav2letterRecognizeAudio(audio_fpath):
    cmd = "docker exec -it wav2letter sh -c \"cat /root/host/" + audio_fpath + \
        " | /root/wav2letter/build/inference/inference/examples/simple_streaming_asr_example --input_files_base_path /root/host/models/wav2letter/\""

    proc = subprocess.Popen([cmd],
                            stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()

    # print(out)
    transcription = concatWav2letterTranscription(out)

    # print(f"Wav2letter transcription: {transcription}")
    return transcription

def concatWav2letterTranscription(out):
    lines = out.splitlines()[21:-2]
    transcription = ""

    for line in lines:
        line = line.decode()
        part = line.split(",")[-1]
        if part != "":
            transcription += part

    transcription = transcription[:-1]

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

def witRecognizeAudio(audio_fpath):
    transcription = ""
    with open(audio_fpath, 'rb') as audio:
        try:
            wit_transcription = wit_client.speech(
                audio, {'Content-Type': 'audio/wav'})

            if wit_transcription != None:
                if "text" in wit_transcription:
                    transcription = str(wit_transcription["text"])
        except Exception:
            # print("Could not request results from Wit.ai service; {0}".format(e))
            transcription = ""

    # print(f"Wit transcription: {transcription}")
    return transcription

def nemoRecognizeAudio(audio_fpath):
    asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained("nvidia/stt_en_conformer_ctc_large")
    # asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained("stt_en_citrinet_512")
    transcription = asr_model.transcribe([audio_fpath])
    return transcription[0]

# 7/9 - ziqian added a new asr (AssemblyAI)
def assembly_read_file(audio_fpath, chunk_size=5242880):
    with open(audio_fpath, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data

def assemblyRecognizeAudio(audio_fpath):
    headers = {'authorization': "b66e701008d14dc18845619b5cdf4ba1"}
    response = requests.post('https://api.assemblyai.com/v2/upload',headers=headers,data=assembly_read_file(audio_fpath))

    temp = response.json().get("upload_url")
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {"audio_url": str(temp)}
    headers = {
        "authorization": "b66e701008d14dc18845619b5cdf4ba1",
        "content-type": "application/json"
    }
    response = requests.post(endpoint, json=json, headers=headers)

    status = response.json().get("status")
    # retrieve results
    while status != "completed":
        time.sleep(10)
        transcription_id = response.json().get("id")
        endpoint = "https://api.assemblyai.com/v2/transcript/" + str(transcription_id)
        headers = {
            "authorization": "b66e701008d14dc18845619b5cdf4ba1",
        }
        response = requests.get(endpoint, headers=headers)
        status = response.json().get("status")

    print("..............output text hereeeee")
    print(response.json().get("text"))
    return response.json().get("text")


def create_huggingface_estimator_by_name(name: str):
    # https://huggingface.co/transformers/custom_datasets.html
    return HuggingFaceTransformer(name=name)

def create_tts_by_name(name: str):
    return getTTS(name)


def create_asr_by_name(name: str):
    return getASR(name)


