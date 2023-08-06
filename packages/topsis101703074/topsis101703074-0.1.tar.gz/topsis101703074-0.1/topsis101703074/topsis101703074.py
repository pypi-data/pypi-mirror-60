import sys
import pandas as pd

filename = sys.argv[1]
weights = [float(val) for val in sys.argv[2].split(',')]
benefit = sys.argv[3].split(',')

def topsis(filename, weights, benefit):
    data = pd.read_csv(filename)
    
    #data = pd.read_csv('Mobiles.csv')
    #weights = [0.25]*4
    #benefit = ['-','+','+','+']
    
    n_cols = len(benefit)
    data2 = [[val for val in data[col]] for col in data]
    data2.insert(0,list(data.keys()))
    
    for num in range(1,n_cols+1):
        if(type(data2[num][0]) != int and type(data2[num][0]) != float):
            data = data.drop(data2[0][num-1], axis=1)
    n_cols = data.shape[1]
    n_rows = data.shape[0]
    
    normalized_data = []
    
    # Normalize
    for num in range(n_cols):
        if(benefit[num] == '-'): # Non-beneficial
            min_val = min(data.iloc[:,num])
            normalized_data.append([(min_val/val) for val in data.iloc[:,num]])        
        else: # Beneficial
            max_val = max(data.iloc[:,num])
            normalized_data.append([(val/max_val) for val in data.iloc[:,num]])
            
            
    # Multiply with weights  
    for num in range(n_cols):
        for row in range(len(normalized_data[num])):
            normalized_data[num][row] = normalized_data[num][row] * weights[num]
            
            
    # Add row wise
    sums = [0]*n_rows
    for num in range(n_rows):
        for col in range(n_cols):
            sums[num] += normalized_data[col][num]
    
    temp_list = sums.copy()  
    rank = [0]*n_rows
    for num in range(n_rows):
        ind = temp_list.index(max(temp_list))
        rank[ind] = num+1;
        temp_list[ind] = -1
        
    results = {'rank':rank, 'sums':sums}
    return results 

#print(topsis(filename, weights, benefit))