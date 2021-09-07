#!/bin/python3

import glob
import os
import numpy as np
from matplotlib import pyplot as plt

LIQUID_FREQ = 6.25 # in Hz
GAS_FREQ = 3.125 # in Hz


def liquid_plot(experiment):
  raxFiles = sorted(glob.glob(f'input/{experiment}/*.RAX'))
  
  series = []
  for raxFile in raxFiles:
    points = []
    with open(raxFile) as f:
      l = f.readline()
      while l != '[Raw Data Points]\n':
        l = f.readline()
        if not l:
          raise Exception(f'No Data Points found in file {raxFile}')
      f.readline() # Skip one line
      while True:
        try:
          points.append(int(f.readline()))
        except ValueError:
          break
    t = np.arange(len(points)) / (LIQUID_FREQ * 60)
    series.append([t, np.array(points)])

  plt.figure(figsize=(12,8))

  ax1 = plt.subplot(len(raxFiles), 1, len(raxFiles))
  plt.plot(series[0][0], series[0][1], label=os.path.basename(raxFiles[0]))
  plt.legend()

  for i in range(1, len(series)):
    ax = plt.subplot(len(series), 1, len(series) - i, sharex=ax1, sharey=ax1)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.plot(series[i][0], series[i][1], label=os.path.basename(raxFiles[i]))
    plt.legend()

  plt.title(experiment)
  plt.savefig(f'output/{experiment}_plot.png')
  plt.show()


def gas_plot(experiment):
  raxFiles = sorted(glob.glob(f'input/{experiment}/*.RAX'))
  print(raxFiles)
