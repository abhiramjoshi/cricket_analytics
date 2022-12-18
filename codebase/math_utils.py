import numpy as np

def clusterize(line, bin_size=2):
    clustered = []
    for i in range((len(line)//bin_size) + 1):
        total = 0
        for j in range(bin_size):
            try:
                total += line[(bin_size*i)+j]
            except IndexError:
                try:
                    total /= j
                    clustered.append(total)
                except ZeroDivisionError:
                    pass
                return clustered
        total /= bin_size
        clustered.append(total)

    return clustered

def first_difference(line):
    a1 = np.array(line[:-1])
    a2 = np.array(line[1:])
    return a2-a1