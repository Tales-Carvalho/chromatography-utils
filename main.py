#!/bin/python3

# Project metadata
PROJECT = dict(
  name = 'chromatography-utils',
  version = '0.2.0',
  description = 'Utility for chromatography analysis written in Python',
  authors = ['Tales Carvalho <taleshen@ualberta.ca>'],
  readme = 'README.md'
)

import glob
import os
import pandas as pd

TIME_COLUMN = 'RT' # Must have the same name in input files and data/database.csv
PEAK_COLUMN = 'Area' # Column used for peak detection, must only be present in input files


def entrypoint():

  # Get databases from data folder
  databases = sorted(glob.glob('data/*.csv'))
  if len(databases) == 0:
    raise Exception('No database found in data folder.')
  print(f'Found {len(databases)} data files: {"; ".join([os.path.basename(d) for d in databases])}')

  # Get experiments subfolders from input folder
  experiments = sorted([p.split('/')[1] for p in glob.glob('input/*/')])  
  if len(experiments) == 0:
    raise Exception('No experiment found in input folder.')
  print(f'Found {len(experiments)} experiment folders: {"; ".join(experiments)}')

  for experiment in experiments:
    # Find all csv files in experiment directory
    inputFiles = sorted(glob.glob(f'input/{experiment}/*.csv'))
    print(f'\nFound {len(inputFiles)} input files for experiment {experiment}.\n')

    summaryDf = pd.DataFrame()

    for num, file in enumerate(inputFiles):
      print(f'Processing {os.path.basename(file)}...')
      fileDf = pd.read_csv(file).sort_values(by=[TIME_COLUMN])

      # Internal variables for processing
      inputDf = fileDf.copy()
      resultsDf = pd.DataFrame()

      # Database choice
      print('Available databases:')
      print("; ".join(
        [f'[{i+1}] {os.path.basename(database)}' for i, database in enumerate(databases)]
      ))
      try:
        databaseNum = int(input('Database number (default=1): '))
        assert databaseNum > 0 and databaseNum <= len(databases)
      except (ValueError, AssertionError):
        print(f'Warning: invalid number, [1] {os.path.basename(databases[0])} will be used.')
        databaseNum = 1

      database = pd.read_csv(databases[databaseNum-1])
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

      # Get area of internal standard from previous resultsDf
      isArea = resultsDf.loc[resultsDf['Classification'] == 'internal standard', 'Area'].squeeze()

      # Get from the user: mass of internal standard and mass of sample
      while True:
        try:
          sampleMass = float(input('Mass of sample [g]: '))
          assert sampleMass > 0
          break
        except (ValueError, AssertionError):
          print('Error: invalid value. Try again.')
      while True:
        try:
          isMass = float(input('Mass of Internal Standard [g]: '))
          assert isMass > 0
          break
        except (ValueError, AssertionError):
          print('Error: invalid value. Try again.')

      # Merge results with input file, so unclassified compounds are still present in output
      resultsDf = pd.merge(
        fileDf,
        resultsDf,
        'outer',
        fileDf.keys().tolist()
      ).sort_values(by=[TIME_COLUMN])

      # Save csv table in output folder, using the input directory template
      os.makedirs(f'output/{experiment}/', exist_ok=True)
      resultsDf.to_csv(f'output/{experiment}/{os.path.basename(file)}', index=False)
      print(f'File saved to output/{experiment}/{os.path.basename(file)}\n')
      
      # Fill empty values of resultsDf
      resultsDf[['RRF']] = resultsDf[['RRF']].fillna(value=1)
      resultsDf[['Classification']] = resultsDf[['Classification']].fillna(value='unidentified')
      
      # Normalized Area and Mass of each compound
      resultsDf['NormalizedArea'] = resultsDf['Area'] / resultsDf['RRF']
      resultsDf['Mass'] = resultsDf['NormalizedArea'] * isMass / isArea

      # Summary
      thisSummaryDf = resultsDf.groupby('Classification')[['Mass']].sum()
      thisSummaryDf = thisSummaryDf.append(pd.Series(data={
        'Mass': sampleMass - resultsDf[['Mass']].sum().squeeze() + isMass
      }, name='unaccounted'))
      thisSummaryDf = thisSummaryDf.append(pd.Series(data={
        'Mass': sampleMass
      }, name='sample'))

      # Identify this summary section
      thisSummaryDf = thisSummaryDf.rename(columns={
        'Mass': f'Mass_{num+1}'
      })

      # Merge this summary with other triplicates
      summaryDf = thisSummaryDf if summaryDf.empty else pd.merge(
        summaryDf,
        thisSummaryDf,
        'outer',
        'Classification'
      )

    summaryDf.to_csv(f'output/{experiment}_summary.csv')
    print(f'Summary saved to output/{experiment}_summary.csv')


if __name__ == '__main__':

  # Print project metadata
  os.system('cls' if os.name == 'nt' else 'clear')
  print(f'Project: {PROJECT["name"]} v{PROJECT["version"]}')
  print(f'Description: {PROJECT["description"]}')
  print(f'Authors: {"; ".join(PROJECT["authors"])}')
  print(f'For more information, read {PROJECT["readme"]} file.')

  print('\n===== Program Start =====\n')
  try:
    entrypoint()
  except Exception as e:
    print('Error:', e)
    raise e
  except KeyboardInterrupt:
    print('\nProgram interrupted.')
  finally:
    print('\n===== Program End =====\n')
