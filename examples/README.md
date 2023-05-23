# Empirical Study on the False Alarms in Automated Speech Recognition Testing

# Getting Started
## 1. WSL Installation (Windows)
1.1 Open Start on Windows > Search "Turn Windows features on or off"

1.2 Check "Virtual Machine Platform" and "Windows Subsystem for Linux"

1.3 Open command prompt and run

```wsl --update```

```wsl.exe --install Ubuntu-20.04```

## 2. Clone the Repository
2.1 Clone the repository to your WSL home directory e.g. \\wsl.localhost\Ubuntu-20.04\home\fit\CrossASRplus
2.2 Checkout to ****branch name

## 3. Open the Project on Your IDE
3.1 Create a new WSL terminal
3.2 Change your directory to the 'examples' directory

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
pip install pydub
pip install transformers
sudo apt install ffmpeg #exceute sudo apt update if you encounter a Not Found error
sudo apt-get -y install sox
```

**In this project we have modified code in the crossasr package.**
**Therefore, you will need to manually copy the 'crossasr' directory and their contents in the repository.**
**And overwrite the 'crossasr' directory in your WSL python package directory: \\wsl.localhost\Ubuntu-20.04\home\fit\env\lib\python3.8\site-packages\crossasr**


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
### 5.3. Festival
[Festival](http://www.cstr.ed.ac.uk/projects/festival/)

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

[DeepSpeech](https://github.com/mozilla/DeepSpeech)

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

### 6.2. Deepspeech2

[DeepSpeech2](https://github.com/PaddlePaddle/DeepSpeech)

#### Setup a docker container for Deepspeech2

[Original Source](https://github.com/PaddlePaddle/DeepSpeech#running-in-docker-container)

```bash
cd asr_models/
git clone https://github.com/PaddlePaddle/DeepSpeech.git
cd DeepSpeech
git checkout tags/v1.1
cp ../../asr/deepspeech2_api.py .
cd models/librispeech/
sh download_model.sh
cd ../../../../
cd asr_models/DeepSpeech/models/lm
sh download_lm_en.sh
cd ../../../../
docker pull perhoong/crossasr:deepspeech2

# run this command from examples folder
# please remove --gpus '"device=0"' if you only have one gpu
docker run --name deepspeech2 --rm --gpus '"device=0"' -it -v $(pwd)/asr_models/DeepSpeech:/DeepSpeech -v $(pwd)/output/:/DeepSpeech/output/  perhoong/crossasr:deepspeech2 /bin/bash

``` 

#### Run Deepspeech2 as an API (inside docker container)
```bash
pip install flask 

# run inside /DeepSpeech folder in the container
CUDA_VISIBLE_DEVICES=0 python deepspeech2_api.py \
    --mean_std_path='models/librispeech/mean_std.npz' \
    --vocab_path='models/librispeech/vocab.txt' \
    --model_path='models/librispeech' \
    --lang_model_path='models/lm/common_crawl_00.prune01111.trie.klm'
```
Then detach from the docker using ctrl+p & ctrl+q after you see `Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`

#### Run Client from the Terminal (outside docker container)

```bash
# run from examples folder in the host machine (outside docker)
docker exec -it deepspeech2 curl http://localhost:5000/transcribe?fpath=output/audio/google/hello.wav
```

### 6.3. Vosk

```pip3 install vosk```

### 6.4. Wav2letter++

[wav2letter++](https://github.com/facebookresearch/wav2letter)

Please find the lastest image of [wav2letter's docker](https://hub.docker.com/r/wav2letter/wav2letter/tags).

```bash
cd asr_models/
mkdir wav2letter
cd wav2letter

for f in acoustic_model.bin tds_streaming.arch decoder_options.json feature_extractor.bin language_model.bin lexicon.txt tokens.txt ; do wget http://dl.fbaipublicfiles.com/wav2letter/inference/examples/model/${f} ; done

ls -sh
cd ../../
```

#### Run docker inference API
```bash
# run from examples folder
docker run --name wav2letter -it --rm -v $(pwd)/output/:/root/host/output/ -v $(pwd)/asr_models/:/root/host/models/ --ipc=host -a stdin -a stdout -a stderr wav2letter/wav2letter:inference-latest
```
Then detach from the docker using ctrl+p & ctrl+q 

#### Run Client from the Terminal

```bash
docker exec -it wav2letter sh -c "cat /root/host/output/audio/google/hello.wav | /root/wav2letter/build/inference/inference/examples/simple_streaming_asr_example --input_files_base_path /root/host/models/wav2letter/"
```

Detail of [wav2letter++ installation](https://github.com/facebookresearch/wav2letter/wiki#Installation) and [wav2letter++ inference](https://github.com/facebookresearch/wav2letter/wiki/Inference-Run-Examples)


## 7. Running a Small Example
We have included a small subset of data from the LJ Dataset in the 'casual_data_demo' directory.
To run the example experiment, please ensure that you are currently on the 'examples' directory. If not run:

```cd examples```

To start the experiment, execute the following command:

```python test_asr.py config_corpus.json```

The config_corpus.json file describes the current experiment configurations like the ASR systems and TTS systems used, the target ASR, the directory for the dataset, output directory, etc.

The results of this experiment is located in the 'output/casual_lj_demo_espeak_vosk' directory for this experiment.
In the 'results' directory contains a .xlsx file and a .json file which describes the false alarm cases, WER, the number of false alarms and the number of executed cases per iteration.

## 8. False Alarm Predictor
We use [Anaconda](https://www.anaconda.com/download) a tool to manage packages and environments to train the False Alarm Predictor.

A environment configuration file (tf_cpu_38.yaml) is included in the 'false_alarm_predictor' directory.

Please import the environment configuration file to Anaconda in order to set up and install the required packages.

The files used to train the predictor model is included under the 'training_files' directory.

A Jupyter Notebook file named 'False_Alarm_Predictor_LJ_Libri.ipynb' describes the steps and code in training and evaluating the predictor model.


