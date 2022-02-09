# UK Biobank Data Parser
#### Contact: Alyssa Zhu <alyssahz@usc.edu>

The UK Biobank Data Parser (**ukbb_parser**) is a python-based package that allows easy interfacing with the large UK Biobank dataset (Zhu et al., OHBM 2019).

To avoid repetitive calls for standard demographic variables, we created default output columns for sex (self-reported and genetic), age at the time of the neuroimaging scan, race/ethnicity, and education. Self-reported race (Data-Field 21000) is coded first by the larger race group due to inconsistent reporting of ethnicity. Genetic ethnic grouping (Data-Field 22006) and the first 10 genetic principal components (Data-Field 22009) are also provided. Education (Data-Field 6138) is coded according to educational levels in the United Kingdom. These levels are converted to standardized education levels based on the International Standard Classification of Education framework, and estimated years of education is derived using the conversion strategy published by Okbay et al. (2016).

See **ReleaseNotes.md** for version updates.

## How to cite 

Zhu, A.H., Salminen, L.E., Thompson, P.M., Jahanshad, N. "The UK Biobank Data Parser: a tool with built in and customizable filters for brain studies." (2019) Organization for Human Brain Mapping. Rome, Italy, June 9-13, 2019.

## Requirements

Please note that this parser uses the Click package, which sometimes has problems installing with Python 3.7. Any Python version <=3.6 will be compatible.

## Installation 

As this package has not been added to PyPI, please follow the instructions below carefully.

Two-step process:
1. To clone the repository:
`git clone https://github.com/USC-IGC/ukbb_parser.git`

2. After downloading or cloning (in the same directory that `git clone` was run in):
`pip install ./ukbb_parser`

One-step process:
`pip install git+https://github.com/USC-IGC/ukbb_parser.git`

N.B. The above installation commands will require administrator/root privileges of the system. If you don't have administrator/root privileges, please try adding the `--user` flag.

Example:
`pip install --user ./ukbb_parser`

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

The output csv will contain a set of default columns: eid, age at visits, race, education levels, healthy control cohorts (see output HTML for more details), and sex. 

Required Inputs:
* `-i, --incsv CSV`          File path of the downloaded UK Biobank data csv
* `-o, --out TEXT`           Output prefix

Optional Inputs:
* `--incon ICD10Code`        ICD10 Diagnosis codes you wish to include. Least 
                           common denominators are acceptable, e.g. --incon F. 
                           Ranges are also acceptable inputs, e.g., F10-F20,
                           and can span across letters
* `--excon ICD10Code`        ICD10 Diagnosis codes you wish to exclude. Least 
                           common denominators are acceptable, e.g. --incon F. 
                           Ranges are also acceptable inputs, e.g., F10-F20, 
                           and can span across letters
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
* `--img_subs_only`          Use this flag to only keep data of participants
                           with an imaging visit.
* `--img_visit_only`         Use this flag to only keep data acquired during the
                           imaging visit.
* `--no_convert`             Use this flag if you don't want the demographic conversions run
* `--long_names`             Use this flag to replace datafield numbers in column names with datafield titles
* `--rcols`                  Use this flag if spreadsheet has columns names under R convention (e.g., "X31.0.0")
* `--fillna TEXT`            Use this flag to fill blank cells with the flag
                           input, e.g., NA
* `--chunksize INTEGER`     Use this flag to set the processing chunk size,
                            Default:1000


The incon/excon/insr/exsr/incat/excat/inhdr/exhdr/combine flags can all be used multiple times, e.g., `--incat 110 --incat 134`.

Example usage:
 
`ukbb_parser parse --incsv ukbb_spreadsheet.csv -o ukbb_subset --incat 100 --excat 135 --incon G35`

### inventory

The **inventory** subcommand will create binary columns indicating the presence of specified data. The data that can be inventoried are _ICD-10 conditions, self-report (non-cancer) conditions, and careers_. 

As can be viewed on [the UK Biobank data showcase](http://biobank.ctsu.ox.ac.uk/crystal/index.cgi), these data are organized in a hierarchical tree structure with five levels. At the end of each of the branches are selectable codes, i.e., codes that are used in and can be queried for in the UK Biobank data spreadsheet. By default, the **inventory** subcommand will aggregate all selectable codes within the requested level/code input into a single binary column. To obtain a column for the aggregate column _and_ an additional column for each of the selectable codes within the requested level/code combination, please use `--all_codes`. All selectable codes regardless of level can also be obtained using `--level S --code all`.

Code inputs should be derived from the datafield-specific coding pages available on the UK Biobank showcase. If there are spaces in the codes, please use quotes around the entry (see example below). Multiple levels and codes can be used at once, but please ensure that levels and codes are provided in corresponding pairs.

N.B. If `--long_names` has been used in the creation of an input spreadsheet for **inventory**, the code will not work.

#### ICD-10 

The coding tree for the ICD-10 conditions can be viewed in part on the pages of either of the datafields ([41202](http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41202) and [41204](http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41204)) or on the [coding page](http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id=19).

_Notes_
* For top level codes (`--level 0`), use the chapter number as the `--code` input, e.g., "Chapter II" to indicate "Neoplasms".
* For Level 1 (`--level 1`), add "Block" to the beginning of the `--code` input, e.g., "Block A00-09" to indicate "Intestinal infectious diseases"

#### Self-Report (non-cancer)

The coding tree for the self-report (non-cancer) conditions can be viewed on [the datafield page](http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=20002) or on the [coding page](http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id=6).

_Notes_
* As can be seen on the coding page, the upper levels of the self-report conditions have non-unique codes (-1). Please use the "Meaning" as the `--code` input instead. 

#### Careers

The coding tree for careers can be viewed on the datafield pages ([132](http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=132) and [22617](http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=22617)) or on the [coding page](http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id=2). Please note that the coding on the coding page is only available to logged-in users.

Also note that this inventory binarization only produces one column per job code, i.e., a job code will be noted as present so long as it has been indicated in any of the visits/instances.

##### Flags and Usage

Inputs:
* `--incsv CSV`            File path of downloaded UK Biobank CSV
* `--outcsv CSV`           File path to write out to
* `--rcols`                Use this flag if spreadsheet has columns names under R convention (e.g., "X31.0.0")
* `--datatype type`        Data to inventory; Valid choices include: icd10,
                          self_report, careers
* `--level level`          Level to inventory by; N.B. Please input 0 for the Top
                          level or S for selectable codes
* `--code code`            Codes to inventory; Use the option 'all' to inventory all
                          categories in the given level; Please use level-appropriate
                          codes; Ranges are allowed for selectable codes
* `--all_codes`            (optional) Use this flag if you'd like to additionally obtain
                         individual inventories of all codes
* `--chunksize INTEGER`     Use this flag to set the processing chunk size,
                            Default:1000

Example usage:

`ukbb_parser inventory --incsv ukbb_spreadsheet.csv --outcsv jobs_inventory.csv --datatype careers --level 3 --code 6113`

`ukbb_parser inventory --incsv ukbb_spreadsheet.csv --outcsv jobs_inventory.csv --datatype careers --level 3 --code 6113 --level 4 --code 1151010 --all_codes`

`ukbb_parser inventory --incsv ukbb_spreadsheet.csv --outcsv icd10_inventory.csv --datatype icd10 --level 0 --code "Chapter V" --level 1 --code "Block G00-G09"`

`ukbb_parser inventory --incsv ukbb_spreadsheet.csv --outcsv jobs_inventory.csv --datatype self_report --level S --code all`

### update

The **update** subcommand will combine and/or update CSV files that were downloaded at different times (e.g., after a refresh).

Inputs:
* `--previous CSV`  File path of previous downloaded UK Biobank CSV
* `--new CSV`       File path of new downloaded UK Biobank CSV or a CSV of processed results
* `--outcsv CSV`    File path to write newly updated CSV to

Example usage:

`ukbb_parser update --previous ukbb_2018_spreadsheet.csv --new ukbb_2019_spreadsheet.csv --outcsv combined_ukbb_2018_2019_spreadsheet.csv`

### check

The **check** subcommand will determine if the queried Datafield or Category is included in the downloaded CSV file.

Inputs:
* `--incsv CSV`     File path of downloaded UK Biobank CSV
* `--datafield df`  Datafield to check for
* `--category cat`  Category to check for

Example usage:

`ukbb_parser check --incsv ukbb_spreadsheet.csv --datafield 31`
`ukbb_parser check --incsv ukbb_spreadsheet.csv --category 100`

### create_cohorts

In Development

## References 

Zhu, A.H., Salminen, L.E., Thompson P.M., Jahanshad N. "The UK Biobank Data Parser: a tool with built in and customizable filters for brain studies." (2019) Organization for Human Brain Mapping. Rome, Italy, June 9-13, 2019.

Okbay, A., Beauchamp, J.P., Fontana, M.A., Lee, J.J., Pers, T.H., Rietveld, C.A., ... & Oskarsson, S. (2016). Genome-wide association study identifies 74 loci associated with educational attainment. Nature, 533(7604), 539.

## Acknowledgments 

This package is developed using the UK Biobank Resource under Application Number 11559.

Funding was provided in part by NIH R01-AG059874 (Jahanshad).
