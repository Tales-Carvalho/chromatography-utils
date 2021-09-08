import glob
import os
import pandas as pd

TIME_COLUMN = 'RT' # Must have the same name in input files and data/database.csv
PEAK_COLUMN = 'Area' # Column used for peak detection, must only be present in input files


def gas_analysis(experiment):
  inputFiles = sorted(glob.glob(f'input/{experiment}/*.TX0'))
  summaryDf = pd.DataFrame()

  tcdDatabases = sorted(glob.glob('data/tcd/*.csv'))
  if len(tcdDatabases) == 0:
    raise Exception('No database found in data/tcd folder.')

  fidDatabases = sorted(glob.glob('data/fid/*.csv'))
  if len(fidDatabases) == 0:
    raise Exception('No database found in data/fid folder.')

  for num in range(3):
    # TCD data file
    print('Avaliable files:')
    print('; '.join(
      [f'[{i+1}] {os.path.basename(f)}' for i, f in enumerate(inputFiles)]
    ))
    while True:
      try:
        fileNum = int(input(f'Select file for TCD analysis of sample {num+1} of {experiment} (type 0 to end analysis of this experiment): '))
        assert fileNum >= 0 and fileNum <= len(inputFiles)
        break
      except (ValueError, AssertionError):
        print('Error: invalid file number. Try again.')

    if fileNum == 0:
      break

    # Internal variables for processing
    tcdFileName = inputFiles[fileNum-1]
    tcdFileDf = pd.read_csv(
      tcdFileName, encoding='latin1', skiprows=15, header=None,
      names=[TIME_COLUMN, PEAK_COLUMN], usecols=[1,2]
    )
    tcdFileDf = tcdFileDf.apply(pd.to_numeric, errors='coerce').dropna().sort_values(by=[TIME_COLUMN])
    tcdInputDf = tcdFileDf.copy()
    tcdResultsDf = pd.DataFrame()

    # Database choice
    print('Available databases:')
    print('; '.join(
      [f'[{i+1}] {os.path.basename(database)}' for i, database in enumerate(tcdDatabases)]
    ))
    try:
      databaseNum = int(input('Database number (default=1): '))
      assert databaseNum > 0 and databaseNum <= len(tcdDatabases)
    except (ValueError, AssertionError):
      print(f'Warning: invalid number, [1] {os.path.basename(tcdDatabases[0])} will be used.')
      databaseNum = 1
    tcdDatabase = pd.read_csv(tcdDatabases[databaseNum-1])

    # TCD Analysis
    for _, inputRow in tcdInputDf.iterrows():
      # Find closest row in tcdDatabase to inputRow[TIME_COLUMN]
      rowResult = tcdDatabase.iloc[(tcdDatabase[TIME_COLUMN]-inputRow[TIME_COLUMN]).abs().argsort()[:1]]
      tcdResultsDf = tcdResultsDf.append(
        pd.concat([inputRow, rowResult.squeeze().drop([TIME_COLUMN])]), ignore_index=True
      )
      # Filter out found compounds in tcdDatabase
      tcdDatabase = tcdDatabase[(tcdDatabase[TIME_COLUMN].isin(tcdResultsDf[TIME_COLUMN]) == False)]

    # FID data file
    print('Avaliable files:')
    print('; '.join(
      [f'[{i+1}] {os.path.basename(f)}' for i, f in enumerate(inputFiles)]
    ))
    while True:
      try:
        fileNum = int(input(f'Select file for FID analysis of sample {num+1} of {experiment}: '))
        assert fileNum > 0 and fileNum <= len(inputFiles)
        break
      except (ValueError, AssertionError):
        print('Error: invalid file number. Try again.')
    
    # Internal variables for processing
    fidFileName = inputFiles[fileNum-1]
    fidFileDf = pd.read_csv(
      fidFileName, encoding='latin1', skiprows=15, header=None,
      names=[TIME_COLUMN, PEAK_COLUMN], usecols=[1,2]
    )
    fidFileDf = fidFileDf.apply(pd.to_numeric, errors='coerce').dropna().sort_values(by=[TIME_COLUMN])
    fidInputDf = fidFileDf.copy()
    fidResultsDf = pd.DataFrame()

    # Database choice
    print('Available databases:')
    print('; '.join(
      [f'[{i+1}] {os.path.basename(database)}' for i, database in enumerate(fidDatabases)]
    ))
    try:
      databaseNum = int(input('Database number (default=1): '))
      assert databaseNum > 0 and databaseNum <= len(fidDatabases)
    except (ValueError, AssertionError):
      print(f'Warning: invalid number, [1] {os.path.basename(fidDatabases[0])} will be used.')
      databaseNum = 1
    fidDatabase = pd.read_csv(fidDatabases[databaseNum-1])

    # FID Analysis
    for _, inputRow in fidInputDf.iterrows():
      # Find closest row in fidDatabase to inputRow[TIME_COLUMN]
      rowResult = fidDatabase.iloc[(fidDatabase[TIME_COLUMN]-inputRow[TIME_COLUMN]).abs().argsort()[:1]]
      fidResultsDf = fidResultsDf.append(
        pd.concat([inputRow, rowResult.squeeze().drop([TIME_COLUMN])]), ignore_index=True
      )

    # Get from the user: mass of sample and volume of sample
    while True:
      try:
        sampleMass = float(input('Mass of sample [g]: '))
        assert sampleMass > 0
        break
      except (ValueError, AssertionError):
        print('Error: invalid value. Try again.')
    while True:
      try:
        sampleVol = float(input('Volume of sample [mL]: ')) # TODO: mL?
        assert sampleVol > 0
        break
      except (ValueError, AssertionError):
        print('Error: invalid value. Try again.')

    # Volume and Mass of each compound
    fidResultsDf['Volume'] = fidResultsDf['Area'] / fidResultsDf['Response Factor']
    fidResultsDf['Volume in Sample'] = fidResultsDf['Volume'] * sampleVol / 5
    fidResultsDf['Mass'] = fidResultsDf['Volume in Sample'] * fidResultsDf['Density']
    tcdResultsDf['Volume'] = tcdResultsDf['Area'] / tcdResultsDf['Response Factor']
    tcdResultsDf['Volume in Sample'] = tcdResultsDf['Volume'] * sampleVol / 5
    tcdResultsDf['Mass'] = tcdResultsDf['Volume in Sample'] * tcdResultsDf['Density']

    # Save csv table in output folder, using the input directory template
    os.makedirs(f'output/{experiment}/', exist_ok=True)
    tcdResultsDf.to_csv(f'output/{experiment}/{os.path.basename(tcdFileName).replace(".TX0", ".csv")}', index=False)
    fidResultsDf.to_csv(f'output/{experiment}/{os.path.basename(fidFileName).replace(".TX0", ".csv")}', index=False)
    print(f'File saved to output/{experiment}/{os.path.basename(tcdFileName).replace(".TX0", ".csv")}')
    print(f'File saved to output/{experiment}/{os.path.basename(fidFileName).replace(".TX0", ".csv")}')

    # Isolate specific compound
    compoundsToIsolate = ['None', 'Nitrogen', 'Isobutylene', '1-Butene', '1,3-Butadiene', 'Butane', 'Isobutane']
    print('Isolate specific compound in analysis?')
    print('; '.join([f'[{i}] {c}' for i, c in enumerate(compoundsToIsolate)]))
    try:
      compoundNum = int(input('Compound number (default=0): '))
      assert compoundNum >= 0 and compoundNum < len(compoundsToIsolate)
    except (ValueError, AssertionError):
      print('Warning: invalid value. [0] None will be considered.')
      compoundNum = 0
    
    if compoundNum != 0:
      tcdResultsDf.loc[tcdResultsDf['Compound'] == compoundsToIsolate[compoundNum], 'Classification'] = compoundsToIsolate[compoundNum]
      fidResultsDf.loc[fidResultsDf['Compound'] == compoundsToIsolate[compoundNum], 'Classification'] = compoundsToIsolate[compoundNum]

    # Merge results to a single table
    thisSummaryDf = pd.merge(
      fidResultsDf.groupby('Classification')[['Mass']].sum(),
      tcdResultsDf.groupby('Classification')[['Mass']].sum(),
      'outer',
      ['Classification', 'Mass']
    )

    # Append unaccounted row 
    thisSummaryDf = thisSummaryDf.append(pd.Series(data={
      'Mass': sampleMass - thisSummaryDf[['Mass']].sum().squeeze()
    }, name='Unaccounted'))

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

  summaryDf.to_excel(f'output/{experiment}_summary.xlsx')
  print(f'Summary saved to output/{experiment}_summary.xlsx')


def liquid_analysis(experiment):
  inputFiles = sorted(glob.glob(f'input/{experiment}/*.csv'))
  summaryDf = pd.DataFrame()

  databases = sorted(glob.glob('data/liquid/*.csv'))
  if len(databases) == 0:
    raise Exception('No database found in data/liquid folder.')

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

  summaryDf.to_excel(f'output/{experiment}_summary.xlsx')
  print(f'Summary saved to output/{experiment}_summary.xlsx')
