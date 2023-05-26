# Empirical Study on the False Alarms in Automated Speech Recognition Testing
Text-To-Speech (TTS) systems have been suggested in recent studies as a means to generate speech test cases automatically, allowing for the identification of failures in Automatic Speech Recognition (ASR) systems on a large scale. However, the failures identified through test cases generated with TTS systems may not accurately the real-world performance of ASR systems when transcribing human speech. When presented with a failed test case synthesised from TTS systems, which consists of a synthetic audio and the corresponding ground truth text, we input the human audio reciting the same ground truth text into the ASR system for transcription. If the human audio can be correctly transcribed, a false alarm is detected. 


To investigate this, we explore the occurrences of false alarms in five popular ASR systems by testing the ASR systems ([Deepspeech](https://github.com/mozilla/DeepSpeech), [Deepspeech2](https://github.com/PaddlePaddle/PaddleSpeech), [Vosk](https://github.com/alphacep/vosk-api), [Wav2letter++](https://github.com/flashlight/wav2letter), [Wav2vec2](https://huggingface.co/docs/transformers/model_doc/wav2vec2)) with synthetic speech generated using four popular TTS systems ([Google](https://cloud.google.com/text-to-speech), [GlowTTS](https://github.com/jaywalnut310/glow-tts.git), [Festival](http://www.cstr.ed.ac.uk/projects/festival/), [Espeak](http://espeak.sourceforge.net)) and human audio of the same texts. The human audio and texts are from two popular datasets - LJ Speech Dataset and LibriSpeech Dataset. 

Additionally, We propose a false alarm predictor, based on Recurrent Neural Networks(RNN), that flags possible false alarms when ASR is tested with TTS-generated speech.

## Getting Started
Navigate to the ```demo_issta``` directory for instructions in running a minimal version of the experiment.

## Detailed Instructions

### 1. Experiment Results
We ran our experiment on both the LJ Speech Dataset and the LibriSpeech Dataset for all combinations of 5 ASR and 4 TTS systems.

As a result, there are 40 sets of results.

Results for each run are grouped based on their dataset and are stored in our Google Drive folder:

- [LJ Speech Dataset Results](https://drive.google.com/drive/folders/1zdbpgHO-0kNU3PfFrvTE4kUDKgEX9XgF?usp=share_link)
- [LibriSpeech Dataset Results](https://drive.google.com/drive/folders/12lUsYHC7K_mhn1TH5Y7hRnPcSNLkH8C-?usp=share_link)


### 2. False Alarm Predictor
We use [Anaconda](https://www.anaconda.com/download) a tool to manage packages and environments.

A environment configuration file ```tf_cpu_38.yaml``` is included in the ```false_alarm_predictor``` directory.

Please import the environment configuration file to Anaconda in order to set up and install the required packages.

The files used to train the predictor model is included under the ```training_files``` directory.

Additionally, a Jupyter Notebook file named ```False_Alarm_Predictor_LJ_Libri.ipynb``` describes the steps and code in training and evaluating the predictor model.