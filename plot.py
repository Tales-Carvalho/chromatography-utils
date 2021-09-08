#!/bin/python3

import glob
import os
import numpy as np
from matplotlib import pyplot as plt

LIQUID_FREQ = 6.25 # in Hz
GAS_FREQ = 3.125 # in Hz


def readRaxFile(raxFile, gas=False):
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
  if gas:
    t = np.arange(len(points)) / (GAS_FREQ * 60)
  else:
    t = np.arange(len(points)) / (LIQUID_FREQ * 60)
  return [t, np.array(points)]


def liquid_plot(experiment):
  raxFiles = sorted(glob.glob(f'input/{experiment}/*.RAX'))
  
  series = []

  for raxFile in raxFiles:
    series.append(readRaxFile(raxFile))

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

  print(f'Plot saved to output/{experiment}_plot.png.')
  print('Close the figure window to continue the program.')

  plt.show()


def gas_plot(experiment):
  raxFiles = sorted(glob.glob(f'input/{experiment}/*.RAX'))
  
  tcdSeries = []
  fidSeries = []
  tcdFiles = []
  fidFiles = []

  for num in range(3):
    print('Avaliable files:')
    print('; '.join(
      [f'[{i+1}] {os.path.basename(f)}' for i, f in enumerate(raxFiles)]
    ))
    while True:
      try:
        fileNum = int(input(f'Select TCD analysis file of sample {num+1} of {experiment}: '))
        assert fileNum > 0 and fileNum <= len(raxFiles)
        break
      except (ValueError, AssertionError):
        print('Error: invalid file number. Try again.')
    tcdFiles.append(raxFiles[fileNum-1])
    tcdSeries.append(readRaxFile(raxFiles[fileNum-1], True))

    while True:
      try:
        fileNum = int(input(f'Select FID analysis file of sample {num+1} of {experiment}: '))
        assert fileNum > 0 and fileNum <= len(raxFiles)
        break
      except (ValueError, AssertionError):
        print('Error: invalid file number. Try again.')
    fidFiles.append(raxFiles[fileNum-1])
    fidSeries.append(readRaxFile(raxFiles[fileNum-1], True))

  plt.figure(figsize=(16,8))

  ax1 = plt.subplot(len(tcdFiles), 2, 2 * len(tcdFiles) - 1)
  plt.plot(tcdSeries[0][0], tcdSeries[0][1], label=os.path.basename(tcdFiles[0]))
  plt.legend()

  for i in range(1, len(tcdSeries)):
    ax = plt.subplot(len(tcdSeries), 2, 2 * (len(tcdSeries) - i) - 1, sharex=ax1, sharey=ax1)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.plot(tcdSeries[i][0], tcdSeries[i][1], label=os.path.basename(tcdFiles[i]))
    plt.legend()

  plt.title(f'{experiment}_TCD')

  ax2 = plt.subplot(len(fidFiles), 2, 2 * len(fidFiles))
  plt.plot(fidSeries[0][0], fidSeries[0][1], label=os.path.basename(fidFiles[0]))
  plt.legend()

  for i in range(1, len(fidSeries)):
    ax = plt.subplot(len(fidSeries), 2, 2 * (len(fidSeries) - i), sharex=ax2, sharey=ax2)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.plot(fidSeries[i][0], fidSeries[i][1], label=os.path.basename(fidFiles[i]))
    plt.legend()

  plt.title(f'{experiment}_FID')

  plt.savefig(f'output/{experiment}_plot.png')
  print(f'Plot saved to output/{experiment}_plot.png.')
  print('Close the figure window to continue the program.')

  plt.show()
