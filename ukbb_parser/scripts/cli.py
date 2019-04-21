#!/usr/bin/env python
import ukbb_parser.scripts.demo_conversion as dc
import ukbb_parser.scripts.condition_filtering as cf
import ukbb_parser.scripts.create_header_key as chk
import ukbb_parser.scripts.level_processing as lp
from ukbb_parser.scripts.utils import read_spreadsheet, find_icd10_ix_range, find_icd10_letter_ixs
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
@click.option("--datafield", metavar="df", help="""Datafield to check for""")
def check(incsv, datafield):
    with open(incsv, 'r') as f:
        first_line = f.readline()
    columns = first_line.strip().split(",")
    datafields = set([col.split("-")[0] for col in columns])
    datafields = list(datafields)
    if datafields[0].startswith('"'):
        datafields = [df[1:] for df in datafields]
    if str(datafield) in datafields:
        click.echo("\nFound {} in CSV\n".format(datafield))
    else:
        click.echo("\nDid not find {} in CSV\n".format(datafield))

@ukbb_parser.command()
@click.option("--previous", metavar="CSV", help="""File path of previous downloaded UK Biobank CSV""")
@click.option("--new", metavar="CSV", help="""File path of new downloaded UK Biobank CSV or CSV of processed results""")
@click.option("--outcsv", metavar="CSV", help="""File path to write newly updated CSV to""")
def update(previous, new, outcsv):
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
    except_eid = outdf.columns.tolist()
    except_eid.remove("eid")
    outdf.dropna(axis=1, how="all", inplace=True)
    outdf[["eid"]+sorted(except_eid, key=lambda x: int(x.split("-")[0]))]
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
@click.option("--rcols", is_flag=True, help='Use this flag if spreadsheet has columns names under R convention (e.g., "X31.0.0")')
@click.option("--fillna",  help="Use this flag to fill blank cells with the flag input, e.g., NA")
@click.option("--combine", metavar="Spreadsheet", multiple=True, help="""Spreadsheets to combine to output; Please make sure all spreadsheets have an identifier column 'eid'; These can be in csv, xls(x) or table formats""")
def parse(incsv, out, incon, excon, insr, exsr, incat, excat, inhdr, exhdr, subjects, dropouts, img_subs_only, img_visit_only, no_convert, rcols, fillna, combine):

    ##################
    ### Setting Up ###
    ##################

    arglist = ' '.join(sys.argv)
    pd.set_option("display.max_colwidth", 500)
    
    ### Functions... We like functions

    def parse_cat_tree(category, cattree):
        class Namespace(object):
            pass
        ns = Namespace()
        ns.results = []

        def inner(data):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == "datafields":
                        ns.results += v
                    else:
                        for item in v:
                            inner(cattree[item])

        inner(cattree[category])
        return ns.results 

    time_between_online_cognitive_test_and_imaging = {'20134-0.0': 'time_between_pairs_matching_imaging',
                                                    '20135-0.0': 'time_between_FI_imaging',
                                                    '20136-0.0': 'time_between_Trails_imaging',
                                                    '20137-0.0': 'time_between_SDMT_imaging',
                                                    '20138-0.0': 'time_between_digit_span_imaging'}

    def delta_t_days(datafield, dataframe):
        imaging_date = pd.Series([datetime.datetime.strptime(v, '%Y-%m-%d') if isinstance(v, str) else np.nan for v in dataframe['53-2.0']])
        online_test_date = pd.Series([datetime.datetime.strptime(v.split('T')[0], '%Y-%m-%d') if isinstance(v, str) else np.nan for v in dataframe[datafield]])
        time_between = online_test_date - imaging_date
        return np.abs(time_between.dt.days)

    ### Reading in the Data Source

    if not os.path.exists(incsv):
        click.echo("{} does not exist. Please double check the provided file path".format(incsv))
        sys.exit(1)

    if out is None:
        click.echo("An out prefix is required. Please provide one and run again.")
        sys.exit(1)

    click.echo("Loading "+incsv)
    df = read_spreadsheet(incsv, 'csv')

    ### Delete empty columns

    df.dropna(axis=1, how="all", inplace=True)
    if rcols:
        revert_names = {}
        for c in df.columns:
            if (len(c.split(".") == 3)) and c.startswith("X"):
                dfr = c.split(".")[0][1:]
                instr = c.split(".")[1]
                entryr = c.split(".")[2]
                revert_names[c] = "{}-{}.{}".format(dfr, instr, entryr)
        df.replace(columns=revert_names, inplace=True)

    orig_columns = df.columns

    ### Loading in Mapped Category and Datafields Tree

    with open(pkg_resources.resource_filename(__name__, 'data/mapped_category_tree.json'), 'r') as f:
        entire_cat_tree = json.load(f)
    cat_tree = entire_cat_tree["tree"]

    ### Creating Include and Exclude Datafield Lists

    click.echo("Determining Output Datafields")

    if len(inhdr) > 0:
        if inhdr[0] == "all":
            to_include = [oc.split("-")[0] for oc in orig_columns]
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

    #######################
    ### Processing Time ###
    #######################
    
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
            except:
                sublist.append(int(sub))
    # if len(cohort) > 0:
    #     for coh in cohort:
    #         click.echo("Obtaining data of individuals listed in " + coh)
    #         with open(coh, "r") as f:
    #             sublist += [l.strip() for l in f.readlines()]

    sublist = [int(subjid) for subjid in sublist]

    if len(sublist) > 0:
        df = df[df.eid.isin(sublist)]

    if img_subs_only:
        if "53-2.0" in orig_columns:
            df = df[df["53-2.0"].notnull()]
        else:
            click.echo("Cannot select imaged subset of participants")
            sys.exit(0)

    ### Remove study dropouts

    dropids = []

    if len(dropouts):
        for drop in dropouts:
            click.echo("Removing data of individuals listed in {} who have withdrawn from the study".format(drop))
            dropcsv = pd.read_csv(drop, header=None)
            dropids += dropcsv[0].values.tolist()

        df = df[~df.eid.isin(dropids)]

    ### Filter subjects by ICD10 conditions

    if (len(incon) > 0) or (len(excon) > 0):
        click.echo("Filtering by ICD10 conditions")

    coding19 = pd.read_csv(pkg_resources.resource_filename(__name__, 'data/icd10_level_map.csv'), index_col="Coding")
    selectable_icd10 = coding19.loc[coding19.Selectable == "Y"].index.tolist()
    
    main_icd_columns = [c for c in orig_columns if c.startswith("41202-")]
    sec_icd_columns = [c for c in orig_columns if c.startswith("41204-")]
    icd_columns = main_icd_columns + sec_icd_columns

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

    if (len(insr) > 0) or (len(exsr) > 0):
        click.echo("Filtering by Self-Report conditions")

    sr_columns = [c for c in orig_columns if c.startswith("20002-")]
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

    if (len(insr) > 0) or (len(incon) > 0):
        found_icd_includes = df[icd_columns].isin(include_icd).any(axis=1)
        found_sr_includes = df[sr_columns].isin(include_srs).any(axis=1)
        found_includes = np.logical_or(found_icd_includes, found_sr_includes)
        df = df.loc[found_includes]

    found_icd_excludes = df[icd_columns].isin(exclude_icd).any(axis=1)
    found_sr_excludes = df[sr_columns].isin(exclude_srs).any(axis=1)
    found_excludes = np.logical_or(found_icd_excludes, found_sr_excludes)
    df = df.loc[~found_excludes]

    ### Control Time

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

    click.echo("Indicating Control Cohorts")
    ### TODO: add Healthy cohort

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

    ### Intermission

    defcols = ["eid"]
    if "31-0.0" in orig_columns:
        defcols.append("31-0.0")
    if "22001-0.0" in orig_columns:
        defcols.append("22001-0.0")

    if no_convert:
        for c in df.columns:
            if c.startswith("6138-") or c.startswith("21000-") or c.startswith("21003-"):
                defcols.append(c)
    else:
        click.echo("Adding Converted Demographic Information")

        ### Calculate Float Ages

        click.echo(" * float ages")
        df, convert_status = dc.calculate_float_ages(df)
        if convert_status is True:
            age_cols = ["Age1stVisit", "AgeRepVisit", "AgeAtScan"]
        else:
            age_cols = ["21003-0.0", "21003-1.0", "21003-2.0"]
        for c in age_cols:
            if c in df.columns:
                defcols.append(c)

        ### Create Race Column
        ### TODO: create separate columns for race and ethnicity?

        click.echo(" * ethnicity")
        df, convert_status = dc.add_ethnicity_columns(df)
        if convert_status is True:
            defcols.append("Race")

        ### Create Eductation Columns

        click.echo(" * education")
        df, convert_status = dc.add_education_columns(df)
        if convert_status is True:
            defcols += ["ISCED", "YearsOfEducation"] 

    ### Filter data columns

    click.echo("Filtering Data Columns")

    includes = [c for c in orig_columns if c.split("-")[0] in to_include]

    for datafield in ["21003-0.0", "21003-1.0", "21003-2.0", "31-0.0", "22001-0.0"]:
        if (datafield in includes) and (datafield in defcols):
            includes.remove(datafield)

    defcols += sorted(list(cohorts.keys()))
    includes = defcols + includes
    df = df[includes]
    df.dropna(axis=1, how="all", inplace=True)

    if "53-2.0" in df.columns:
        for c in includes:
            if c in time_between_online_cognitive_test_and_imaging.keys():
                df[time_between_online_cognitive_test_and_imaging[c]] = delta_t_days(c, df) 

    ########################
    ### Finishing Up Now ###
    ########################

    ### Check if Imaging Time Point Data Only is Requested

    if img_visit_only:
        click.echo("Selecting data acquired at Imaging time point for those datafields using instance 2 codes")
        field_txt = pd.read_csv(pkg_resources.resource_filename(__name__, 'data/field.txt'), sep='\t')
        instance2s = field_txt.loc[field_txt.instance_id == 2, "field_id"].tolist()
        instance2s = [str(in2) for in2 in instance2s]
        drop_non_img_tps = []
        for col in df.columns:
            if (col.split("-")[0] in instance2s):
                if len(col.split("-")) > 1:
                    if col.split("-")[1].split(".")[1] != "2":
                        drop_non_img_tps.append(col)
        df = df.drop(drop_non_img_tps, axis=1)

    ### Create Header Key

    click.echo("Creating HTML header key")
    chk.create_html_key(df, arglist, out)

    ### Add Additional Spreadsheets

    if len(combine) > 0:
        for com in combine:
            click.echo('Adding {} data to output spreadsheet'.format(com))
            add_df = read_spreadsheet(com, 'unknown')
            if "eid" not in add_df.columns:
                click.echo("eid was not found in {}. Skipping for now.".format(com))
                continue
            df = df.merge(add_df, on='eid', how='left', suffixes=("", "_"+com[:5]))

    if fillna is not None:
        df.fillna(fillna, inplace=True)
    
    df.to_csv(out+".csv", chunksize=15000, index=False)
    click.echo("Done!")

@ukbb_parser.command()
@click.option("--incsv", metavar="CSV", help="""File path of downloaded UK Biobank CSV""")
@click.option("--outcsv", metavar="CSV", help="""File path to write out to""")
@click.option("--datatype", metavar="type", 
        type=click.Choice(['icd10', 'self_report', 'careers']),
        help="""Data to inventory; Valid choices include: icd10, self_report, careers""")
@click.option("--level", multiple=True, metavar="level", help="""Level to inventory by; N.B. Please input 0 for the Top level or S for selectable codes""")
@click.option("--code", multiple=True, metavar="code", help="""Codes to inventory; Use the option 'all' to inventory all categories in the given level; Please use level-appropriate codes; Ranges are allowed""")
@click.option("--all_codes", is_flag=True, help="""(optional) Use this flag if you'd like to obtain additionally obtain individual inventories of all codes""")
def inventory(incsv, outcsv, datatype, code, level, all_codes):

    # Check Inputs First

    if len(level) != len(code):
        click.echo("Number of --level and --code flags used should match. Please double check your inputs before trying again.")
        sys.exit(1)

    # Load Datafields from Column Headers
    with open(incsv, "r") as f:
        first_line = f.readline()
    columns = first_line.strip().split(",")
    datafields = set([col.split("-")[0] for col in columns])
    datafields = list(datafields)
    if datafields[0].startswith('"'):
        datafields = [df[1:] for df in datafields]

    # Isolate the Necessary DataFields
    if datatype == 'icd10':
        dfs = ['41202', '41204']
    elif datatype == 'self_report':
        dfs = ['20002']
    elif datatype == 'careers':
        dfs = ['132', '22617']
    else:
        click.echo("--datatype was not specified correctly. Please check inputs and try again.")
        sys.exit(1)

    # Check to make sure necessary datafields are present
    click.echo("Currently checking for the required datafields")
    should_exit = False
    missing_df = 0
    for d in dfs:
        if d not in datafields:
            if datatype == "careers":
                click.echo("Caution: Datafield {} is not included in your data.".format(d))
                missing_df += 1
                if missing_df == 2:
                    click.echo("The relevant datafields have not been found. Please double check your input spreadsheet for the datafields before trying again.")
                    should_exit = True
            else:
                click.echo("Datafield {} is required for this to work. Please double check your input spreadsheet for the datafield before trying again.".format(d))
                should_exit = True
                break
    if should_exit:
        sys.exit(1)

    # Load in relevant level map
    level_map = pkg_resources.resource_filename(__name__, 'data/{}_level_map.csv'.format(datatype))
    
    # Processing
    df = read_spreadsheet(incsv)
    df.dropna(axis=1, how="all", inplace=True)
    original_columns = df.columns.tolist()
    reldfs = []
    for c in df.columns:
        if c.split("-")[0] in dfs:
            reldfs.append(c)
    for i, l in enumerate(level):
        click.echo("Currently conducting an entry inventory of level {} / code {}".format(l, code[i]))
        df = lp.level_processing(df, datatype, reldfs, level_map, code[i], l, all_codes)
    df.dropna(axis=1, how="all", inplace=True)
    new_columns = [col for col in df.columns if col not in original_columns]
    df = df[original_columns + new_columns]
    df.to_csv(outcsv, chunksize=15000, index=False)
    click.echo("Done!")

if __name__ == "__main__":
    ukbb_parser()
