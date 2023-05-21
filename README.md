# Empirical Study on the False Alarms in Automated Speech Recognition Testing
This repository is a code implementation for the paper ["Synthesizing Speech Test Cases with Text-To-Speech? An Empirical Study on the False Alarms in Automated Speech Recognition Testing"](https://rb.gy/r03ui). Our study investigates false alarm occurences in the usage of Text-To-Speech (TTS) systems to automatically synthesise speech test cases on Automated Speech Recognition (ASR) systems. To do so, we propose augmenting [CrossASR](https://github.com/soarsmu/CrossASRplus) with a false alarm predictor to help developers identify false alarms efficiently.

Developers need to perform adequate testing to ensure the quality of Automatic Speech Recognition (ASR) systems. However, manually collecting required test cases is tedious and time-consuming. Our recent work proposes, namely [CrossASR](https://github.com/soarsmu/CrossASR), a differential testing method for ASR systems. This method first utilizes Text-to-Speech (TTS) to generate audios from texts automatically and then feed these audios into different ASR systems for cross-referencing to uncover failed test cases. It also leverages a failure estimator to find test cases more efficiently. Such a method is inherently self-improvable: the performance can increase by leveraging more advanced TTS and ASR systems. 

So in this accompanying tool, we devote more engineering and propose **CrossASR++, an easy-to-use ASR testing tool that can be conveniently extended to incorporate different TTS and ASR systems and failure estimators**. We also make CrossASR++ chunk texts dynamically and enable the estimator to work in a more efficient and flexible way. We demonstrate that the new features can help CrossASR++ discover more failed test cases.

Please check our Tool Demo Video at [https://www.youtube.com/watch?v=ddRk-f0QV-g](https://www.youtube.com/watch?v=ddRk-f0QV-g)

PDF preprint is [available](https://mhilmiasyrofi.github.io/papers/CrossASRv2.pdf)

## 1. WSL Installation (Windows)
1.1 Open Start on Windows > Search "Turn Windows features on or off"
1.2 Check "Virtual Machine Platform" and "Windows Subsystem for Linux"
1.3 Open command prompt
```wsl --update```
```wsl.exe --install Ubuntu-20.04```

## 2. Clone the Repository
Checkout to ****branch name

## 3. Open a new WSL Terminal on Your IDE
```cd examples```

## 4. On the 'examples' directory, execute the following commands to set up

### 4.1. Install the Python development environment

```bash
sudo apt update
sudo apt install python3-dev python3-pip python3-venv
```

### 4.2. Create a virtual environment

Create a new virtual environment by choosing a Python interpreter and making a ./env directory to hold it:

```bash
python3 -m venv --system-site-packages ~/./env
```

Activate the virtual environment using a shell-specific command:

```bash
source ~/./env/bin/activate  # sh, bash, or zsh
pip install crossasr
bash install_requirement.sh
```

### Preparation

Make a folder to save the output

```bash
if [ ! -d "output/" ]
then
    mkdir output/
fi

if [ ! -d "output/audio/" ]
then
    mkdir output/audio/
fi
```

## 5. Prepare TTSes

### 5.1. Google
We use [gTTS](https://pypi.org/project/gTTS/) (Google Text-to-Speech), a Python library and CLI tool to interface with Google Translate text-to-speech API.

```bash
pip install gTTS
```

#### Trial
```bash
mkdir output/audio/google/
gtts-cli 'hello world google' --output output/audio/google/hello.mp3
ffmpeg -i output/audio/google/hello.mp3  -acodec pcm_s16le -ac 1 -ar 16000 output/audio/google/hello.wav -y
```

### 5.2. Espeak

[eSpeak](http://espeak.sourceforge.net/) is a compact open source software speech synthesizer for English and other languages.

```bash
sudo apt install espeak -y

mkdir output/audio/espeak/
espeak "hello e speak" --stdout > output/audio/espeak/hello.riff
ffmpeg -i output/audio/espeak/hello.riff  -acodec pcm_s16le -ac 1 -ar 16000 output/audio/espeak/hello.wav -y
```
### 5.3. Festival
[Festival](http://www.cstr.ed.ac.uk/projects/festival/) is a free TTS written in C++. It is developed by The Centre for Speech Technology Research at the University of Edinburgh. Festival are distributed under an X11-type licence allowing unrestricted commercial and non-commercial use alike. Festival is a command-line program that already installed on Ubuntu 16.04.

#### Trial
```bash
sudo apt install festival -y
mkdir output/audio/festival/
festival -b "(utt.save.wave (SayText \"hello festival \") \"output/audio/festival/hello.wav\" 'riff)"
```

### 5.4. GlowTTS

```bash
pip install TTS
```

## 6. Prepare ASRs

### 6.1. Deepspeech

[DeepSpeech](https://github.com/mozilla/DeepSpeech) is an open source Speech-To-Text engine, using a model trained by machine learning techniques based on [Baidu's Deep Speech research paper](https://arxiv.org/abs/1412.5567). **CrossASR++ uses [Deepspeech-0.9.3](https://github.com/mozilla/DeepSpeech/releases/tag/v0.9.3)**

```bash
pip install deepspeech===0.9.3

if [ ! -d "asr_models/" ]
then 
    mkdir asr_models
fi

cd asr_models
mkdir deepspeech
cd deepspeech 
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer
cd ../../
```

Please follow [this link for more detailed installation](https://github.com/mozilla/DeepSpeech/tree/v0.9.3).

#### Trial
```bash
deepspeech --model asr_models/deepspeech/deepspeech-0.9.3-models.pbmm --scorer asr_models/deepspeech/deepspeech-0.9.3-models.scorer --audio output/audio/google/hello.wav
```

