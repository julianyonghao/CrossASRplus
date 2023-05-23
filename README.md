# Empirical Study on the False Alarms in Automated Speech Recognition Testing

## Getting Started
Navigate to the ```demo_issta``` directory for instructions in running a minimal version of the experiment

## Detail Instructions

### 1. Results
We ran our experiment on both the LJ Speech Dataset and the LibriSpeech Dataset for all combinations of 5 ASR and 4 TTS systems.

As a result, there are 40 sets of results.

Results for each run are grouped based on their dataset and are stored in our Google Drive folder:

- [LJ Speech Dataset Results](https://drive.google.com/drive/folders/1zdbpgHO-0kNU3PfFrvTE4kUDKgEX9XgF?usp=share_link)
- [LibriSpeech Dataset Results](https://drive.google.com/drive/folders/12lUsYHC7K_mhn1TH5Y7hRnPcSNLkH8C-?usp=share_link)


### 2. False Alarm Predictor
We use [Anaconda](https://www.anaconda.com/download) a tool to manage packages and environments.

A environment configuration file (tf_cpu_38.yaml) is included in the 'false_alarm_predictor' directory.

Please import the environment configuration file to Anaconda in order to set up and install the required packages.

The files used to train the predictor model is included under the 'training_files' directory.

Additionally, a Jupyter Notebook file named 'False_Alarm_Predictor_LJ_Libri.ipynb' describes the steps and code in training and evaluating the predictor model.