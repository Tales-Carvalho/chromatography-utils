#!/bin/python3

import glob
import os
from matplotlib import pyplot as plt


def liquid_plot(experiment):
  raxFiles = sorted(glob.glob(f'input/{experiment}/*.RAX'))
  print(raxFiles)


def gas_plot(experiment):
  raxFiles = sorted(glob.glob(f'input/{experiment}/*.RAX'))
  print(raxFiles)

