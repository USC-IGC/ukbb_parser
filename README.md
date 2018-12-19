# UK Biobank Data Parser
#### Contact: Alyssa Zhu <alyssahz@usc.edu>

The UK Biobank Data Parser (ukbb_parser) is a python-based package that allows easy interfacing with the large UK Biobank dataset.

## Installation 

After downloading or cloning:
`pip install ukbb_parser`

## Usages

### Display available subcommands
`ukbb_parser --help`

### Display flags/options for a specific subcommand
`ukbb_parser [subcommand] --help`

### Use subcommand
`ukbb_parser [subcommand] [--flags inputs]`

## Subcommands

### parse

The **parse** subcommand will filter the input CSV file with the given input parameters.

### update

The **update** subcommand will combine and/or update CSV files that were downloaded at different times (e.g., after a refresh).

### check

The **check** subcommand will determine if the queried Datafield is included in the downloaded CSV file.

### create_cohorts

In Development

## Acknowledgments 

This package is developed using the UK Biobank Resource under Application Number 11559.
