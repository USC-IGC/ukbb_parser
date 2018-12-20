# UK Biobank Data Parser
#### Contact: Alyssa Zhu <alyssahz@usc.edu>

The UK Biobank Data Parser (ukbb_parser) is a python-based package that allows easy interfacing with the large UK Biobank dataset.

To avoid repetitive calls for standard demographic variables, we created default output columns for sex, age at the time of the neuroimaging scan, race/ethnicity, and education. Race (Data-Field 21000) is coded first by the larger race group due to inconsistent reporting of ethnicity. Education (Data-Field 6138) is coded according to educational levels in the United Kingdom. These levels are converted to standardized education levels based on the International Standard Classification of Education framework, and estimated years of education is derived using the conversion strategy published by Okbay et al. (2016).

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

Required Inputs:
* `-i, --incsv CSV`          File path of the downloaded UK Biobank data csv
* `-o, --out TEXT`           Output prefix

Optional Inputs:
* `--incon ICD10Code`        ICD10 Diagnosis codes you wish to include. Least 
                           common denominators are acceptable, e.g. --incon F. 
                           Ranges are also acceptable inputs. Please include 
                           chapters for both ends, e.g. F10-F20
* `--excon ICD10Code`        ICD10 Diagnosis codes you wish to exclude. Least 
                           common denominators are acceptable, e.g. --incon F. 
                           Ranges are also acceptable inputs. Please include 
                           chapters for both ends, e.g. F10-F20
* `--insr SRCode`            Self-Report codes you wish to include. Ranges are
                           acceptable inputs.
* `--exsr SRCode`            Self-Report codes you wish to exclude. Ranges are
                           acceptable inputs.
* `--incat Category`         Categories you wish to include. Ranges are
                           acceptable inputs, e.g. 100-200
* `--excat Category`         Categories you wish to exclude. Ranges are
                           acceptable inputs, e.g. 100-200
* `--inhdr HeaderName`       Columns names you wish to include. Ranges are
                           acceptable inputs, e.g. 100-200
                           If you wish to have
                           all the available data, please use --inhdr all
* `--exhdr HeaderName`       Columns names you wish to exclude. Ranges are
                           acceptable inputs, e.g. 100-200
* `--subjects SubID`         A list of participant IDs to include
* `--dropouts dropouts`      CSV(s) containing eids of participants who have
                           dropped out of the study
* `--icd10_count ICD10Code`  Create a binary column for the specified ICD10
                           conditions only. Ranges can cross consecutive
                           letters, e.g. A00-B99. Ranges within a letter
                           should be specified, A00-A99. A single letter will
                           create a binary column for that group of diseases.
                           Give the input as 'all' to create a column for
                           every self-report condition
* `--sr_count SRCode`        Create a binary column for the specified self-
                           report conditions only. Ranges are acceptable
                           inputs. Give the input as 'all' to create a column
                           for every self-report condition
* `--img_subs_only`          Use this flag to only keep data of participants
                           with an imaging visit.
* `--img_visit_only`         Use this flag to only keep data acquired during the
                           imaging visit.
* `--fillna TEXT`            Use this flag to fill blank cells with the flag
                           input, e.g., NA
* `--combine Spreadsheet`    Spreadsheets to combine to output; Please make sure
                           all spreadsheets have an identifier column 'eid'

### update

The **update** subcommand will combine and/or update CSV files that were downloaded at different times (e.g., after a refresh).

Inputs:
* `--previous CSV`  File path of previous downloaded UK Biobank CSV
* `--new CSV`       File path of new downloaded UK Biobank CSV or a CSV of processed results
* `--output CSV`    File path to write newly updated CSV to

### check

The **check** subcommand will determine if the queried Datafield is included in the downloaded CSV file.

Inputs:
* `--incsv CSV`     File path of downloaded UK Biobank CSV
* `--datafield df`  Datafield to check for

### create_cohorts

In Development

## References 

Okbay, A., Beauchamp, J. P., Fontana, M. A., Lee, J. J., Pers, T. H., Rietveld, C. A., ... & Oskarsson, S. (2016). Genome-wide association study identifies 74 loci associated with educational attainment. Nature, 533(7604), 539.

## Acknowledgments 

This package is developed using the UK Biobank Resource under Application Number 11559.
