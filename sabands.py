# Reading input list, select two random entries,
# finds coverart for them and deleted them from the input list

import pandas as pd
import os
from random import randint
import sys

import coverart

# filename='sabands.csv'

# ---
def getalbums(filename):
    # count number of lines
    with open(filename, 'r') as f:
        data = pd.read_csv(filename, delimiter=",", header=0)
        data = data.dropna()

        numlines = data.shape[0]

        print('Total data lines: {}\n'.format(numlines))

    outdf = pd.DataFrame(columns=data.columns)

    selectnums = [randint(0,numlines) for p in range(0,2)]

    i = 0
    for i in range(0,2):
        s = selectnums[i]
        r = data.iloc[s]
        outdf.loc[i] = r
        # drop from input data
        data = data.drop(data.index[s])
        ++i

    print(outdf)
    outfile = 'out.txt'
    outdf.to_csv(outfile, index=False, header=False)
    print('')

    with open('out.txt', 'w') as w:
        cover0 = outdf.iloc[0]['Artist'] + ' - ' + outdf.iloc[0]['Album']
        w.write(cover0+'\n')
        cover1 = outdf.iloc[1]['Artist'] + ' - ' + outdf.iloc[1]['Album']
        w.write(cover1+'\n')

    print(cover0)
    print(cover1)

    #write out a new list minus selected entries
    with open(filename, 'w') as o:
        data.to_csv(filename, index=False)

# ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: saband.py <input file 1>')
        exit(1)

    inputFile1 = sys.argv[1]

    getalbums(inputFile1)

    coverart.main('out.txt', 'out')


