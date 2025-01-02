#!/bin/python3

# Project metadata
PROJECT = dict(
  name = 'chromatography-utils',
  version = '0.4.1',
  description = 'Utility for chromatography analysis written in Python',
  authors = ['Tales Carvalho <taleshen@ualberta.ca>'],
  readme = 'README.md'
)

import glob
import os

import analysis
import plot

def entrypoint():

  # Get experiments subfolders from input folder
  experiments = sorted([p.split(os.sep)[1] for p in glob.glob(os.path.join('input', '*'))])  
  if len(experiments) == 0:
    raise Exception('No experiment found in input folder.')
  print(f'Found {len(experiments)} experiment folders: {"; ".join(experiments)}')

  print('Available functions: (1) peak analysis; (2) plot; (3) both.\n')
  try:
    funNum = int(input('Function number for this execution (default=1): '))
    assert funNum >= 1 and funNum <= 3
  except (ValueError, AssertionError):
    print('Warning: invalid number, (1) peak analysis will be considered.')
    funNum = 1

  if funNum == 1 or funNum == 3:
    for experiment in experiments:
      print(f'\nExecuting peak analysis function for {experiment}.')
      skip = 'n'
      if os.path.exists(os.path.join('output', f'{experiment}_summary.xlsx')):
        skip = 'y'
        skip = input(f'\nOutput for {experiment} already exists. Skip? [Y,n] ')
      if skip == 'n' or skip == 'N':
        print('Available experiment types: (1) liquid; (2) gas.\n')
        try:
          expType = int(input(f'Type number for experiment {experiment} (default=1): '))
          assert expType == 1 or expType == 2
        except (ValueError, AssertionError):
          print('Warning: invalid number, (1) liquid will be used.')
          expType = 1

        try:
          if expType == 1:
            analysis.liquid_analysis(experiment)
          else:
            analysis.gas_analysis(experiment)
        except Exception as e:
          print('Error:', e)
          print('Skipping to next experiment.')
      else:
        print('Skipping.')

  if funNum == 2 or funNum == 3:
    for experiment in experiments:
      print(f'\nExecuting plot function for {experiment}.')
      skip = 'n'
      if os.path.exists(os.path.join('output', f'{experiment}_plot.png')) or os.path.exists(os.path.join('output', f'{experiment}_TCD_plot.png')):
        skip = 'y'
        skip = input(f'\nOutput for {experiment} already exists. Skip? [Y,n] ')
      if skip == 'n' or skip == 'N':
        print('Available experiment types: (1) liquid; (2) gas.\n')
        try:
          expType = int(input(f'Type number for experiment {experiment} (default=1): '))
          assert expType == 1 or expType == 2
        except (ValueError, AssertionError):
          print('Warning: invalid number, (1) liquid will be used.')
          expType = 1

        try:
          if expType == 1:
            plot.liquid_plot(experiment)
          else:
            plot.gas_plot(experiment)
        except Exception as e:
          print('Error:', e)
          print('Skipping to next experiment.')
      else:
        print('Skipping.')


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
