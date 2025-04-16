import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt

samp_rate = 10e6
N_FRAMES = 10
START_FRAME = 1

if len(sys.argv) == 2:
    samp_rate = int(sys.argv[1])

#* CORRELATION HELPERS
def mean(X):
    return np.sum(X, axis=0)/len(X)

def std_dev(X, X_bar):
    return np.sqrt(np.sum((X-X_bar)**2, axis=0))

def cov(X, X_bar, Y, Y_bar):
    return np.sum((X-X_bar)*(Y-Y_bar), axis=0)

def pearson(X,Y):
    X_mean = mean(X)
    Y_mean = mean(Y)    
    return cov(X, X_mean, Y, Y_mean)/(std_dev(X, X_mean)*std_dev(Y, Y_mean))

#* TRACE METADATA HELPER
def get_fps(path:str):
    return float(path.split('@')[-1].strip())

def get_x(path:str):
    return int(path.split('x')[0].strip())

def get_y(path:str):
    return int(path.split('x')[1].split('@')[0].strip())

paths = []
for entry in os.scandir("traces/"):
    path = entry.path.split('/')[-1].replace(".trace", '')
    if re.match(r"^\d+x\d+@\d+\.\d+$", path):
        paths.append(path)
print(paths)
print(f"# Correlation over {N_FRAMES} frame(s), skipping {START_FRAME} frame(s)")
for path in paths:
    data = np.fromfile(open("traces/"+path+".trace"), dtype=np.float32)
    frame_t = int(samp_rate/get_fps(path)) #time that a whole (inc padding) frame takes in the trace

    correlations = []
    for i in range(START_FRAME, START_FRAME+N_FRAMES):
        if frame_t*(i+2) >= len(data):
            print("error: sample too small/target frame too high!")
            break

        samp1 = data[frame_t*i:frame_t*(i+1)]
        samp2 = data[frame_t*(i+1):frame_t*(i+2)]
        r = pearson(samp1, samp2)
        correlations.append(r)

    print(f"{path}: \n\tmax {max(correlations)}\n\tmean {mean(correlations)}\n\tmin {min(correlations)}")

