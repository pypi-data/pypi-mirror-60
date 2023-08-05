import sys
import numpy as np
import pandas as pd
import math
import scipy.stats as ss
def main():
    dataset = pd.read_csv(sys.argv[1]).values             
#    decision_matrix = dataset[:,1:]                        
    weights = [float(i) for i in sys.argv[2].split(',')]   
    impacts = sys.argv[3].split(',')                      
    topsis(dataset , weights , impacts)
def topsis(dataset,weight,impact):
   
    

    dataset = pd.DataFrame(dataset)
    output = dataset.iloc[:,:]
    
    a=dataset.shape
    no_rows=a[0]
    no_cols=a[1]
    #normalize
    dataset = dataset ** 2
    sum_of_sq = dataset.sum(axis=0)
    dataset["sum_of_sq"] = sum_of_sq
    dataset["square_root"] = np.sqrt(dataset["sum_of_sq"])
    
    dataset = output.divide(dataset["square_root"], axis=1)
    dataset = dataset.iloc[:,:-1]
    
    #multiply with weights
    
    dataset = dataset.mul(weight,axis=1)
    maxValue = dataset.max()
    minValue = dataset.min()
    vPlus = []
    vMinus = []
    #finding the worst and the best 
    
    for i in range(0,no_cols):
        if(impact[i] == '-'):
            vPlus.append(maxValue[i])
            vMinus.append(minValue[i])
        else:
            vPlus.append(minValue[i])
            vMinus.append(maxValue[i])
    
    dataset = dataset.to_numpy()    
    p = []
    sPlus = []
    sMinus = []
    for i in range(0,no_rows):
        ans1=0
        ans2=0
        for j in range(0,no_cols):
            ans1 = ans1 + (dataset[i,j] - vPlus[j])*(dataset[i,j] - vPlus[j])
            ans2 = ans2 + (dataset[i,j] - vMinus[j])**2
           
        ans1 = math.sqrt(ans1)
        sPlus.append(ans1)
        ans2 = math.sqrt(ans2)
        sMinus.append(ans2)
        p.append(ans1/(ans1+ans2))
    
        
    rank = ss.rankdata(p)
    rank = len(rank) - rank + 1
    output["performance score"] = p
    output["rank"] = rank
    
    return output
if __name__=="__main__" :
    main()       
