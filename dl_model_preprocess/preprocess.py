import sys
import utils
import os
import pandas as pd

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == "__main__":
    result_folder_name = "../dl_model_results_rank/"
    dataset_folder_name = "../examples/casual_data/Casual_Data_LJ/transcription/"


    rnn_data_file = open(os.path.join(result_folder_name, "rnn_data_training.txt"), "w")
    rnn_data_testing_file = open(os.path.join(result_folder_name, "rnn_data_test.txt"), "w")
    num_of_false_alarms = 1108 #get value from results file
    max_cap = 1108
    keep_for_testing = num_of_false_alarms - max_cap
    zero_index = 0
    zero_test_index = 0
    one_index = 0
    no_cap = True

    filter_specific_index_for_manual_test =[]
    false_alarm_file_list = []
    data = pd.read_excel(os.path.join(result_folder_name, "false_alarm_rank.xlsx"))
    current = ""
    fa_index = 0
    for index in data.index:
        if fa_index == num_of_false_alarms:
            break
        if current != data['filename'][index]:
            current = data['filename'][index]
            false_alarm_file_list.append(current)
            if (one_index < max_cap or no_cap) and index not in filter_specific_index_for_manual_test:
                rnn_data_file.write(data['filename'][index] + "\t" + data['original'][index] + "\t" + "1\n")
                one_index += 1
            else:
                rnn_data_testing_file.write(data['filename'][index] + "\t" + data['original'][index] + "\t" + "1\n")
            fa_index = fa_index + 1

    for subdir, dirs, files in os.walk(dataset_folder_name):

        for ori_file in files:
            if ori_file.split(".")[0] not in false_alarm_file_list:
                try:
                    file = open(os.path.join(dataset_folder_name, ori_file))
                    text = file.readlines()[0]
                    rnn_data_file.write(ori_file.split(".")[0] + "\t" + text + "\t" + "0\n")
                    # if zero_index < max_cap or no_cap:
                    #     rnn_data_file.write(ori_file.split(".")[0] + "\t" + text + "\t" + "0\n")
                    #     zero_index += 1
                    # else:
                    #     if zero_test_index < keep_for_testing:
                    #         rnn_data_testing_file.write(
                    #             ori_file.split(".")[0] + "\t" + text + "\t" + "0\n")
                    #         zero_test_index += 1

                    file.close()
                except:
                    continue
    rnn_data_file.close()