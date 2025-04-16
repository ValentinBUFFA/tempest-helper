import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt

from helpers import *

samp_rate = 10e6
N_FRAMES = 5
START_FRAME = 5

HARMONIC_THRESHOLD = 500_000_000

# * CORRELATION HELPERS
def mean(X):
    return np.sum(X, axis=0) / len(X)


def std_dev(X, X_bar):
    return np.sqrt(np.sum((X - X_bar) ** 2, axis=0))


def cov(X, X_bar, Y, Y_bar):
    return np.sum((X - X_bar) * (Y - Y_bar), axis=0)


def pearson(X, Y):
    X_mean = mean(X)
    Y_mean = mean(Y)
    return cov(X, X_mean, Y, Y_mean) / (std_dev(X, X_mean) * std_dev(Y, Y_mean))


# compute correlations for every trace in the folder
def correlate_folder(folder_path="traces/", verbose=False):
    # get all .trace files in the folder
    paths = []
    for entry in os.scandir(folder_path):
        path = entry.path.split("/")[-1].replace(".trace", "")
        if re.match(r"^\d+x\d+@\d+\.\d+#?[a-zA-Z]*$", path):
            paths.append(path)

    # keep track of the max
    max_correlations = []
    print(f"Correlation over {N_FRAMES} frame(s), skipping {START_FRAME} frame(s)")
    for path in paths:
        data = np.fromfile(os.path.join(folder_path, path + ".trace"), dtype=np.float32)
        # time that a whole (inc padding) frame takes in the trace
        frame_t = int(samp_rate / get_fps(path))

        # compute pearson coefficients for each successive pair of frames
        correlations = []
        for i in range(START_FRAME, START_FRAME + N_FRAMES):
            # prevent going out of bounds for the sample
            if frame_t * (i + 2) >= len(data):
                print("error: sample too small/target frame too high!")
                break

            samp1 = data[frame_t * i : frame_t * (i + 1)]
            samp2 = data[frame_t * (i + 1) : frame_t * (i + 2)]
            r = pearson(samp1, samp2)
            correlations.append(r)

        max_correlations.append(max(correlations))
        if verbose:
            print(
                f"{path}: \n\tmax {max(correlations)}\n\tmean {mean(correlations)}\n\tmin {min(correlations)}"
            )

    print("\nModes to test, in order:")
    for i in range(len(max_correlations)):
        max_idx = max_correlations.index(max(max_correlations))
        if max(max_correlations) > 0.1 or verbose:
            path = paths[max_idx]
            htot, vtot = get_htot_vtot(path)
            freq = pxclock = htot*vtot*get_fps(path)
            while freq < HARMONIC_THRESHOLD:  
                freq += pxclock
            print(
                f"{i+1}. {bcolors.OKBLUE}{path}{bcolors.ENDC}: {max_correlations[max_idx]:.3f} \t total resolution {bcolors.OKBLUE}{htot}x{vtot}@{get_fps(path)}{bcolors.ENDC}\t freq {bcolors.OKGREEN}{freq}{bcolors.ENDC}"
            )
        max_correlations[max_idx] = -99
