
def topsis(d,w,c):
    size = d.shape
    sq_sum = []
    for i in range(size[1]):
        temp = 0
        for j in range(size[0]):
            temp += (d.iloc[j,i])**2
        temp = temp**0.5
        sq_sum.append(temp)
        
    for i in range(size[1]):
        d.iloc[:,i] /= sq_sum[i]
        d.iloc[:,i] *= (w[i]/size[1])
     
    
    i_best = []
    i_worst = []
    for i in range(size[1]):
        
        if c[i] == '+':
            i_best.append(max(d.iloc[:,i]))
            i_worst.append(min(d.iloc[:,i]))
        else:
            i_best.append(min(d.iloc[:,i]))
            i_worst.append(max(d.iloc[:,i]))
  
    db = []
    dw = []
    for i in range(size[0]):
        temp = 0
        temp1 = 0
        for j in range(size[1]):
            temp += (i_best[j] - d.iloc[i,j])**2
            temp1 += (i_worst[j] - d.iloc[i,j])**2
        temp = temp**0.5
        temp1 = temp1**0.5
        db.append(temp)
        dw.append(temp1)
        
    performance_score = []
    for i in range(size[0]):
        performance_score.append(dw[i]/(dw[i] + db[i]))
        
    rank = []
    for i in range(len(performance_score)):
        rank.insert(performance_score.index(max(performance_score)),i+1)
        performance_score.remove(max(performance_score))

    return rank


    
