#!/usr/bin/env python
import ukbb_parser.scripts.demo_conversion as dc
import ukbb_parser.scripts.condition_filtering as cf
import ukbb_parser.scripts.create_header_key as chk
import ukbb_parser.scripts.level_processing as lp
from ukbb_parser.scripts.utils import read_spreadsheet, find_icd10_ix_range, find_icd10_letter_ixs, parse_cat_tree, create_long_bois
import pkg_resources
import pandas as pd
import numpy as np
import datetime
import click
import json
import sys
import os
# import category_tree as ct
# import config

### These are to get rid of warning messages that might worry people. Comment them out when developing and debugging
import warnings
warnings.filterwarnings("ignore")

@click.group()
def ukbb_parser():
    pass

# ### Create Custom Cohorts
# 
# @ukbb_parser.command()
# @click.option("--cohort", metavar="path", help="""Name of text file to write out""")
# @click.option("--incsv", metavar="csv", help="""CSV(s) from which the cohort subject IDs are to be derived""")
# def create_cohort(cohort, incsv):
#     subjids = []
#     for csv in incsv:
#         subjids += csv.eid.values.tolist()
# 
#     subjids = set(subjids) # Remove Duplicates
#     subjids = sorted(list(subjids)) # Sort them in increasing order
#     subjids = [str(subjid)+"\n" for subjid in subjids] # Convert IDs to strings and add prepare for writing to text file
#     
#     with open(cohort, "w") as f:
#         f.writelines(subjids)

@ukbb_parser.command()
@click.option("--incsv", metavar="CSV", help="""File path of downloaded UK Biobank CSV""")
@click.option("--datafield", multiple=True, metavar="df", help="""Datafield to check for""")
@click.option("--category", multiple=True, metavar="cat", help="""Category to check for""")
def check(incsv, datafield, category):
    '''
    Determine if the queried Datafield or Category is included in the downloaded CSV file.

    Please see https://github.com/USC-IGC/ukbb_parser for additional documentation.
    '''
    with open(incsv, 'r') as f:
        first_line = f.readline()
    columns = first_line.strip().split(",")
    datafields = set([col.split("-")[0] for col in columns])
    datafields = list(datafields)
    if datafields[0].startswith('"'):
        datafields = [df[1:] for df in datafields]
    if len(datafield) > 0:
        for dfield in datafield:
            if str(dfield) in datafields:
                click.echo("\nFound {} in CSV\n".format(dfield))
            else:
                click.echo("\nDid not find {} in CSV\n".format(dfield))
    if len(category) > 0:
        with open(pkg_resources.resource_filename(__name__, 'data/mapped_category_tree.json'), 'r') as f:
            entire_cat_tree = json.load(f)
        cat_tree = entire_cat_tree["tree"]
        for cat in category:
            cat_dfs = parse_cat_tree(cat, cat_tree)
            if len(cat_dfs) == 0:
                click.echo("\n{} does not appear to be a valid or mapped category\n".format(cat))
                sys.exit(1)
            else:
                y = 0
                missing = []
                for dfield in cat_dfs:
                    if str(dfield) in datafields:
                        y += 1
                    else:
                        missing.append(dfield)
                click.echo("\nFound {} data-fields.\nMissing {} data-fields\n".format(y, len(missing)))
                if len(missing) > 0:
                    click.echo(", ".join(missing)+'\n')


@ukbb_parser.command()
@click.option("--previous", metavar="CSV", help="""File path of previous downloaded UK Biobank CSV""")
@click.option("--new", metavar="CSV", help="""File path of new downloaded UK Biobank CSV or CSV of processed results""")
@click.option("--outcsv", metavar="CSV", help="""File path to write newly updated CSV to""")
def update(previous, new, outcsv):
    '''
    Combine multiple spreadsheet files.

    Please see https://github.com/USC-IGC/ukbb_parser for additional documentation.
    '''
    click.echo("Loading "+previous)
    pc = read_spreadsheet(previous, 'csv')
    click.echo("Loading "+new)
    nc = read_spreadsheet(new, 'csv')

    keep = ['eid']
    for col in pc.columns:
        if col not in nc.columns:
            keep.append(col)
    old_columns = " ".join(set([dfn.split("-")[0] for dfn in keep]))
    click.echo("\nKeeping old columns: " + old_columns)

    new_cols = []
    for col in nc.columns:
        if col not in pc.columns:
            new_cols.append(col)
    new_columns = " ".join(set([dfn.split("-")[0] for dfn in new_cols]))
    click.echo("\nNew columns: " + new_columns)

    outdf = pd.merge(pc[keep], nc, how="outer", on="eid")
    except_eid = list(outdf.columns)
    str_columns = []
    for c in outdf.columns.tolist():
        try:
            int(c.split("-")[0])
        except ValueError:
            except_eid.remove(c)
            str_columns.append(c)
    outdf.dropna(axis=1, how="all", inplace=True)
    outdf[str_columns+sorted(except_eid, key=lambda x: int(x.split("-")[0]))]
    click.echo("\nWriting "+outcsv)
    outdf.to_csv(outcsv, chunksize=15000, index=False)

parser_desc = """ 
 """

@ukbb_parser.command()
@click.option("-i", "--incsv", metavar="CSV", help="""File path of the downloaded UK Biobank data csv""")
@click.option("-o", "--out", help="""Output prefix""")
@click.option("--incon", multiple=True, metavar="ICD10Code",
        help="ICD10 Diagnosis codes you wish to include. Least common denominators are acceptable, e.g. --incon F. Ranges are also acceptable inputs, e.g. F10-F20, and can span across letters")
@click.option("--excon", multiple=True, metavar="ICD10Code",
        help="ICD10 Diagnosis codes you wish to exclude. Least common denominators are acceptable, e.g. --excon F. Ranges are also acceptable inputs, e.g. F10-F20, and can span across letters") 
@click.option("--insr", multiple=True, metavar="SRCode",
        help="Self-Report codes you wish to include. Ranges are acceptable inputs.")
@click.option("--exsr", multiple=True, metavar="SRCode",
        help="Self-Report codes you wish to exclude. Ranges are acceptable inputs.")
# @click.option("--filter", metavar="column=value", multiple=True,
#         help="Filters to only give rows where the column value is as specified")
@click.option("--incat", multiple=True, metavar="Category",
        help="Categories you wish to include. Ranges are acceptable inputs, e.g. 100-200")
@click.option("--excat", multiple=True, metavar="Category",
        help="Categories you wish to exclude. Ranges are acceptable inputs, e.g. 100-200")
@click.option("--inhdr", multiple=True, metavar="HeaderName",
        help="Columns names you wish to include. Ranges are acceptable inputs, e.g. 100-200\nIf you wish to have all the available data, please use --inhdr all")
@click.option("--exhdr", multiple=True, metavar="HeaderName",
        help="Columns names you wish to exclude. Ranges are acceptable inputs, e.g. 100-200")
# @click.option("--cohort", metavar="cohort", multiple=True,
#         help="""Output csv will be limited to the data of the cohort(s)""")
@click.option("--subjects", multiple=True, metavar="SubID", help="""A list of participant IDs to include""")
@click.option("--dropouts", multiple=True, metavar="dropouts", help="""CSV(s) containing eids of participants who have dropped out of the study""")
@click.option("--img_subs_only", is_flag=True, help="Use this flag to only keep data of participants with an imaging visit.")
@click.option("--img_visit_only", is_flag=True, help="Use this flag to only keep data acquired during the imaging visit.")
@click.option("--no_convert", is_flag=True, help="Use this flag if you don't want the demographic conversions run")
@click.option("--long_names", is_flag=True, help='Use this flag to replace datafield numbers in column names with datafield titles')
@click.option("--rcols", is_flag=True, help='Use this flag if spreadsheet has columns names under R convention (e.g., "X31.0.0")')
@click.option("--fillna",  help="Use this flag to fill blank cells with the flag input, e.g., NA")
@click.option("--chunksize", help="Use this flag to set the processing chunk size, Default:1000", default=1000)
# @click.option("--combine", metavar="Spreadsheet", multiple=True, help="""Spreadsheets to combine to output; Please make sure all spreadsheets have an identifier column 'eid'; These can be in csv, xls(x) or table formats""")
def parse(incsv, out, incon, excon, insr, exsr, incat, excat, inhdr, exhdr, subjects, dropouts, img_subs_only, img_visit_only, no_convert, long_names, rcols, fillna, chunksize):
    '''
    Filter the input CSV file with the given input parameters.

    Please see https://github.com/USC-IGC/ukbb_parser for additional documentation.
    '''

    ##################
    ### Setting Up ###
    ##################

    if not os.path.exists(incsv):
        click.echo("{} does not exist. Please double check the provided file path".format(incsv))
        sys.exit(1)

    if out is None:
        click.echo("An out prefix is required. Please provide one and run again.")
        sys.exit(1)

    if os.path.exists(out+'.csv'):
        click.echo("The output CSV already exists.\nIf %s is the intended name, please delete it and run again." %(out+'.csv'))
        sys.exit(1)

    arglist = ' '.join(sys.argv)
    pd.set_option("display.max_colwidth", 500)
    
    ### Functions... We like functions

    time_between_online_cognitive_test_and_imaging = {
            '20134-0.0': 'time_between_pairs_matching_imaging',
            '20135-0.0': 'time_between_FI_imaging',
            '20136-0.0': 'time_between_Trails_imaging',
            '20137-0.0': 'time_between_SDMT_imaging',
            '20138-0.0': 'time_between_digit_span_imaging'
            }

    def delta_t_days(datafield, dataframe):
        imaging_date = pd.Series([datetime.datetime.strptime(v, '%Y-%m-%d') if isinstance(v, str) else np.nan for v in dataframe['53-2.0']])
        online_test_date = pd.Series([datetime.datetime.strptime(v.split('T')[0], '%Y-%m-%d') if isinstance(v, str) else np.nan for v in dataframe[datafield]])
        try:
            time_between = online_test_date - imaging_date
            return np.abs(time_between.dt.days)
        except TypeError:
            return np.array([np.nan]*len(imaging_date))

    ####################################
    ### Filter data columns, Part I  ###
    ####################################

    all_columns = pd.read_csv(incsv, encoding='ISO-8859-1', nrows=2)
    all_columns = list(all_columns.columns)
    defcols = ["eid"]
    covariate_columns = ['eid']

    # R cols

    if rcols:
        revert_names = {}
        for c in all_columns:
            if (len(c.split(".")) == 3) and c.startswith("X"):
                dfr = c.split(".")[0][1:]
                instr = c.split(".")[1]
                entryr = c.split(".")[2]
                revert_names[c] = "{}-{}.{}".format(dfr, instr, entryr)
        all_columns = ['eid'] + list(revert_names.values())

    ### Loading in Mapped Category and Datafields Tree

    with open(pkg_resources.resource_filename(__name__, 'data/mapped_category_tree.json'), 'r') as f:
        entire_cat_tree = json.load(f)
    cat_tree = entire_cat_tree["tree"]

    ### Creating Include and Exclude Datafield Lists

    click.echo("Determining Output Datafields")

    if len(inhdr) > 0:
        if inhdr[0] == "all":
            to_include = [oc.split("-")[0] for oc in all_columns]
        else:
            to_include = []
            for ih in inhdr:
                if "-" in ih:
                    inhdr_range = list(range(int(ih.split("-")[0]), int(ih.split('-')[1])+1))
                    to_include += [str(hdr) for hdr in inhdr_range]
                else:
                    to_include.append(ih)
    else:
        to_include = []

    to_exclude = []
    if len(exhdr) > 0:
        for eh in exhdr:
            if "-" in eh:
                exhdr_range = list(range(int(eh.split("-")[0]), int(eh.split('-')[1])+1))
                to_exclude += [str(hdr) for hdr in exhdr_range]
            else:
                to_exclude.append(eh)

    if len(incat) > 0: 
        for ic in incat:
            if "-" in ic:
                for n in range(int(ic.split("-")[0]), int(ic.split("-")[1])+1):
                    to_include += parse_cat_tree(str(n), cat_tree)
            else:
                to_include += parse_cat_tree(str(ic), cat_tree)

    if len(excat) > 0:
        for ec in excat:
            if "-" in ec:
                for n in range(int(ec.split("-")[0]), int(ec.split("-")[1])+1):
                    to_exclude += parse_cat_tree(str(n), cat_tree)
            else:
                to_exclude += parse_cat_tree(str(ec), cat_tree)

    to_include = list(set(sorted(to_include)))
    to_include = [hdr for hdr in to_include if hdr not in to_exclude]

    ### Check if Imaging Time Point Data Only is Requested

    if img_visit_only or long_names:
        field_txt = pd.read_csv(pkg_resources.resource_filename(__name__, 'data/field.txt'), index_col='field_id', sep='\t')

    instance2s = []
    if img_visit_only:
        click.echo("Selecting data acquired at Imaging time point for those datafields using instance 2 codes")
        instance2s = field_txt.loc[field_txt.instance_id == 2].index.tolist()
        instance2s = [str(in2) for in2 in instance2s]

    ### Default Covariates

    # Sex

    if "31-0.0" in all_columns:
        covariate_columns.append("31-0.0")
        defcols.append("31-0.0")
    if "22001-0.0" in all_columns:
        defcols.append("22001-0.0")
        covariate_columns.append("22001-0.0")

    # Genetic Race

    if "22006-0.0" in all_columns:
        defcols.append("22006-0.0")
        covariate_columns.append("22006-0.0")

    # And More

    mds_components = []
    icd_columns = []
    sr_columns = []

    for c in all_columns:

        # Other Demographics
        if c.split("-")[0] in ["6138", "21000", "21003", "34", "52", "53"]:
            defcols.append(c)
            continue

        # Genetics 

        if c.startswith("22009-") and (len(mds_components) < 10):
            defcols.append(c)
            mds_components.append(c)
            continue

        # ICD10 Conditions 

        if c.startswith("41202-") or c.startswith("41204-") or c.startswith("41270-"):
            icd_columns.append(c)
            defcols.append(c)
            continue

        # Self-Report Conditions 

        if c.startswith("20002-"):
            sr_columns.append(c)
            defcols.append(c)
            continue

        # DataField Filter

        datafield = c.split("-")[0] 
        if datafield in to_include:
            # Time Point Filter
            if img_visit_only and (datafield in instance2s):
                if c.split("-")[1].split(".")[0] in ["2", "3"]:
                    defcols.append(c)
            else:
                defcols.append(c)

    #####################
    ### Preprocessing ###
    #####################

    ### ICD10

    if (len(icd_columns) == 0) and ((len(incon) > 0) or (len(excon) > 0)):
        click.echo("ICD 10 columns are not available for diagnosis condition filtering. Please check input spreadsheet before trying again.")
        sys.exit(1)

    coding19 = pd.read_csv(pkg_resources.resource_filename(__name__, 'data/icd10_level_map.csv'), index_col="Coding")
    selectable_icd10 = coding19.loc[coding19.Selectable == "Y"].index.tolist()
    
    include_icd = []

    if len(incon) > 0:
        for icd in incon:
            if icd in selectable_icd10:
                include_icd.append(icd)
            elif "-" in icd:
                start_loc, end_loc = find_icd10_ix_range(coding19, icd.split("-")[0], icd.split("-")[1])
                include_icd += coding19.loc[start_loc : end_loc].index.tolist()
            else:
                include_icd += find_icd10_letter_ixs(coding19, icd)

    exclude_icd = []

    if len(excon) > 0:

        for icd in excon:
            if icd in selectable_icd10:
                exclude_icd.append(icd)
            elif "-" in icd:
                start_loc, end_loc = find_icd10_ix_range(coding19, icd.split("-")[0], icd.split("-")[1])
                exclude_icd += coding19.loc[start_loc : end_loc].index.tolist()
            else:
                exclude_icd += find_icd10_letter_ixs(coding19, icd)

    # N.B. Actual filtering happens below in Self-Report section

    ### Filter subjects by Self-Report conditions

    if (len(sr_columns) == 0) and ((len(insr) > 0) or (len(exsr) > 0)):
        click.echo("Self-report columns are not available for filtering. Please check input spreadsheet before trying again.")
        sys.exit(1)

    if (len(insr) > 0) or (len(exsr) > 0):
        click.echo("Filtering by Self-Report conditions")

    include_srs = []

    if len(insr) > 0:
        for sr in insr:
            if "-" in sr:
                include_srs += list(range(int(sr.split("-")[0]), int(sr.split("-")[1]) + 1))
            else:
                include_srs.append(int(sr))
                
    exclude_srs = []
    
    if len(exsr) > 0:
        for sr in exsr:
            if "-" in sr:
                exclude_srs += list(range(int(sr.split("-")[0]), int(sr.split("-")[1]) + 1)) 
            else:
                exclude_srs.append(int(sr))

    ### Filter subjects by IDs

    sublist = []
    if len(subjects) > 0:
        click.echo("Obtaining subset of provided subject IDs")
        for sub in subjects:
            try:
                with open(sub, 'r') as f:
                    lines = [l.strip() for l in f.readlines()]
                sublist += [int(l) for l in lines]
                del lines
            except (FileNotFoundError, UnicodeDecodeError) as e:
                sublist.append(int(sub))
            except ValueError:
                print("Encountered invalid --subjects entry. Please check before trying again.")
                sys.exit(1)
    
    sublist = [int(subjid) for subjid in sublist]

    ### Remove study dropouts

    dropids = []

    if len(dropouts) > 0:
        for drop in dropouts:
            try:
                with open(drop, 'r') as f:
                    lines = [l.strip() for l in f.readlines()]
                dropids += [int(l) for l in lines]
                del lines
            except (FileNotFoundError, UnicodeDecodeError) as e:
                dropids.append(int(drop))
            except ValueError:
                print("Encountered invalid --dropouts entry. Please check before trying again.")
                sys.exit(1)

    ###############
    ### COHORTS ###
    ###############

    ### Cohort Flag

    # if len(cohort) > 0:
    #     for coh in cohort:
    #         click.echo("Obtaining data of individuals listed in " + coh)
    #         with open(coh, "r") as f:
    #             sublist += [l.strip() for l in f.readlines()]

    cohorts = {"NP_controls_1": {"icd10": ['A8', 'B20', 'B21', 'B22', 'B23', 'B24', 'B65-B83',
                                           'C', 'F','G','I6','Q0','S04','S06','S07','S08','S09',
                                           'T36-T46', 'T48-T50']},
               "NP_controls_2": {"icd10": ['A8', 'B20', 'B21', 'B22', 'B23', 'B24', 'B65-B83',
                                           'C', 'F','G','I6','Q0','S04','S06','S07','S08','S09',
                                           'T36-T46', 'T48-T50'],
                                 "sr": [1075, 1081, 1086, 1220, 1234, 1243, 1246, 1247, 1250, 1256, 1258, 1260,
                                        1261, 1262, 1264, 1266, 1267, 1286, 1287, 1288, 1291, 1371, 1408,
                                        1434, 1437, 1439]},
               "CNS_controls_1": {"icd10": ['C70', 'C71', 'C72', 'G', 'I6', 'Q0', 'R90', 'R940', 
                                            'S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08', 'S09'],
                                  "sr": [1081, 1086, 1266, 1267, 1397, 1434, 1437, 1491, 1626]\
                                        + list(range(1244,1252)) + list(range(1258, 1265))},
               "CNS_controls_2": {"icd10": ['C70', 'C71', 'C72', 'F2', 'F31', 'F7', 'G', 'I6', 'Q0', 'R90', 'R940', 
                                            'S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08', 'S09'],
                                  "sr": [1081, 1086, 1243, 1266, 1267, 1289, 1291, 
                                         1371, 1397, 1434, 1437, 1491, 1626]\
                                        + list(range(1244,1252)) + list(range(1258, 1265))}
               }

    ### TODO: add Healthy cohort


    #######################
    ### Processing Time ###
    #######################
    
    ### Reading in the Data Source

    click.echo("Loading "+incsv)
    # df = read_spreadsheet(incsv, 'csv')

    ### Delete empty columns

    # df.dropna(axis=1, how="all", inplace=True)

    for i, df in enumerate(pd.read_csv(incsv, encoding='ISO-8859-1', chunksize=chunksize, usecols=defcols)):

        if rcols:
            df.rename(columns=revert_names, inplace=True)

        click.echo("\nProcessing Chunk %i\n" %i)

        ### Filter subjects by IDs
        if len(sublist) > 0:
            df = df[df.eid.isin(sublist)]
        if df.empty:
            continue

        if img_subs_only:
            if "53-2.0" in df.columns:
                df = df[df["53-2.0"].notnull()]
            else:
                click.echo("Cannot select imaged subset of participants")
                sys.exit(1)
        if df.empty:
            continue

        ### Remove study dropouts

        if len(dropids) > 0:
            click.echo("Removing data of individuals listed in {} who have withdrawn from the study".format(drop))
            df = df[~df.eid.isin(dropids)]
        if df.empty:
            continue

        ### Filter subjects by ICD10 conditions

        if (len(incon) > 0) or (len(excon) > 0):
            click.echo("Filtering by ICD10 conditions")


        if (len(insr) > 0) or (len(incon) > 0):
            found_icd_includes = df[icd_columns].isin(include_icd).any(axis=1)
            found_sr_includes = df[sr_columns].isin(include_srs).any(axis=1)
            found_includes = np.logical_or(found_icd_includes, found_sr_includes)
            df = df.loc[found_includes]

        found_icd_excludes = df[icd_columns].isin(exclude_icd).any(axis=1)
        found_sr_excludes = df[sr_columns].isin(exclude_srs).any(axis=1)
        found_excludes = np.logical_or(found_icd_excludes, found_sr_excludes)
        df = df.loc[~found_excludes]
        if df.empty:
            continue

        ### Control Time

        if (len(icd_columns) > 0) and (len(sr_columns) > 0):
            click.echo("Indicating Control Cohorts")
            for k, v in cohorts.items():
                icd10_excludes = []
                for icd in v['icd10']:
                    if icd in selectable_icd10:
                        icd10_excludes.append(icd)
                    elif "-" in icd:
                        excon_ix_0 = icd.split("-")[0]
                        excon_ix_1 = icd.split("-")[1]
                        start_loc, end_loc = find_icd10_ix_range(coding19, excon_ix_0, excon_ix_1)
                        icd10_excludes += coding19.loc[start_loc : end_loc].index.tolist()
                    else:
                        icd10_excludes += find_icd10_letter_ixs(coding19, icd)

                icd10_series = df[icd_columns].isin(icd10_excludes).any(axis=1)
                sr_series = np.zeros_like(icd10_series)
                if 'sr' in v.keys():
                    sr_series = df[sr_columns].isin(v['sr']).any(axis=1)
                df.loc[~np.logical_or(icd10_series, sr_series), k] = 1
        else:
            click.echo("Warning: Cannot indicate control subjects. ICD-10 or self-report data fields are missing")

        ### Default Covariates

        if no_convert:
            for c in df.columns:
                if c.startswith("6138-") or c.startswith("21000-") or c.startswith("21003-"):
                    covariate_columns.append(c)
        else:
            click.echo("Adding Converted Demographic Information")

            ### Calculate Float Ages

            click.echo(" * float ages")
            df, convert_status = dc.calculate_float_ages(df)
            if convert_status is True:
                age_cols = ["Age1stVisit", "AgeRepVisit", "AgeAtScan", "AgeAt2ndScan"]
            else:
                age_cols = ["21003-0.0", "21003-1.0", "21003-2.0", "21003-3.0"]
            for c in age_cols:
                if c in df.columns:
                    covariate_columns.append(c)

            ### Create Race Column
            ### TODO: create separate columns for race and ethnicity?

            click.echo(" * ethnicity")
            df, convert_status = dc.add_ethnicity_columns(df)
            if convert_status is True:
                covariate_columns.append("Race")

            ### Create Eductation Columns

            click.echo(" * education")
            df, convert_status = dc.add_education_columns(df)
            if convert_status is True:
                covariate_columns += ["ISCED", "YearsOfEducation"] 

        ####################################
        ### Filter data columns, Part II ###
        ####################################

        click.echo("Filtering Data Columns")

        includes = [c for c in defcols if c.split("-")[0] in to_include]
        for datafield in ["21003-0.0", "21003-1.0", "21003-2.0", "21003-3.0", "31-0.0", "22001-0.0", "22006-0.0"] + mds_components:
            if (datafield in includes) and (datafield in covariate_columns):
                includes.remove(datafield)

        covariate_columns += mds_components
        covariate_columns += sorted(list(cohorts.keys()))
        includes = [c for c in df.columns if c in covariate_columns + includes]
        df = df[includes]
        # df.dropna(axis=1, how="all", inplace=True)

        if "53-2.0" in df.columns:
            for k in time_between_online_cognitive_test_and_imaging.keys():
                if k in includes:
                    df[time_between_online_cognitive_test_and_imaging[k]] = np.array(delta_t_days(k, df))

        ########################
        ### Finishing Up Now ###
        ########################

        ### Long Bois Time

        if long_names:
            name_key = create_long_bois(df.columns, field_txt)
            df.rename(columns=name_key, inplace=True)

        if fillna is not None:
            df.fillna(fillna, inplace=True)
        
        if os.path.exists(out+".csv"):
            df.to_csv(out+".csv", mode="a", header=False, index=False)
        else:
            df.to_csv(out+".csv", index=False)

            ### Create Header Key

            click.echo("Creating HTML header key")
            chk.create_html_key(df, arglist, out)

    ### Add Additional Spreadsheets

    # if len(combine) > 0:
    #     for com in combine:
    #         click.echo('Adding {} data to output spreadsheet'.format(com))
    #         add_df = read_spreadsheet(com, 'unknown')
    #         if "eid" not in add_df.columns:
    #             click.echo("eid was not found in {}. Skipping for now.".format(com))
    #             continue
    #         else:
    #             if not pd.api.types.is_numeric_dtype(add_df.eid):
    #                 valid_eids = [eid for eid in add_df.eid if eid.isdigit()]
    #                 add_df = add_df[add_df.eid.isin(valid_eids)]
    #                 add_df.eid = add_df.eid.astype(int)
    #             df = df.merge(add_df, on='eid', how='left', suffixes=("", "_"+com[:5]))

    click.echo("Done!")

@ukbb_parser.command()
@click.option("--incsv", metavar="CSV", help="""File path of downloaded UK Biobank CSV""")
@click.option("--outcsv", metavar="CSV", help="""File path to write out to""")
@click.option("--subjects", multiple=True, metavar="SubID", help="""A list of participant IDs to include""")
@click.option("--rcols", is_flag=True, help='Use this flag if spreadsheet has columns names under R convention (e.g., "X31.0.0")')
@click.option("--datatype", metavar="type", 
        type=click.Choice(['icd10', 'self_report', 'careers']),
        help="""Data to inventory; Valid choices include: icd10, self_report, careers""")
@click.option("--level", multiple=True, metavar="level", help="""Level to inventory by; N.B. Please input 0 for the Top level or S for selectable codes""")
@click.option("--code", multiple=True, metavar="code", help="""Codes to inventory; Use the option 'all' to inventory all categories in the given level; Please use level-appropriate codes; Ranges are allowed""")
@click.option("--all_codes", is_flag=True, help="""(optional) Use this flag if you'd like to obtain additionally obtain individual inventories of all codes""")
@click.option("--chunksize", help="Use this flag to set the processing chunk size, Default:1000", default=1000)
def inventory(incsv, outcsv, subjects, rcols, datatype, code, level, all_codes, chunksize):
    '''
    Create binary columns indicating the presence of specified data.

    Please see https://github.com/USC-IGC/ukbb_parser for additional documentation.
    '''

    # Check Inputs First

    if not os.path.exists(incsv):
        click.echo("{} does not exist. Please double check the provided file path".format(incsv))
        sys.exit(1)

    if os.path.exists(outcsv):
        click.echo("The output CSV already exists.\nIf %s is the intended name, please delete it and run again." %outcsv)
        sys.exit(1)

    if len(level) != len(code):
        click.echo("Number of --level and --code flags used should match. Please double check your inputs before trying again.")
        sys.exit(1)

    # Load Datafields from Column Headers
    all_columns = pd.read_csv(incsv, encoding='ISO-8859-1', nrows=2)
    all_columns = list(all_columns.columns)

    # R columns
    if rcols:
        revert_names = {}
        for c in all_columns:
            if (len(c.split(".")) == 3) and c.startswith("X"):
                dfr = c.split(".")[0][1:]
                instr = c.split(".")[1]
                entryr = c.split(".")[2]
                revert_names[c] = "{}-{}.{}".format(dfr, instr, entryr)
        all_columns = ['eid']+list(revert_names.values())

    # Isolate the Necessary DataFields

    necessary = {
            'icd10': ['41202', '41204', '41270'],
            'self_report': ['20002'],
            'careers': ['22617'] # 132 now restricted
            }

    # The following shouldn't be necessary but just in case
    if datatype not in list(necessary.keys()):
        click.echo("--datatype was not specified correctly. Please check inputs and try again.")
        sys.exit(1)

    # Check to make sure necessary datafields are present
    click.echo("Currently checking for the required datafields")
    missing_df = 0
    defcols=['eid']
    datafields = []
    for c in all_columns:
        datafield = c.split("-")[0]
        if datafield in necessary[datatype]:
            if datafield not in datafields:
                datafields.append(datafield)
            defcols.append(c)

    if len(datafields) == 0:
        click.echo("The relevant datafield(s) (%s) have not been found. Please double check your input spreadsheet for the datafields before trying again." % ", ".join(necessary[datatype]))
        sys.exit(1)
    elif len(datafields) < len(necessary[datatype]):
        click.echo("Caution: Some datafields (%s) are not included in the input spreadsheet. Proceeding with the other(s)" % ", ".join([f for f in necessary[datatype] if f not in datafields]))

    # Load in relevant level map
    level_map = pkg_resources.resource_filename(__name__, 'data/{}_level_map.csv'.format(datatype))
    
    ### Filter subjects by IDs

    sublist = []
    if len(subjects) > 0:
        click.echo("Obtaining subset of provided subject IDs")
        for sub in subjects:
            try:
                with open(sub, 'r') as f:
                    lines = [l.strip() for l in f.readlines()]
                sublist += [int(l) for l in lines]
                del lines
            except (FileNotFoundError, UnicodeDecodeError) as e:
                sublist.append(int(sub))
            except ValueError:
                print("Encountered invalid --subjects entry. Please double check before trying again.")
                sys.exit(1)

    # Processing

    # df = read_spreadsheet(incsv)
    reldfs = list(defcols)
    reldfs.remove('eid')
    for i, df in enumerate(pd.read_csv(incsv, encoding='ISO-8859-1', chunksize=chunksize, usecols=defcols)):

        # Filter Subjects
        if len(sublist) > 0:
            df = df[df.eid.isin(sublist)]

        if rcols:
            df.rename(columns=revert_names, inplace=True)

        for i, l in enumerate(level):
            click.echo("Currently conducting an entry inventory of level {} / code {}".format(l, code[i]))
            df = lp.level_processing(df, datatype, reldfs, level_map, code[i], l, all_codes)
        new_columns = [col for col in df.columns if col not in reldfs]
        df = df[new_columns]

        if os.path.exists(outcsv):
            df.to_csv(outcsv, mode="a", header=False, index=False)
        else:
            df.to_csv(outcsv, index=False)

    click.echo("Done!")

if __name__ == "__main__":
    ukbb_parser()
