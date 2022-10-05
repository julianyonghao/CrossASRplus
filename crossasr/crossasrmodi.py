from operator import is_
import os, time, random
import numpy as np
import json

import crossasr.constant
from crossasr.constant import INDETERMINABLE_TEST_CASE, SUCCESSFUL_TEST_CASE, FAILED_TEST_CASE,FALSE_ALARM_TEST_CASE
from crossasr.constant import DATA_DIR, EXECUTION_TIME_DIR, CASE_DIR, CASUAL_DIR
from crossasr.constant import AUDIO_DIR, TRANSCRIPTION_DIR

from crossasr.utils import preprocess_text
from crossasr.utils import make_dir, read_json, save_execution_time, get_execution_time
from crossasr.text import Text

from crossasr.tts import TTS
from crossasr.asr import ASR

from jiwer import wer
import xlsxwriter

# from evaluate import load
from crossasr.textmodi import TextModi


class CrossASRmodi:
    def __init__(self, tts: [TTS], asr: ASR, output_dir: "", recompute=False, num_iteration=5,
                 time_budget=3600, max_num_retry=0, text_batch_size=None, seed=None, estimator=None, audio_type="audio_raw", corpus_fpath=None):
        self.ttss = tts
        self.asr = asr
        self.target_asr = asr

        self.output_dir = output_dir
        self.casual_dir = corpus_fpath

        self.audio_dir = os.path.join(output_dir, DATA_DIR, AUDIO_DIR)
        self.transcription_dir = os.path.join(output_dir, DATA_DIR, TRANSCRIPTION_DIR)
        self.init_directory()

        ## TODO: make init directory for execution time and case
        self.execution_time_dir = os.path.join(output_dir, EXECUTION_TIME_DIR)
        self.case_dir = os.path.join(output_dir, CASE_DIR)
        self.recompute = recompute
        self.num_iteration = num_iteration
        self.time_budget = time_budget
        self.max_num_retry = max_num_retry
        self.text_batch_size = text_batch_size
        self.estimator = estimator
        self.outputfile_failed_test_case = self.get_outputfile_for_failed_test_case()
        self.outputfile_false_alarms = self.get_outputfile_for_false_alarms()

        # Zi Qian added this 23/8
        self.wer_temp = {}

        self.audio_type = audio_type

        if seed:
            crossasr.utils.set_seed(seed)

        ## TODO: convert print into global logging

    def init_directory(self):
        # init directory for save the audio
        for tts in self.ttss:
            make_dir(os.path.join(self.audio_dir, tts.getName()))

        # init directory for save the transcription
        for tts in self.ttss:
            make_dir(os.path.join(self.transcription_dir, tts.getName(), self.asr.getName()))

    def get_outputfile_for_failed_test_case(self):
        asr_dir = self.asr.getName()
        ttss_dir = "_".join([tts.getName() for tts in self.ttss])
        result_dir = os.path.join(self.output_dir,
                                  "result",
                                  ttss_dir,
                                  asr_dir,
                                  f"num_iteration_{self.num_iteration}",
                                  f"text_batch_size_{self.text_batch_size if self.text_batch_size else 'global'}")
        make_dir(result_dir)
        experiment_name = f"with-estimator-{self.estimator.getName().replace('/', '-')}" if self.estimator else "without-estimator"
        return os.path.join(result_dir, experiment_name + ".json")
    
    def get_outputfile_for_false_alarms(self):
        asr_dir = self.asr.getName()
        ttss_dir = "_".join([tts.getName() for tts in self.ttss])
        result_dir = os.path.join(self.output_dir,
                                  "result",
                                  ttss_dir,
                                  asr_dir,
                                  f"num_iteration_{self.num_iteration}",
                                  f"text_batch_size_{self.text_batch_size if self.text_batch_size else 'global'}")
        make_dir(result_dir)
        experiment_name = f"false_alarms"
        print(os.path.join(result_dir, experiment_name + ".xlsx"))
        return os.path.join(result_dir, experiment_name + ".xlsx")

    def getTTS(self):
        return self.ttss

    def addTTS(self, tts: TTS):
        for curr_tts in self.ttss:
            if tts.getName() == curr_tts.getName():
                # asr is already on the list of asrs
                return
        self.ttss.append(tts)

    def getASRS(self):
        return self.asr

    def addASR(self, asr: ASR):
        self.asr = asr

    # Julian removed this 08/09 - since only one asr
    # def removeASR(self, asr_name: str):
    #     for i, asr in enumerate(self.asrs):
    #         if asr_name == asr.getName():
    #             break
    #     del self.asrs[i]

    def getOutputDir(self):
        return self.audio_dir

    def setOutputDir(self, output_dir: str):
        self.output_dir = output_dir

        self.audio_dir = os.path.join(output_dir, DATA_DIR, AUDIO_DIR)
        self.transcription_dir = os.path.join(output_dir, DATA_DIR, TRANSCRIPTION_DIR)
        self.execution_time_dir = os.path.join(output_dir, EXECUTION_TIME_DIR)
        self.case_dir = os.path.join(output_dir, CASE_DIR)

    # Zi Qian updated this function 23/8
    def caseDeterminer(self, text: str, transcriptions: str):
        # word error rate
        wers = {}

        is_determinable = False
    
        # print(transcriptions)
        # {'google_wit': 'is technology making our attention span shorter'}
        # ({'google_wit': 0.0}, {'google_wit': 2})
        # TESTTTT
        # {'casual_wit': 'is technology making our attention span shorter'}
        # ({'casual_wit': 0.0}, {'casual_wit': 2})
        # output --> casual_data --> enhanced/mono --> ASR --> id_flag.text

        for k, transcription in transcriptions.items():
            word_error_rate = wer(text, transcription)
            wers[k] = word_error_rate
            if word_error_rate == 0:
                is_determinable = True

        case = {}
    
        if is_determinable:
            for k in transcriptions.keys():
                if wers[k] == 0:
                    case[k] = SUCCESSFUL_TEST_CASE
                else:
                    case[k] = FAILED_TEST_CASE
        else:
            for k in transcriptions.keys():
                case[k] = INDETERMINABLE_TEST_CASE

        return wers, case

    def casesDeterminer(self, text: str, transcriptions: dict):
        # word error rate
        wers = {}
        false_alarm_transcriptions = {}

        is_determinable = False

        is_false_alarm = False
    
        print(transcriptions)
        # {
        # 'google_wit': 'is technology making our attention span shorter', 
        # 'festival_wit': '',
        # 'casual_wit': 'is technology making our attention span shorter'
        # }

        # {'original': 'original transcription', 'casual_wit': '', 'festival_wit': '', 'google_wit': ''}

        for k, transcription in transcriptions.items():
            word_error_rate = wer(text, transcription)
            wers[k] = word_error_rate
            if word_error_rate == 0:
                is_determinable = True
                tts = k.split('_')[0]
                if tts == 'casual':
                    is_false_alarm = True

        case = {}
        if is_determinable and is_false_alarm:
            for k in transcriptions.keys():
                if wers[k] == 0:
                    case[k] = SUCCESSFUL_TEST_CASE
                else:
                    false_alarm_transcriptions['original'] = text
                    false_alarm_transcriptions[k] = transcriptions[k]
                    case[k] = FALSE_ALARM_TEST_CASE
        elif is_determinable and not is_false_alarm:
            for k in transcriptions.keys():
                if wers[k] == 0:
                    case[k] = SUCCESSFUL_TEST_CASE
                else:
                    case[k] = FAILED_TEST_CASE
        else:
            for k in transcriptions.keys():
                case[k] = INDETERMINABLE_TEST_CASE

        return wers, case, false_alarm_transcriptions

    def saveCase(self, case_dir: str, tts_name: str, asr_name: str, filename: str, case: str):
        case_dir = os.path.join(case_dir, tts_name, asr_name)
        make_dir(case_dir)
        fpath = os.path.join(case_dir, filename + ".txt")
        file = open(fpath, "w+")
        file.write(case)
        file.close()

    # 23/8 - Zi Qian: save WER (write to second line)
    def saveCaseWER(self, case_dir: str, tts_name: str, asr_name: str, filename: str, case: str):
        case_dir = os.path.join(case_dir, tts_name, asr_name)
        make_dir(case_dir)
        fpath = os.path.join(case_dir, filename + ".txt")
        file = open(fpath, "a")
        file.write("\n")
        file.write(case)
        file.close()

    def getCase(self, case_dir: str, tts_name: str, asr_name: str, filename: str):
        case_dir = os.path.join(case_dir, tts_name, asr_name)
        fpath = os.path.join(case_dir, filename + ".txt")
        file = open(fpath, "r")
        case = int(file.readlines()[0][0])
        file.close()
        return case

    # 23/8 - Zi Qian: get WER (write to second line)
    def getCaseWER(self, case_dir: str, tts_name: str, asr_name: str, filename: str):
        case_dir = os.path.join(case_dir, tts_name, asr_name)
        fpath = os.path.join(case_dir, filename + ".txt")
        file = open(fpath, "r")
        case = float(file.readlines()[1])
        file.close()
        return case

    # Julian updated this function 08/09
    # Zi Qian updated this function 23/8
    def printResult(self, text: str, filename: str):

        print()
        print(f"TTSs: {[tts.getName() for tts in self.ttss]}")
        print(f"ASR: {self.asr.getName()}")
        print()
        print(f"Input text: {text}")
        print()
        for tts in self.ttss:
            print(f"Transcription: {tts.getName()}")
            transcription_dir = os.path.join(
                self.transcription_dir, tts.getName())
            transcription = self.asr.loadTranscription(
                transcription_dir=transcription_dir, filename=filename)
            print(f"\t {self.asr.getName()}: {preprocess_text(transcription)}")


        print()
        for tts in self.ttss:
            print(f"Cases: {tts.getName()}")
            case = self.getCase(self.case_dir, tts.getName(), self.asr.getName(), filename)
            wer = self.getCaseWER(self.case_dir, tts.getName(), self.asr.getName(), filename)

            if case == FAILED_TEST_CASE:
                print(f"\t {self.asr.getName()}: failed test case")
                print(f"\t WER: {wer}")

            elif case == SUCCESSFUL_TEST_CASE:
                print(f"\t {self.asr.getName()}: successful test case")
                print(f"\t WER: {wer}")
            else:
                print(f"\t {self.asr.getName()}: indeterminable test case")
                print(f"\t WER: {wer}")
        print()

    def printStatistic(self):
        f = self.get_outputfile_for_failed_test_case()
        data = crossasr.utils.read_json(f)
        print()
        print("Number of Failed Test Case Found")
        for k, v in data["number_of_failed_test_cases_per_asr"].items():
            print(f"\t{k}: {v[-1]}")
        print(f"\tTotal: {data['number_of_failed_test_cases_all'][-1]}")
        print()


    def processText(self, text: str, filename: str, cc_dir: str):
        """
        Run CrossASR on a single text
        Description: Given a sentence as input, the program will generate a test case. The program needs some parameters, i.e. a TTS and ASRs used
        :params text:
        :params filename:
        :returns case:
        :returns execution time:
        """
        execution_time = 0.
        transcriptions = {}
        cases_list = []

        for tts in self.ttss:
            ### GENERATE/OBTAIN AUDIO FILE FOR ASR
            if tts.getName() != "casual":
                # create directory to save tts execution time
                tts_exec_time_dir = os.path.join(self.execution_time_dir, AUDIO_DIR, tts.getName())
                make_dir(tts_exec_time_dir)
                time_for_generating_audio_fpath = os.path.join(tts_exec_time_dir, filename + ".txt")

                # tts audio output file path (e.g. <output_dir>/data/audio/<TTS>/<wav file>)
                audio_fpath = tts.getAudioPath(text=text, audio_dir=self.audio_dir, filename=filename)

                # TTS generates audio if audio file was never generated or if you decide to recompute the operation
                if self.recompute or not os.path.exists(audio_fpath):
                    start_time = time.time()
                    tts.generateAudio(text=text, audio_fpath=audio_fpath)
                    save_execution_time(fpath=time_for_generating_audio_fpath, execution_time=time.time() - start_time)

                # add execution time for generating audio into process_text execution time
                execution_time += get_execution_time(fpath=time_for_generating_audio_fpath)

            else: # human audio (no execution needed)
                audio_fpath = os.path.join(cc_dir, filename + ".wav")
                

            # create directory to save asr execution time
            transcription_dir = os.path.join(self.transcription_dir, tts.getName())
            asr_exec_time_dir = os.path.join(self.execution_time_dir, TRANSCRIPTION_DIR, tts.getName(), self.asr.getName())
            make_dir(asr_exec_time_dir)
            time_for_recognizing_audio_fpath = os.path.join(asr_exec_time_dir, filename + ".txt")

            # asr audio output file path (e.g. <output_dir>/data/transcription/<TTS>/<ASR>/<txt file>)
            transcription_fpath = os.path.join(transcription_dir, self.asr.getName(), filename + ".txt")

            if self.recompute or not os.path.exists(transcription_fpath):
                start_time = time.time()
                # TODO:
                # change recognize audio -> input audio instead of fpath
                # audio = asr.loadAudio(audio_fpath=audio_fpath)
                # transcription = asr.recognizeAudio(audio=audio)
                # asr.saveTranscription(transcription_fpath, transcription)
                transcription = self.asr.recognizeAudio(audio_fpath=audio_fpath)
                self.asr.setTranscription(transcription)
                self.asr.saveTranscription(transcription_dir=transcription_dir, filename=filename)
                save_execution_time(fpath=time_for_recognizing_audio_fpath, execution_time=time.time() - start_time)

            transcription = self.asr.loadTranscription(transcription_dir=transcription_dir, filename=filename)
            num_retry = 0
            while transcription == "" and num_retry < self.max_num_retry:
                print("...............Retrying............." + filename)

                start_time = time.time()
                transcription = self.asr.recognizeAudio(audio_fpath=audio_fpath)
                self.asr.setTranscription(transcription)
                self.asr.saveTranscription(
                    transcription_dir=transcription_dir, filename=filename)
                save_execution_time(
                    fpath=time_for_recognizing_audio_fpath, execution_time=time.time() - start_time)
                transcription = self.asr.loadTranscription(
                    transcription_dir=transcription_dir, filename=filename)

                if self.asr.getName() == "wit":
                    random_number = float(random.randint(9, 47)) / 10.
                    time.sleep(random_number)

                num_retry += 1

            transcriptions[tts.getName()] = preprocess_text(transcription)

            ## add execution time for generating audio
            execution_time += get_execution_time(
                fpath=time_for_recognizing_audio_fpath)

                # cases = self.caseDeterminer(text, transcriptions)
                # print(cases)
                # ({'casual_wit': 0.0}, {'casual_wit': 0})
                # print(transcriptions)
                # print(cases)
                # if sum(cases.values()) == 0 :
                #     print(text)
                #     print(transcriptions["wav2vec2"])
                #     print(cases)
                #     print()
        cases = self.casesDeterminer(text, transcriptions)
        # ({'casual_wit': 0.0}, {'casual_wit': 0})
        # cases_list: [({'google': 0.0}, {'google': 2}), ({'casual': 0.0}, {'casual': 0})]
        # cases: ({'google_wit': 0.0, 'casual_wit': 0.0}, {'google_wit': 2, 'casual_wit': 2})
       
        # To re-create cases list 
        for k, value in cases[0].items():
            wer_obj = {}
            case_obj = {}
            wer_obj[k] = value 
            case_obj[k] = cases[1][k]
            tuple = (wer_obj, case_obj)
            cases_list.append(tuple)

        for tts_name, case in cases[1].items():
            self.saveCase(self.case_dir, tts_name, self.asr.getName(), filename, str(case))

        # write WER into file
        for tts_name, case in cases[0].items():
            self.saveCaseWER(self.case_dir, tts_name, self.asr.getName(), filename, str(case))
        
        if cases[2]:
            cases[2]['filename'] = filename
            print('cases_filename') 
            print(cases)

        # print(f"Execution time: {execution_time}")
        return cases_list, execution_time, cases[2]

    def processOneIteration(self, curr_texts: [TextModi], processed_texts: [TextModi], cases):
        start_time = time.time()
        curr_cases = []
        false_alarms = []

        # if self.estimator and len(processed_texts) > 0:
        #     labels = get_labels_from_cases(cases)
        #     self.trainEstimator(processed_texts, labels)
        #     # print(f"Length texts: {len(curr_texts)}")
        #     # start_time_classifier = time.time()
        #     curr_texts = self.rank(curr_texts)
        #     # end_time_classifier = time.time()
        #     # print({f"Time for prediciton: {end_time_classifier-start_time_classifier}s"})

        execution_time = 0.

        i = 0
        for text in curr_texts:
            # print("================")
            # print(f"{text.getId()}")
            case, exec_time, false_alarm_transcription_obj = self.processText(
                text=text.getText(), filename=f"{text.getId()}", cc_dir=os.path.join(self.casual_dir, self.audio_type))
            if false_alarm_transcription_obj:
                false_alarms.append(false_alarm_transcription_obj)
            curr_cases.extend(case)
            execution_time += exec_time
            i += 1

            if execution_time + time.time() - start_time > self.time_budget:
                # print(f"Number of processed texts {i}")
                break

        curr_processed_texts = curr_texts[:i]
        unprocessed_texts = curr_texts[i:]
        print('===========')
        print(false_alarms)
        return curr_cases, curr_processed_texts, unprocessed_texts, false_alarms

    def writeResult(self, cases, num_false_alarms_test_cases, num_processed_texts):
        tts_avg_wer = {}
        for tts in self.ttss:
            total = 0
            count = 0
            for tuple_case in cases:
                key, value = list(tuple_case[0].items())[0]
                if key == tts.getName():
                    count += 1
                    total = total + float(value)
            if count != 0:
                tts_avg_wer[tts.getName()] = total / count

        data = {}
        data["number_of_false_alarms_test_cases_all"] = num_false_alarms_test_cases
        # data["number_of_failed_test_cases_per_asr"] = num_failed_test_cases_per_tts
        data["number_of_processed_texts"] = num_processed_texts
        data["average_word_error_rate"] = tts_avg_wer
        with open(self.outputfile_failed_test_case, 'w') as outfile:
            json.dump(data, outfile, indent=2, sort_keys=True)

    def processCorpus(self, texts: [TextModi]):
        """
        Run CrossASR on a corpus
        given a corpus, which is a list of sentences, the CrossASR generates test cases.
        :param texts: a list of tuple(sentence, id)
        """

        remaining_texts = texts
        curr_texts = []
        processed_texts = []
        cases = []
        num_false_alarms_test_cases = []
        num_failed_test_cases_per_tts = {}
        num_processed_texts = []
        false_alarms = []


        workbook = xlsxwriter.Workbook(self.outputfile_false_alarms)
        worksheet = workbook.add_worksheet()

        worksheet.write(0,0,"filename")
        worksheet.write(0,1,"original")
        
        row = 1
        col = 2
        tts_col_obj = {}
        # Save which tts is which column 
        for tts in self.ttss:
            if tts.getName() != "casual":
                worksheet.write(0,col,tts.getName())
                tts_col_obj[tts.getName()] = col
                col += 1
                num_failed_test_cases_per_tts[tts.getName()] = []
    

        for i in range(self.num_iteration):
            # print(f"Iteration: {i+1}")
            if self.text_batch_size:
                curr_texts = remaining_texts[:self.text_batch_size]
                remaining_texts = remaining_texts[self.text_batch_size:]

            else:  # use global visibility
                curr_texts = remaining_texts

            if len(curr_texts) > 0:

                curr_cases, curr_processsed_texts, unprocessed_texts, false_alarm_arr = self.processOneIteration(curr_texts,
                                                                                                processed_texts, cases)
                for obj in false_alarm_arr:
                    # false_alarms.append(obj)
                    for key in obj.keys():
                        if key == 'filename':
                            worksheet.write(row,0,obj[key])
                        elif key == 'original':
                            worksheet.write(row,1,obj[key])
                        else:
                            worksheet.write(row, tts_col_obj[key], obj[key])
                    row += 1
                    
                cases.extend(curr_cases)
                processed_texts.extend(curr_processsed_texts)
                if self.text_batch_size:
                    remaining_texts.extend(unprocessed_texts)
                else:
                    remaining_texts = unprocessed_texts

                num_false_alarms_test_cases.append(calculate_cases(cases, mode=FALSE_ALARM_TEST_CASE))
                # num_failed_test_cases_per_tts[self.asr.getName()].append(calculate_cases_per_asr(
                #     cases, mode=FAILED_TEST_CASE, asr_name=self.asr.getName()))
                num_processed_texts.append(len(processed_texts))
                self.writeResult(cases, num_false_alarms_test_cases, num_processed_texts)

            else:
                print("Texts are not enough!")

            # shuffle the remaining texts
            np.random.shuffle(remaining_texts)
        tts_avg_wer = {}
        for tts in self.ttss:
            total = 0
            count = 0
            for tuple_case in cases:
                key, value = list(tuple_case[0].items())[0]
                if key == tts.getName():
                    count += 1
                    total = total + float(value)
            if count != 0:
                tts_avg_wer[tts.getName()] = total / count
        data = {}
        data["number_of_false_alarms_test_cases_all"] = num_false_alarms_test_cases
        # data["number_of_failed_test_cases_per_asr"] = num_failed_test_cases_per_tts
        data["number_of_processed_texts"] = num_processed_texts
        data["average_word_error_rate"] = tts_avg_wer
        data["false_alarm_cases"] = false_alarms
        with open(self.outputfile_failed_test_case, 'w') as outfile:
            json.dump(data, outfile, indent=2, sort_keys=True)
        workbook.close()
        #
        # if self.target_asr:
        #     self.saveFailedTestCases(processed_texts, cases)

    def saveFailedTestCases(self, processed_texts, cases):
        failed_test_case_dir = os.path.join(self.output_dir, "failed_test_cases", self.tts.getName(), self.target_asr)
        make_dir(failed_test_case_dir)
        ids = self.get_id_only(processed_texts)
        input_texts = self.get_text_only(processed_texts)
        source_audio_dir = os.path.join(self.audio_dir, self.tts.getName())
        for input_text, filename, case in zip(input_texts, ids, cases):
            if case[self.target_asr] == FAILED_TEST_CASE:
                src_audio_fpath = source_audio_dir + f"/{filename}.wav"
                trgt_audio_fpath = failed_test_case_dir + f"/{filename}.wav"
                os.system(f"cp {src_audio_fpath} {trgt_audio_fpath}")
                ground_truth_file = failed_test_case_dir + f"/{filename}.txt"
                f = open(ground_truth_file, 'w+')
                f.write(input_text)
                f.close()

    def get_text_only(self, texts: [Text]) -> [str]:
        res = []
        for t in texts:
            res.append(t.getText())
        return res

    def get_id_only(self, texts: [Text]) -> [str]:
        res = []
        for t in texts:
            res.append(t.getId())
        return res

    def trainEstimator(self, processed_texts, labels):
        train_texts = self.get_text_only(processed_texts)
        self.estimator.fit(train_texts, labels)

    def rank(self, texts: [Text]):

        ranking = self.estimator.predict(self.get_text_only(texts))

        ## https://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list
        texts = [x for _, x in reversed(sorted(zip(ranking, texts)))]

        return texts


def calculate_cases(cases, mode: str):
    count = 0
    for c in cases:
        for _, v in c[1].items():
            if v == mode:
                count += 1
    return count


def calculate_cases_per_asr(cases, mode: str, asr_name: str):
    count = 0
    for c in cases:
        for k, v in c[1].items():
            if k.split("_")[1] == asr_name and v == mode:
                count += 1
    return count


def get_labels_from_cases(cases):
    def determine_label(case):
        if INDETERMINABLE_TEST_CASE in case.values():
            return INDETERMINABLE_TEST_CASE
        if FAILED_TEST_CASE:
            return FAILED_TEST_CASE
        return SUCCESSFUL_TEST_CASE

    labels = []
    for case in cases:
        label = determine_label(case)
        labels.append(label)

    return labels
