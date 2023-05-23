# Empirical Study on the False Alarms in Automated Speech Recognition Testing

# Getting Started
## 1. WSL Installation (Windows)
1.1 Open Start on Windows > Search "Turn Windows features on or off"

1.2 Check "Virtual Machine Platform" and "Windows Subsystem for Linux"

1.3 Open command prompt and run

```wsl --update```

```wsl.exe --install Ubuntu-20.04```

## 2. Clone the Repository
2.1 Clone the repository to your WSL home directory e.g. ```\\wsl.localhost\Ubuntu-20.04\home\fit\FAinASRtest```

2.2 Checkout to ```main``` branch

## 3. Open the Project on Your IDE
3.1 Create a new WSL terminal

3.2 Change your directory to the ```demo_issta``` directory e.g ```cd demo_issta```

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
pip install pydub
pip install transformers
sudo apt install ffmpeg #exceute sudo apt update if you encounter a Not Found error
sudo apt-get -y install sox
```

**In this project we have modified code in the crossasr package.**

**Therefore, you will need to manually copy the 'crossasr' directory and their contents in the repository.**

**And overwrite the 'crossasr' directory in your WSL python package directory: ```\\wsl.localhost\Ubuntu-20.04\home\fit\env\lib\python3.8\site-packages\crossasr```**


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
[gTTS](https://pypi.org/project/gTTS/) (Google Text-to-Speech).

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

[eSpeak](http://espeak.sourceforge.net/).

```bash
sudo apt install espeak -y

mkdir output/audio/espeak/
espeak "hello e speak" --stdout > output/audio/espeak/hello.riff
ffmpeg -i output/audio/espeak/hello.riff  -acodec pcm_s16le -ac 1 -ar 16000 output/audio/espeak/hello.wav -y
```

## 6. Prepare ASRs

### 6.1. Vosk
[Vosk](https://alphacephei.com/vosk/)

```pip3 install vosk```


## 7. Running a Small Example
We have included a small subset of data from the LJ Dataset in the ```casual_data_demo``` directory.
To run the demo experiment, please ensure that you are currently on the ```demo_issta``` directory.

To start the experiment, execute the following command:

```python test_asr.py config_corpus.json```

The config_corpus.json file describes the current experiment configurations like the ASR systems and TTS systems used, the target ASR, the directory for the dataset, output directory, etc.

In this demo experiment, we use Espeak TTS, Wav2Vec2 ASR and Vosk ASR.

The results of this experiment is located in the ```output/casual_lj_demo_espeak_vosk``` directory for this experiment.
In the ```results``` directory contains a .xlsx file and a .json file which describes the false alarm cases, WER, the number of false alarms and the number of executed cases per iteration.


