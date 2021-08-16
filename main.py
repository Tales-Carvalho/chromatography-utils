import glob
import os
import pandas as pd

if __name__ == '__main__':

  if not os.path.exists('data/database.csv'):
    print('data/database.csv not found. Exiting.')
    exit(1)
  database = pd.read_csv('data/database.csv')

  inputFiles = glob.glob('input/*.csv')
  print(f'Found {len(inputFiles)} input files:')
  for f in inputFiles:
    print(f'\t* {os.path.basename(f)}')

  for f in inputFiles:
    print(f'Processing {os.path.basename(f)}...')
    fileDf = pd.read_csv(f).sort_values(by=['RT'])

    inputDf = fileDf.copy()
    resultsDf = pd.DataFrame()

    for index, dbRow in database.iterrows():  
      # Select only local Area peaks from inputDf
      filteredDf = inputDf[
        (inputDf.shift(1, fill_value=0)['Area'] < inputDf['Area']) &
        (inputDf.shift(-1, fill_value=0)['Area'] < inputDf['Area'])
      ]
      # Find closest row in filteredDf to dbRow['RT']
      rowResult = filteredDf.iloc[(filteredDf['RT']-dbRow['RT']).abs().argsort()[:1]]
      resultsDf = resultsDf.append(
        pd.concat([dbRow.drop(['RT']), rowResult.squeeze()]), ignore_index=True
      )
      # Filter out found compounds in inputDf
      inputDf = inputDf[(inputDf['RT'].isin(resultsDf['RT']) == False)]

    resultsDf = pd.merge(fileDf, resultsDf, 'outer', ['RT', 'Height', 'Area']).sort_values(by=['RT'])
    resultsDf.to_csv(f'output/{os.path.basename(f)}', index=False)
    print(f'File saved to output/{os.path.basename(f)}')
