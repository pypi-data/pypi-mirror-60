# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 19:27:00 2020

@author: Nishant
"""

import numpy as np
import pandas as pd

def outliers_detection(input_csv_file, output_csv_file):
    
    
    dataset1 = pd.read_csv(input_csv_file)
    dataset2 = dataset1.iloc[:,1:]  

    for ind, row in dataset2.iterrows():
        threshold = 3
        mean = np.mean(row)
        std_dev = np.std(row)
        for value in row:
            z_score = (value-mean)/std_dev
            if np.abs(z_score)>threshold:
                dataset1 = dataset1.drop(dataset2.index[ind])
                break
            
    dataset1.to_csv(output_csv_file, index=False)
    print('Number of rows removed are :',len(dataset2) - len(dataset1))
    
    
