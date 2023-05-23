# First column is file name 
# Second column is ASR name 
# Third column is the original transcription, meaning the correct transcription 
# Fourth column is the transcribed text 

# Compare third and fourth column to find out text difference 
# Is first row target ASR?
# Only find out target ASR?

# import module
import openpyxl
import difflib
import xlsxwriter

def post_processing(file_path, output_file_path):
    
    # load excel with its path
    wrkbk = openpyxl.load_workbook(file_path)
    sh = wrkbk.active
    prev_filename = ''
    k = 1
    dict = {}
    row = 1
  
    # iterate through excel and display data
    # row 
    for i in range(2, sh.max_row+1):
        # print("\n")
        # print("Row ", i, " data :")

        # Get filename
        filename_obj = sh.cell(row=i, column=1)
        filename = filename_obj.value

        if filename == prev_filename:
            prev_filename = filename 
            continue 
        else:
        
            # initiate the Differ object
            d = difflib.Differ()

            
            # calculate the difference between the two texts
            original = sh.cell(row=i, column=3).value
            transcribed = sh.cell(row=i, column=4).value
            diff = d.compare(original.split(), transcribed.split())

            # output the result
            # print ('\n'.join(diff))
            for word in list(diff):
                if word[0] == '-' or word[0] == '+':
                    print(word)
                    if word in dict:
                        dict[word] = dict[word] + 1
                    else:
                        dict[word] = 1
            prev_filename = filename

        # column 
        # for j in range(1, sh.max_column+1):
        #     cell_obj = sh.cell(row=i, column=j)
        #     print(cell_obj.value, end=" ")
    print(output_file_path)
    workbook = xlsxwriter.Workbook(output_file_path)
    worksheet = workbook.add_worksheet()

    worksheet.write(0,0,"word")
    worksheet.write(0,1, "frequency")

    for key, value in dict.items():
        worksheet.write(row,0,key)
        worksheet.write(row,1, value)
        row +=1
    workbook.close()
    

if __name__ == "__main__":
    post_processing("results/false_alarms.xlsx", "false_alarm_pattern.xlsx")