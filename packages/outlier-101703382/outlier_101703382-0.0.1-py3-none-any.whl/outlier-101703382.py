import numpy as np
import pandas as pd

def remove_outliers(incsv_filename, outcsv_filename):

    ds = pd.read_csv(incsv_filename)	
    data = ds.iloc[:,1:]  

    for i, row in data.iterrows():
        threshold_value = 1.5
        mean = np.mean(row)
        std = np.std(row)
        for value in row:
            z_score = (value-mean)/std
            if np.abs(z_score)>threshold_value:
                ds = ds.drop(data.index[i])
                break
            
    ds.to_csv(outcsv_filename, index=False)
    print ('The no of rows removed:',len(data) - len(ds))


