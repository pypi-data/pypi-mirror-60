import os
import pandas as pd
import numpy as np
import math
import sys

def topsis(filename, weight_string, impact_string):  
    weights = weight_string.split(",")
    impacts = impact_string.split(",")
    raw_data = pd.read_csv(os.getcwd() + "\\" + filename)
    data = raw_data.iloc[:,1:].values
    model_names = raw_data.iloc[:, 0].values
    num_rows = len(data)
    num_columns = len(data[0])

    column_sums = []

    for i in range(num_rows):
        for j in range(num_columns):
            if(i==0):
                column_sums.append(data[i][j] * data[i][j])
            else:
                column_sums[j] += data[i][j] * data[i][j]
            if(i == num_rows-1):
                column_sums[j] = math.sqrt(column_sums[j])

    for i in range(num_rows):
        for j in range(num_columns):
            data[i][j] *= float(weights[j])
            data[i][j] /= column_sums[j]

    best = []
    worst = []

    for i in range(num_rows):
        for j in range(num_columns):
            if(i==0):
                best.append(data[i][j])
                worst.append(data[i][j])
            else:
                if(impacts[j] == "+"):
                    if(data[i][j] > best[j]):
                        best[j] = data[i][j]
                    if(data[i][j] < worst[j]):
                        worst[j] = data[i][j]
                else:
                    if(data[i][j] < best[j]):
                        best[j] = data[i][j]
                    if(data[i][j] > worst[j]):
                        worst[j] = data[i][j]

    print_header = np.concatenate([ list(raw_data), ["S+", "S-", "Perf. Score", "Rank"] ])
    print_data = []

    for i in range(num_rows):
        s_pos = 0
        s_neg = 0
        for j in range(num_columns):
            s_pos += (data[i][j] - best[j])**2     
            s_neg += (data[i][j] - worst[j])**2
        s_pos = math.sqrt(s_pos)     
        s_neg = math.sqrt(s_neg)     
        perf_score = (s_neg)/(s_neg+s_pos)
        
        print_data.append(np.concatenate([ [model_names[i]] ,data[i], [s_pos, s_neg, perf_score, int(i+1)]], axis=0))

    print_data = sorted(print_data, key=lambda x:x[7], reverse = True)

    for i in range(num_rows):
        print_data[i][8] = i+1

    str = ""
    for i in print_header:
        str += '{0: <15}'.format(i)
    for row in print_data:
        str += "\n\n"
        for d in row:
            try:
                d_n = round(float(d), 5)
            except:
                d_n = d
            str += '{0: <15}'.format( d_n )
    print("\n\n")
    print(str)
    print("\n\n")

def cmd_topsis():
    try:
        current_file, filename, weight_string, impact_string = sys.argv
        topsis(filename, weight_string, impact_string)
    except:
        if(len(sys.argv) <= 1): print("Refer to Readme.md for using the package.")
        else: print("Invalid use!")