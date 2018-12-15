#!/usr/bin/env python
import demo_conversion as dc
import category_tree as ct
import condition_filtering as cf
import create_header_key as chk
import pkg_resources
import pandas as pd
import numpy as np
import datetime
import click
import json
import sys
import os
# import config

### These are to get rid of warning messages that might worry people. Comment them out when developing and debugging
# import warnings
# warnings.filterwarnings("ignore")

@click.group()
def ukbb_parser():
    pass

### Create Custom Cohorts

@ukbb_parser.command()
@click.option("--cohort", metavar="<cohort>", help="""Cohort Name""")
@click.option("--incsv", metavar="<csv>", nargs="+", help="""CSV(s) from which the cohort subject IDs are to be derived""")
def create_cohort(cohort, incsv):
    subjids = []
    for csv in incsv:
        subjids += csv.eid.values.tolist()

    subjids = set(subjids) # Remove Duplicates
    subjids = sorted(list(subjids)) # Sort them in increasing order
    subjids = [str(subjid)+"\n" for subjid in subjids] # Convert IDs to strings and add prepare for writing to text file
    
    with open(cohort, "w") as f:
        f.writelines(subjids)

@ukbb_parser.command()
@click.option("--previous", help="""File path of previous downloaded UK Biobank csv""")
@click.option("--new", help="""File path of new downloaded UK Biobank csv""")
@click.option("--output", help="""File path to write newly updated csv to""")
def update(previous, new, output)
    def read_csv(csv):
        csv_size = os.stat(csv).st_size # This is in bytes
        if csv_size > 500000000:
            csv_reader = pd.read_csv(csv, chunksize=15000)
            chunk_list = []
            for chunk in csv_reader:
                click.echo("Loading {}...".format(csv))
                chunk_list.append(chunk)
            dataFrame = pd.concat(chunk_list, ignore_index=True)
            del chunk, chunk_list
        else:
            dataFrame = pd.read_csv(csv)
        return dataFrame
    pc = read_csv(prevcsv)
    nc = read_csv(newcsv)

    keep = ['eid']
    for col in pc.columns:
        if col not in nc.columns:
            keep.append(col)
    click.echo("Keeping old columns:", set([dfn.split("-")[0] for dfn in keep]))

    new_cols = []
    for col in nc.columns:
        if col not in pc.columns:
            new_cols.append(col)
    click.echo("New columns:", set([dfn.split("-")[0] for dfn in new_cols]))

    outdf = pd.merge(pc[keep], nc, how="right", on="eid")
    except_eid = outdf.columns.tolist()
    except_eid.remove("eid")
    outdf[["eid"]+sorted(except_eid)]
    outdf.to_csv(outcsv, index=False)

parser_desc = """ 
 """

@ukbb_parser.command()
@click.option("-i", "--incsv", help="""File path of the downloaded UK Biobank data csv""")
@click.option("-o", "--out", help="""Output prefix""")
@click.option("--incon", nargs="+", metavar="ICD10Code",
        help="ICD10 Diagnosis codes you wish to include. \nLeast common denominators are acceptable, e.g. --incon F\nFor ranges, please keep them within the same letter, e.g. F10-20") 
@click.option("--excon", nargs="+", metavar="ICD10Code",
        help="ICD10 Diagnosis codes you wish to exclude. \nLeast common denominators are acceptable, e.g. --excon F\nFor ranges, please keep them within the same letter, e.g. F10-20") 
@click.option("--insr", nargs="+", metavar="SRCode",
        help="Self-Report codes you wish to include. \nRanges are acceptable inputs.")
@click.option("--exsr", nargs="+", metavar="SRCode",
        help="Self-Report codes you wish to exclude. \nRanges are acceptable inputs.")
# @click.option("--filter", metavar="column=value", nargs="+",
#         help="Filters to only give rows where the column value is as specified")
@click.option("--incat", nargs="+", metavar="Category",
        help="Categories you wish to include. Ranges are acceptable inputs, e.g. 100-200")
@click.option("--excat", nargs="+", metavar="Category",
        help="Categories you wish to exclude. Ranges are acceptable inputs, e.g. 100-200")
@click.option("--inhdr", nargs="+", metavar="HeaderName",
        help="Columns names you wish to include. Ranges are acceptable inputs, e.g. 100-200\nIf you wish to have all the available data, please use --inhdr all")
@click.option("--exhdr", nargs="+", metavar="HeaderName",
        help="Columns names you wish to exclude. Ranges are acceptable inputs, e.g. 100-200")
@click.option("--cohort", metavar="cohort", nargs="+",
        help="""Output csv will be limited to the data of the cohort(s)""")
@click.option("--subjects", nargs="+", metavar="SubID", help="""Subject IDs""")
@click.option("--dropouts", nargs="+", metavar="dropouts", help="""CSV(s) containing eids of participants who have dropped out of the study""")
@click.option("--icd10_count", nargs="+", metavar="ICD10Code", 
        help="Create a binary column for the specified ICD10 conditions only.\nRanges can cross consecutive letters, e.g. A00-B99. Ranges within a letter should be specified, A00-A99.\nA single letter will create a binary column for that group of diseases\nGive the input as 'all' to create a column for every self-report condition")
@click.option("--sr_count", nargs="+", metavar="SRCode", 
        help="Create a binary column for the specified self-report conditions only.\nRanges are acceptable inputs\nGive the input as 'all' to create a column for every self-report condition")
@click.option("--img_only", is_flag=True, help="Use this flag to only keep data acquired during the imaging visit.")
@click.option("--fillna",  help="Use this flag to fill blank cells with the flag input, e.g., NA")
@click.option("--combine", nargs="+", help="""Spreadsheets to combine to output; Please make sure all spreadsheets have an identifier column 'eid'""")
def data_parse(incsv, out, cohort, incon, excon, insr, exsr, incat, excat, inhdr, exhdr, subjects, dropouts, icd10_count_all, icd10_count, sr_count_all, sr_count, img_only, fillna, combine):

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

    def delta_t_months(datafield, dataframe=df):
        imaging_date = pd.Series([datetime.datetime.strptime(v, '%Y-%m-%d') if isinstance(v, str) else np.nan for v in dataframe['53-2.0']])
        online_test_date = pd.Series([datetime.datetime.strptime(v.split('T')[0], '%Y-%m-%d') if isinstance(v, str) else np.nan for v in dataframe[datafield]])
        time_between = online_test_date - imaging_date
        return np.abs(time_between.dt.days)

    # Reading in the Data Source

    incsv_size = os.stat(incsv).st_size # This is in bytes
    if incsv_size > 500000000:
        incsv_reader = pd.read_csv(incsv, chunksize=15000)
        chunk_list = []
        for chunk in incsv_reader:
            click.echo("Loading input...")
            chunk_list.append(chunk)
        df = pd.concat(chunk_list, ignore_index=True)
        del chunk, chunk_list
    else:
        df = pd.read_csv(incsv)

    # Delete empty columns

    df.dropna(axis=1, how="all", inplace=True)
    orig_columns = df.columns

    # Loading in Mapped Category and Datafields Tree

    with open(pkg_resources.resource_filename(__name__, 'mapped_category_tree.json'), 'r') as f:
        entire_cat_tree = json.load(f)
    cat_tree = entire_cat_tree["tree"]

    # Creating Include and Exclude Datafield Lists

    if inhdr is not None:
        if inhdr[0] == "all":
            to_include = [oc.split("-")[0] for oc in orig_columns]
        else:
            to_include = list(inhdr)
    else:
        to_include = []

    if exhdr is not None:
        to_exclude = list(exhdr)
    else:
        to_exclude = []

    if incat is not None:
        for ic in incat:
            if "-" in ic:
                for n in range(int(ic.split("-")[0]), int(ic.split("-")[1])+1):
                    to_include += parse_cat_tree(str(n))
            else:
                to_include += parse_cat_tree(str(ic))

    if excat is not None:
        for ec in excat:
            if "-" in ec:
                for n in range(int(ec.split("-")[0]), int(ec.split("-")[1])+1):
                    to_exclude += parse_cat_tree(str(n))
            else:
                to_exclude += parse_cat_tree(str(ec))

    to_include = list(set(sorted(to_include)))
    to_include = [cat for cat in to_include if not in to_exclude]

    #######################
    ### Processing Time ###
    #######################
    
    # Filter subjects by IDs

    sublist = []
    if subjects is not None:
        sublist += subjects
    if cohort is not None:
        for coh in cohort:
            with open(coh, "r") as f:
                sublist += [l.strip() for l in f.readlines()]

    sublist = [int(subjid) for subjid in sublist]

    if len(sublist) > 0:
        df = df[df.eid.isin(sublist)]

    # Remove study dropouts

    dropids = []

    if dropouts is not None:
        for drop in dropouts:
            dropcsv = pd.read_csv(drop, header=None)
            dropids += dropcsv[0].values.tolist()

        df = df[~df.eid.isin(dropids)]

    # Filter subjects by ICD10 conditions

    coding19 = pd.read_table(pkg_resources.resource_filename(__name__, 'coding19.tsv'), index_col="coding")
    
    main_icd_columns = [c for c in orig_columns if c.startswith("41202-")]
    sec_icd_columns = [c for c in orig_columns if c.startswith("41204-")]
    icd_columns = main_icd_columns + sec_icd_columns

    include_icd = []

    if incon is not None:
        for icd in incon:
            if "-" in icd:
                include_icd += coding19.loc[icd.split("-")[0] : icd.split("-")[1]].index.tolist()
            else:
                include_icd.append(icd)

    exclude_icd = []

    if excon is not None: 
        for icd in excon:
            if "-" in icd:
                exclude_icd += coding19.loc[icd.split("-")[0] : icd.split("-")[1]].index.tolist()
            else:
                exclude_icd.append(icd)

    # N.B. Actual filtering happens below in Self-Report section

    count_icd10 = []

    if icd10_count is not None:
        if icd10_count[0] == "all":
            count_icd10 = icd10.index.tolist()
        else:
            for icd in icd10_count:
                if "-" in icd:
                    count_icd10 += coding19.loc[icd.split("-")[0] : icd.split("-")[1]].index.tolist()
                else:
                    count_icd10.append(icd)

    for ci in count_icd10:
        df.loc[df[icd_columns].isin([ci]).any(axis=1), ci] = 1   
        # There are slice assignment warnings for this 

    # Filter subjects by Self-Report conditions

    coding6 = pd.read_table(pkg_resources.resource_filename(__name__, 'coding6.tsv'), index_col="coding")

    sr_columns = [c for c in orig_columns if c.startswith("20002-")]
    include_srs = []

    if insr is not None:
        for sr in insr:
            if "-" in sr:
                include_srs += list(range(int(sr.split("-")[0]), int(sr.split("-")[1]) + 1))
            else:
                include_srs.append(int(sr))
                
    exclude_srs = []
    
    if exsr is not None:
        for sr in exsr:
            if "-" in sr:
                exclude_srs += list(range(int(sr.split("-")[0]), int(sr.split("-")[1]) + 1)) 
            else:
                exclude_srs.append(int(sr))

    found_icd_includes = df[icd_columns].isin(include_icd).any(axis=1)
    found_sr_includes = df[sr_columns].isin(include_srs).any(axis=1)
    found_includes = np.logical_or(found_icd_includes, found_sr_includes)
    df = df.loc[found_includes]

    found_icd_excludes = df[icd_columns].isin(exclude_icd).any(axis=1)
    found_sr_excludes = df[sr_columns].isin(exclude_srs).any(axis=1)
    found_excludes = np.logical_or(found_icd_excludes, found_sr_excludes)
    df = df.loc[~found_excludes]

    count_sr = []

    if sr_count is not None:
        if sr_count[0] == "all":
            count_sr += coding6.loc[coding6.selectable == "Y"].index.tolist()
        else:
            for sr in sr_count:
                if "-" in sr:
                    count_sr += list(range(int(sr.split("-")[0]), int(sr.split("-")[1]) + 1))
                else:
                    count_sr += int(sr)
    
    for csr in count_sr:
        df.loc[df[sr_columns].isin([csr]).any(axis=1), csr] = 1   
        # There are slice assignment warnings for this 

    df.dropna(axis=1, how="all", inplace=True)

    ### Calculate Float Ages

    df = dc.calculate_float_ages(df)

    ### Create Race Column

    df = dc.add_ethnicity_columns(df)

    ### Create Eductation Columns

    df = dc.add_education_columns(df)

    # Filter data columns

    defcols = ["eid", "31-0.0", "Age1stVisit", "AgeRepVisit", "AgeAtScan", "Race", "ISCED", "YearsOfEducation"]

    includes = [c for c in orig_columns if c.split("-")[0] in to_include]

    if "31-0.0" in includes:
        includes.remove("31-0.0")

    includes = defcols + includes
    df = df[includes]

    ########################
    ### Finishing Up Now ###
    ########################

    ### Create Header Key

    chk.create_html_key(df, arglist, out)

    ### Add Additional Spreadsheets

    if combine is not None:
        for com in combine:
            click.echo('Adding {} data to output spreadsheet'.format(com))
            if com.endswith('csv'):
                add_df = pd.read_csv(com)
            elif com.endswith('xls') or com.endswith('xlsx'):
                try:
                    add_df = pd.read_excel(com)
                except UnicodeDecodeError:
                    add_df = pd.read_excel(com, encoding="ISO-8859-1")
            else:
                add_df = pd.read_table(com)
            df = df.merge(add_df, on='eid', how='left')

    if img_only:
        field_txt = pd.read_table(pkg_resources.resource_filename(__name__, 'field.txt'))
        instance2s = field_txt.loc[field_txt.instance_id == 2, "field_id"].tolist()
        instance2s = [str(in2) for in2 in instance2s]
        drop_non_img_tps = []
        for col in df.columns:
            if (col.split("-")[0] in instance2s):
                if len(col.split("-")) > 1:
                    if col.split("-")[1].split(".")[1] != "2":
                        drop_non_img_tps.append(col)
        df = df.drop(drop_non_img_tps, axis=1)

    if fillna is not None:
        df.fillna(fillna, inplace=True)
    
    df.to_csv(out, index=False)

if __name__ == "__main__":
    ukbb_parser()
