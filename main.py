import glob
import os
import pandas as pd

if __name__ == '__main__':

  if not os.path.exists('data/database.csv'):
    print('data/database.csv not found. Exiting.')
    exit(1)
  dbDf = pd.read_csv('data/database.csv')

  if not os.path.exists('data/rrf.csv'):
    print('data/rrf.csv not found. Exiting.')
    exit(1)
  rrfDf = pd.read_csv('data/rrf.csv')

  mergedDf = pd.merge(dbDf, rrfDf, 'inner', ['nC', 'Classification']).sort_values(by=['RT'])
  mergedDf.to_csv('merged.csv')

  inputFiles = glob.glob('input/*.csv')
  print(f'Found {len(inputFiles)} input files:')
  [print(f'\t* {os.path.basename(f)}') for f in inputFiles]

  for f in inputFiles:
    print(f'Processing {os.path.basename(f)}...')
    df = pd.read_csv(f)

    # TODO: filter df with local maxima, and process with merge_asof in filtered df

    outDf = pd.merge_asof(
      mergedDf[['RT', 'nC', 'Classification', 'Compound', 'RRF']].rename(columns={'RT': 'RT_db'}),
      df,
      left_on='RT_db',
      right_on='RT',
      direction='nearest').drop('RT_db', axis=1)

    outDf = pd.merge(df, outDf, 'outer', ['RT', 'Height', 'Area']).sort_values(by=['RT'])

    outDf.to_csv(f'output/{os.path.basename(f)}', index=False)
    print(f'File saved to output/{os.path.basename(f)}')
