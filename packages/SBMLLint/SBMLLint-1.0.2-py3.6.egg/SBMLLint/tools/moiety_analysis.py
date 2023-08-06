#!/usr/bin/env python
"""
Runs moiety analysis for a local XML file.
Usage: moiety_analysis <filepath>
"""

import add_path
from SBMLLint.tools import sbmllint

import argparse

def main():
  parser = argparse.ArgumentParser(description='SBML XML file.')
  parser.add_argument('filename', type=str, help='SBML file')
  args = parser.parse_args()
  sbmllint.lint(args.filename,
      mass_balance_check=sbmllint.STRUCTURED_NAMES)


if __name__ == '__main__':
  main()
