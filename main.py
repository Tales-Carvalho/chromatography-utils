import glob
import os
import pandas as pd

TIME_COLUMN = 'RT' # Must have the same name in input files and data/database.csv
PEAK_COLUMN = 'Area' # Column used for peak detection, must only be present in input files

if __name__ == '__main__':

  if not os.path.exists('data/database.csv'):
    print('data/database.csv not found. Exiting.')
    exit(1)
  database = pd.read_csv('data/database.csv')

  # Find all csv files in input directory
  inputFiles = glob.glob('input/*.csv')
  print(f'Found {len(inputFiles)} input files:')
  for f in inputFiles:
    print(f'\t* {os.path.basename(f)}')

  for f in inputFiles:
    print(f'Processing {os.path.basename(f)}...')
    fileDf = pd.read_csv(f).sort_values(by=[TIME_COLUMN])

    # Internal variables for processing
    inputDf = fileDf.copy()
    resultsDf = pd.DataFrame()

    for _, dbRow in database.iterrows():  
      # Select only local Area peaks from inputDf
      filteredDf = inputDf[
        (inputDf.shift(1, fill_value=0)[PEAK_COLUMN] < inputDf[PEAK_COLUMN]) &
        (inputDf.shift(-1, fill_value=0)[PEAK_COLUMN] < inputDf[PEAK_COLUMN])
      ]
      # Find closest row in filteredDf to dbRow[TIME_COLUMN]
      rowResult = filteredDf.iloc[(filteredDf[TIME_COLUMN]-dbRow[TIME_COLUMN]).abs().argsort()[:1]]
      resultsDf = resultsDf.append(
        pd.concat([dbRow.drop([TIME_COLUMN]), rowResult.squeeze()]), ignore_index=True
      )
      # Filter out found compounds in inputDf
      inputDf = inputDf[(inputDf[TIME_COLUMN].isin(resultsDf[TIME_COLUMN]) == False)]

    # Merge results with input file, so unclassified compounds are still present in output
    resultsDf = pd.merge(
      fileDf,
      resultsDf,
      'outer',
      fileDf.keys().tolist()
    ).sort_values(by=[TIME_COLUMN])

    resultsDf.to_csv(f'output/{os.path.basename(f)}', index=False)
    print(f'File saved to output/{os.path.basename(f)}')
