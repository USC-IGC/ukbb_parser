__author__ = 'azhu'

REFERENCE_FILES = {
        'ukbb_html': "/ifs/loni/faculty/thompson/four_d/azhu/ukbb/updated_header_keys.html",
        # ^^^ I need to account for this (ours is preprocessed)
        'incsv': '/ifs/loni/faculty/thompson/four_d/azhu/ukbb/updated_oct2017_imaging_subset.csv',
        }

ADDITIONAL_SPREADSHEETS = {
        'GWAS': {
            'spreadsheet_file': '/ifs/loni/faculty/thompson/four_d/azhu/ukbb/ukb1155_GWASed_HM3_b37mds.mds',
            'delimiter': 'whitespace'
            }
        'freesurfer': {
            'spreadsheet_file': "/ifs/loni/faculty/thompson/four_d/azhu/ukbb/CorticalMeasuresENIGMA_SurfAvg-ThickAvg_ALL_v7_ROI_fails_as_NAs_NEDA_RL_combined.xlsx"
            #'join_on': '',
            }
        }

self_report_excludes = [1075, 1081, 1086, 1220, 1234, 1243, 1246, 1247, 1250, 1256, 1258, 1260,
                        1261, 1262, 1264, 1266, 1267, 1286, 1287, 1288, 1291, 1371, 1408,
                        1434, 1437, 1439]

# Maybe take this out since we'll have the other function 
COHORT= {
        "CNSFree_Broad": {
            'cohort_file': ''
            },
        "CNSFree_Strict": {
            'cohort_file': ''
            },
        "NeuroFree_Broad": {
            'cohort_file': ''
            },
        "NeuroFree_Strict": {
            'cohort_file': ''
            },
        "Healthy": {
            'cohort_file': ''
            },
        "SuperHealthy": {
            'cohort_file': ''
            }
        }

defcols = ["eid", "31-0.0", "Age1stVisit", "AgeRepVisit", "AgeAtScan", "Race", "ISCED", "YearsOfEducation"]
          + list(COHORT.keys()) 

if len(ADDITIONAL_SPREADSHEETS) > 0:
    defcols += list(ADDITIONAL_SPREADSHEETS.keys()) # This doesn't actually make sense
