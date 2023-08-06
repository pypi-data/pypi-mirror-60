#importing libraries
import numpy as np
import pandas as pd

#defining the outliers removal function
#using Z-VALUE
def outliers_removal(inputcsv_file, outputcsv_file):
    dataset = pd.read_csv(inputcsv_file)
    d = dataset.iloc[:,1:]  
    for i, row in d.iterrows():
        threshold = 3
        #calculating mean
        mean = np.mean(row)
        #calculate standard deviation
        std = np.std(row)
        for value in row:
            z_score = (value-mean)/std
            if np.abs(z_score)>threshold:
                dataset = dataset.drop(d.index[i])
                break
    dataset.to_csv(outputcsv_file, index=False)
    
    print 'The number of rows removed are:',len(d) - len(dataset)