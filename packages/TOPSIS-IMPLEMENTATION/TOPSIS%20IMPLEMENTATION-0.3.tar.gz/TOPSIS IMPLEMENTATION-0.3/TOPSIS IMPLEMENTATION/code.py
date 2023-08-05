
def topsiscode(data, matrix, sign):
    import numpy as np
    import pandas as pd
    dataset = pd.read_csv('data')    
    x = dataset.shape[0]
    y = dataset.shape[1]

    summ = sum(matrix)
    
    s = []
    for j in range(y):
        s.append(0)
        for i in range(x):
            s[j] = s[j]+(dataset.get_value(i,j,takeable = 'True')*dataset.get_value(i,j,takeable = 'True'))
        s[j]=np.sqrt(s[j])

    for i in range(y):
        for j in range(x):
            mat2=(dataset.get_value(j,i,takeable = 'True')*matrix[i]/summ/s[i])
            dataset.set_value(j, dataset.columns[i], mat2)
        vmax = []
        vmin =[]

    for i in  range(y):
        if sign[i]=='+':
            vmax.append(dataset[dataset.columns[i]].max())
            vmin.append(dataset[dataset.columns[i]].min())
        elif sign[i]=='-':
            vmax.append(dataset[dataset.columns[i]].min())
            vmin.append(dataset[dataset.columns[i]].max())
    sp =[]
    sn=[]

    for i in range(x):
        sp.append(0)
        sn.append(0)
        for j in range(y):
            sp[i]=sp[i]+((dataset.get_value(i,j,takeable = 'True')-vmax[j])*(dataset.get_value(i,j,takeable = 'True')-vmax[j]))
            sn[i]=sn[i]+((dataset.get_value(i,j,takeable = 'True')-vmin[j])*(dataset.get_value(i,j,takeable = 'True')-vmin[j]))
        sp[i]=np.sqrt(sp[i])
        sn[i]=np.sqrt(sn[i])

    final = []
    for i in range(x):
        final.append(0)
        final[i]=sn[i]/(sn[i]+sp[i])

    fianl = pd.DataFrame(final)
    f = fianl.rank()
    return(f)

    