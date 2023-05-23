import utils

if __name__ == "__main__":
    transcription = utils.nemoRecognizeAudio("output/audio/google/hello.wav")
    print(transcription)