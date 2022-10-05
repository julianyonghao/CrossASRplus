import sys
import utils
import os

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == "__main__":
    result_folder_name = "output/lj_deepspeech_corpus/"
    casual_data_fpath = "casual_data/Casual_Data_LJ"

    case_fpath = os.path.join(result_folder_name, "case", "festival", "deepspeech")

    make_dir(os.path.join(result_folder_name, "for_rnn_data"))
    rnn_data_file = open(os.path.join(result_folder_name, "for_rnn_data", "rnn_data_training.txt"), "w")
    rnn_data_testing_file = open(os.path.join(result_folder_name, "for_rnn_data", "rnn_data_test.txt"), "w")
    num_of_false_alarms = 1385 #get value from results file
    max_cap = 1380
    keep_for_testing = num_of_false_alarms - max_cap
    zero_index = 0
    zero_test_index = 0
    one_index = 0
    for subdir, dirs, files in os.walk(case_fpath):

        for ori_file in files:
            try:
                file = open(os.path.join(case_fpath, ori_file))
                text = file.readlines()
                ground_truth_file = open(os.path.join(casual_data_fpath, "transcription", ori_file))
                ground_truth_text = ground_truth_file.readlines()[0]
                if int(text[0][0]) == 3:
                    if one_index < max_cap:
                        rnn_data_file.write(ori_file.split(".")[0] + "\t" + ground_truth_text + "\t" + "1\n")
                        one_index += 1
                    else:
                        rnn_data_testing_file.write(ori_file.split(".")[0] + "\t" + ground_truth_text + "\t" + "1\n")
                else:
                    if zero_index < max_cap:
                        rnn_data_file.write(ori_file.split(".")[0] + "\t" + ground_truth_text + "\t" + "0\n")
                        zero_index += 1
                    else:
                        if zero_test_index < keep_for_testing:
                            rnn_data_testing_file.write(ori_file.split(".")[0] + "\t" + ground_truth_text + "\t" + "0\n")
                            zero_test_index += 1
                ground_truth_file.close()
                file.close()
            except:
                continue
    rnn_data_file.close()

