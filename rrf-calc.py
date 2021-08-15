import glob
import os
import pandas as pd

if __name__ == '__main__':
  inputFiles = glob.glob('input/*.csv')
  print(f'Found {len(inputFiles)} input files:')
  [print(f'\t{os.path.basename(f)}') for f in inputFiles]

  for f in inputFiles:
    df = pd.read_csv(f)

    df['Classification'] = '---'
    df['RRF'] = 1

    df.to_csv(f'output/{os.path.basename(f)}', index=False)