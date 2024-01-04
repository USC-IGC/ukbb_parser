### Release 0.8.0

Updates: 
* [January 3, 2024] Updated the category tree to account for newly available data fields and categories
* [January 3, 2024] Removed datafield 132 as a necessary datafield from the job inventory script

### Release 0.7.0

New Features: 
* [Oct 15, 2020] Changed `ukbb_parser check` to accept multiples and combinations of `--datafield` and `--category` arguments

Bug Fixes:

* [Oct 15, 2020] Fixed time difference calculation for imaging and online cognitive test dates

### Release 0.6.0

New Features: 

* [Sep 23, 2020] Added `--subjects` flag to `ukbb_parser inventory`
* [Sep 23, 2020] Added `--chunksize` flag to `ukbb_parser inventory` and `ukbb_parser parse`
* [Sep 23, 2020] Added `--long_names` flag to `ukbb_parser parse`

Removed Features:

* [Sep 23, 2020] The `--combine` flag has been removed from the parse command 

### Release 0.5.1

* [Feb 26, 2020] Added `--rcols` to `ukbb_parser inventory`
* [Feb 26, 2020] Added funcionality for fourth visit (i.e., second imaging visit)
* [Feb 26, 2020] Edited `ukbb_parser parse` control assignments to account for missing datafields

### Release 0.5.0

* [Jan 15, 2020] Updated datafield reference for `ukbb_parser parse` output HTML
* [Jan 16, 2020] Updated category map json
* Introduced dynamic setting of chunk size reading for input CSVs (better for lower memory environments)
