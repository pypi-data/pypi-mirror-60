import sys
import topsis
import pandas as pd

def main():
    data = pd.read_csv(sys.argv[1])
    data = data.iloc[:,1:5]
    t = sys.argv[2]
    v = sys.argv[3]
    w = []
    c = []
    for i in range(len(t)):
        if t[i] == ',':
           continue
        else:
            w.append(int(t[i]))
            c.append(v[i])
            
          
    print(topsis.topsis(data,w,c))

if __name__ == '__main__':
    main()
    


