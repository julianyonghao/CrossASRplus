import os
import pandas as pd
import xlsxwriter

if __name__ == "__main__":
    false_alarm_dict = {}
    for subdir, dirs, files in os.walk('./'):
        for dir in dirs:
            data = pd.read_excel(os.path.join(dir, "false_alarms.xlsx"))
            current = ""
            for index in data.index:
                if current != data['filename'][index]:
                    current = data['filename'][index]
                    if current in false_alarm_dict:
                        freq, ori = false_alarm_dict[current]
                        false_alarm_dict[current] = (freq + 1 , ori)
                    else:
                        false_alarm_dict[current] = (1, data['original'][index])
    workbook = xlsxwriter.Workbook('false_alarm_rank.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "filename")
    worksheet.write(0, 1, "original")
    worksheet.write(0, 2, "frequency")

    sorted_false_alarm_dict = {k: v for k, v in sorted(false_alarm_dict.items(), key=lambda item: item[1][0], reverse=True)}
    row = 1
    for key, value in sorted_false_alarm_dict.items():
        worksheet.write(row, 0, key)
        worksheet.write(row, 1, value[1])
        worksheet.write(row, 2, value[0])
        row = row + 1
    workbook.close()