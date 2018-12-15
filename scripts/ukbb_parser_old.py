#!/usr/bin/env python
import demo_conversion as dc
import category_tree as ct
import condition_filtering as cf
import create_header_key as chk
import pkg_resources
import config
import pandas as pd
import numpy as np
import datetime
import click
import json
import sys
import os

### These are to get rid of warning messages that might worry people. Comment them out when developing and debugging
# import warnings
# warnings.filterwarnings("ignore")

@click.group()
def ukbb_parser():
    pass

### Create Custom Cohorts

@ukbb_parser.command()
@click.option("--cohort", metavar="<cohort>", help="""Cohort Name""")
@click.option("--cohort_file", metavar="<filename>", help="""Name of file to save cohort subjects to""")
@click.option("--excon", nargs="+", metavar="<ICD10Code>",
        help="""ICD10 Diagnosis codes you wish to exclude. \nLeast common denominators are acceptable, e.g. --excon F\nFor ranges, please keep them within the same letter, e.g. F10-20""") 
@click.option("--exsr", nargs="+", metavar="<SRCode>",
        help="Self-Report codes you wish to exclude. \nRanges are acceptable inputs.")
@click.option("--incon", nargs="+", metavar="<ICD10Code>",
        help="""ICD10 Diagnosis codes you wish to include. \nLeast common denominators are acceptable, e.g. --incon F\nFor ranges, please keep them within the same letter, e.g. F10-20""") 
@click.option("--insr", nargs="+", metavar="<SRCode>",
        help="Self-Report codes you wish to include. \nRanges are acceptable inputs.")
def create_cohorts(cohort, cohort_file, excon, exsr, incon, insr):
    incsv_size = os.stat(config.REFERENCE_FILES["incsv"]).st_size # This is in bytes
    if incsv_size > 500000000:
        incsv_reader = pd.read_csv(config.REFERENCE_FILES['incsv'], chunksize=15000)
        chunk_list = []
        for chunk in incsv_reader:
            chunk_list.append(chunk)
        df = pd.concat(chunk_list, ignore_index=True)
        del chunk, chunk_list
    else:
        df = pd.read_csv(config.REFERENCE_FILES['incsv'])
    cf.cohort_filter(df, exc)
    
### Create An ICD10 and Self-Report Condition Reference

@ukbb_parser.command()
@click.option()
@click.option()
def create_condition_dbs():
    incsv_size = os.stat(config.REFERENCE_FILES["incsv"]).st_size # This is in bytes
    if incsv_size > 500000000:
        incsv_reader = pd.read_csv(config.REFERENCE_FILES['incsv'], chunksize=15000)
        chunk_list = []
        for chunk in incsv_reader:
            chunk_list.append(chunk)
        df = pd.concat(chunk_list, ignore_index=True)
        del chunk, chunk_list
    else:
        df = pd.read_csv(config.REFERENCE_FILES['incsv'])
    

### Parse the Data

@ukbb_parser.command()

@click.option("-o", "--out", help="Name of output spreadsheet")
@click.option("--cohort", metavar="<cohort>", 
        help="If a cohort is selected, an ICD10 filter is applied to limit inclusion subject criteria.\nDefault: No filter")
@click.option("--incon", nargs="+", metavar="<ICD10Code>",
        help="ICD10 Diagnosis codes you wish to include. \nLeast common denominators are acceptable, e.g. --incon F\nFor ranges, please keep them within the same letter, e.g. F10-20") 
@click.option("--excon", nargs="+", metavar="<ICD10Code>",
        help="ICD10 Diagnosis codes you wish to exclude. \nLeast common denominators are acceptable, e.g. --excon F\nFor ranges, please keep them within the same letter, e.g. F10-20") 
@click.option("--insr", nargs="+", metavar="<SRCode>",
        help="Self-Report codes you wish to include. \nRanges are acceptable inputs.")
@click.option("--exsr", nargs="+", metavar="<SRCode>",
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
@click.option("--subjects", nargs="+", metavar="SubID",
        help="A list or text file containing the subject IDs for whom you want data.\nIf using a text file, please list one subject per line.")
@click.option("--freesurfer", is_flag=False, help="Use this flag to also get the QCed cortical data")
@click.option("--icd10_count", nargs="+", metavar="ICD10Code", 
        help="Create a binary column for the specified ICD10 conditions only.\nRanges can cross consecutive letters, e.g. A00-B99. Ranges within a letter should be specified, A00-A99.\nA single letter will create a binary column for that group of diseases\nGive the input as 'all' to create a column for every self-report condition")
@click.option("--sr_count", nargs="+", metavar="SRCode", 
        help="Create a binary column for the specified self-report conditions only.\nRanges are acceptable inputs\nGive the input as 'all' to create a column for every self-report condition")
@click.option("--img_only", action="store_true", help="Use this flag to only keep data acquired during the imaging visit.")
@click.option("--fillna",  help="Use this flag to fill blank cells with the flag input, e.g., 'NA'")
def data_parse(out, cohort, incon, excon, insr, exsr, incat, excat, inhdr, exhdr, subjects, freesurfer, icd10_count_all, icd10_count, sr_count_all, sr_count, img_only, fillna):

    arglist = ' '.join(sys.argv)

    ### Setting Up

    pd.set_option("display.max_colwidth", 500)

    # HTML header key
    ukbb_html = pd.read_html(config.REFERENCE_FILES['ukbb_html'])[0]
    if len(ukbb_html) > 1:
        header_html = ukbb_html[1]
    else:
        header_html = ukbb_html[0]
    del ukbb_html

    # Reading in the Data Source
    incsv_size = os.stat(config.REFERENCE_FILES["incsv"]).st_size # This is in bytes
    if incsv_size > 500000000:
        incsv_reader = pd.read_csv(config.REFERENCE_FILES['incsv'], chunksize=15000)
        chunk_list = []
        for chunk in incsv_reader:
            chunk_list.append(chunk)
        df = pd.concat(chunk_list, ignore_index=True)
        del chunk, chunk_list
    else:
        df = pd.read_csv(config.REFERENCE_FILES['incsv'])

    columns = df.columns
    # I need to add this json to the package
    with open(pkg_resources.resource_filename(__name__, 'mapped_category_tree.json'), 'r') as f:
        entire_cat_tree = json.load(f)
    cat_tree = entire_cat_tree["tree"]

    ### Calculate Float Ages

    df = dc.calculate_float_ages(df)

    ### Create Race Column

    df = dc.add_ethnicity_columns(df)

    ### Create Eductation Columns

    df = dc.add_education_columns(df)

    ### Create Cohort Columns
    cohorts = list(config.COHORT.keys())

    for c in cohorts:
        cohort_file = config.COHORT[c]['cohort_file']
        with open(cohort_file, 'r') as f:
            subject_list = [int(l.strip()) for l in f.readlines()] 
        cohortdf = pd.DataFrame.from_dict({'eid': subject_list, c: np.ones(len(subject_list))}) 
        df = df.merge(cohortdf, on='eid', how='left')

    ### Add Additional Data Columns
    ### For example, GWAS component data

    if len(config.ADDITIONAL_SPREADSHEETS) > 0:
        for k, v in config.ADDITIONAL_SPREADSHEETS.items():
            print('Adding %s data to output spreadsheet' %k)
            if v['spreadsheet_file'].endswith('csv'):
                add_df = pd.read_csv(v['spreadsheet_file'])
            elif v['spreadsheet_file'].endswith('xls') or v['spreadsheet_file'].endswith('xlsx'):
                try:
                    add_df = pd.read_excel(v['spreadsheet_file'])
                except UnicodeDecodeError:
                    add_df = pd.read_excel(v['spreadsheet_file'], encoding="ISO-8859-1")
            else:
                try:
                    if 'delimiter' in v.keys():
                        if v['delimiter'] == 'whitespace':
                            add_df = pd.read_table(v['spreadsheet_file'], delim_whitespace=True)
                        else:
                            add_df = pd.read_table(v['spreadsheet_file'], delimiter=v['delimiter'])
                    else:
                        add_df = pd.read_table(v['spreadsheet_file'], delimiter='\t')
                except:
                    print("Additional spreadsheet is in an unfamiliar file format. Please double check the file.")
                    sys.exit(1)
            if 'join_on' in v.keys():
                df = df.merge(add_df, left_on='eid', right_on=v['join_on'], how='outer')
            else:
                df = df.merge(add_df, on='eid', how='outer')

            del add_df # To clear memory

### Functions... We like functions

time_between_online_cognitive_test_and_imaging = {'20134-0.0': 'time_between_pairs_matching_imaging',
                                                '20135-0.0': 'time_between_FI_imaging',
                                                '20136-0.0': 'time_between_Trails_imaging',
                                                '20137-0.0': 'time_between_SDMT_imaging',
                                                '20138-0.0': 'time_between_digit_span_imaging'}
# reverse_tbocti = dict((v,k) for k,v in time_between_online_cognitive_test_and_imaging.items())

def delta_t_months(datafield):
    imaging_date = pd.Series([datetime.datetime.strptime(v, '%Y-%m-%d') if isinstance(v, str) else np.nan for v in df['53-2.0']])
    online_test_date = pd.Series([datetime.datetime.strptime(v.split('T')[0], '%Y-%m-%d') if isinstance(v, str) else np.nan for v in df[datafield]])
    time_between = online_test_date - imaging_date
    return np.abs(time_between.dt.days/30.5 )



    ### Time to start actually getting what we want

    # Filter by Subject List

    if subjects:
        subs = []
        for s in subjects:
            try:
                with open(s, 'r') as f:
                    subs += [int(l.strip()) for l in f.readlines()]
        except:
            subs.append(s)

        df = df[df['eid'].isin(subs)]

    # Filter by Preset Cohort

    if cohort is not None:
        if cohort not in config.COHORT.keys():
            print("\n\nCohort not found. Please double check your command line input or run the create_cohorts command\n\n")
            sys.exit(1)
        cohort_file = config.COHORT[cohort]['cohort_file']
        if not os.path.exists(cohort_file):
            print("\n\nPreset cohort file not found\nPlease run the create_cohorts command\n\n")
            sys.exit(1)
        else:
            with open(cohort_file, 'r') as f:
                subs = [int(l.strip()) for l in f.readlines()]
            df = df[df['eid'].isin(subs)]

    # Filter by ICD10 Conditions

    exc = {'icd': [], 'sr': []}

if excon:
    for e in excon:
        if "-" in e:
            l = e.split("-")[0][0]
            s = e.split("-")[0][1:]
            f = e.split("-")[1]
            for r in range(int(s),int(f)+1):
                if s[0] == "0" and len(s) == 2:
                    exc['icd'].append(l+"%02d" %r)
                elif s[0] == "0" and len(s) == 3:
                    exc['icd'].append(l+"%03d" %r)
                else:
                    exc['icd'].append(l+str(r))
        else:
            exc['icd'].append(e)
    exc['icd'] = sorted(exc['icd'])

if exsr:
    for e in exsr:
        if "-" in e:
            s = e.split("-")[0]
            f = e.split("-")[1]
            for r in range(int(s),int(f)+1):
                exc["sr"].append(float(r))
        else:
            exc['sr'].append(float(e))
    exc['sr'] = sorted(exc['sr'])

inc = {'icd': [], 'sr': []}
if incon:
    for i in incon:
        if "-" in i:
            l = i.split("-")[0][0]
            s = i.split("-")[0][1:]
            f = i.split("-")[1]
            for r in range(int(s),int(f)+1):
                if s[0] == "0" and len(s) == 2:
                    inc['icd'].append(l+"%02d" %r)
                elif s[0] == "0" and len(s) == 3:
                    inc['icd'].append(l+"%03d" %r)
                else:
                    inc['icd'].append(l+str(r))
        else:
            inc['icd'].append(i)

if insr:
    for i in insr:
        if "-" in i:
            s = i.split("-")[0]
            f = i.split("-")[1]
            for r in range(int(s),int(f)+1):
                inc['sr'].append(float(r))
        else:
            inc['sr'].append(float(i))
    inc['sr'] = sorted(inc['sr'])

condense = []
if icd10_count_all:
    counter = 'all'
elif icd10_count:
    counter = []
    saveme = pd.read_table(pkg_resources.resource_filename(__name__, 'coding19.tsv'))
    for a in icd10_count:
        if "-" in a:
            l1 = a.split("-")[0][0]
            s = a.split("-")[0][1:]
            l2 = a.split("-")[1][0]
            f = a.split("-")[1][1:]
            try:
                if s == "00":
                    s = saveme[saveme["helpme"] == "%s start" %l1].index.values[0]
                else:
                    s = saveme[saveme["coding"] == "%s%s" %(l1, s)].index.values[0]
                if f == "99":
                    f = saveme[saveme["helpme"] == "%s stop" %l2].index.values[0]
                else:
                    f = saveme[saveme["coding"] == "%s%s" %(l2, f)].index.values[0]
            except IndexError:
                print("\n\nPlease check to make sure that the start/stop criterion of the range you're using is selectable\n\n")
                sys.exit(1)
            counter += list(saveme["coding"][s:f+1])
        elif len(a) == 1:
            s = saveme[saveme["helpme"] == "%s start" %a].index.values[0]
            f = saveme[saveme["helpme"] == "%s stop" %a].index.values[0]
            counter += list(saveme["coding"][s:f+1])
            condense.append(a)
        else:
            counter.append(a)
else:
    counter=None

if sr_count_all:
    sr = 'all'
elif sr_count:
    sr = []
    for a in sr_count:
        if "-" in a:
            s = a.split("-")[0]
            f = a.split('-')[1]
            for r in range(int(s), int(f)+1):
                sr.append(r)
        else:
            sr.append(float(a))
else:
    sr = None

if (cohort == 'NeuroFree_Strict') or (cohort == 'Healthy'):
    df, icd10_conditions, sr_conditions  = cf.cohort_filter(df, exc, inc, sr=sr, count=counter)
elif (len(exc['icd']) != 0) or (len(inc['icd']) != 0) or (counter is not None) or (len(exc['sr']) != 0) or (len(inc['sr']) != 0) or (sr is not None):
    df, icd10_conditions, sr_conditions = cf.cohort_filter(df, exc, inc, sr=sr, count=counter)

    # Filtering a Specific Column by a Specific Value

    # if filter:
    #     for f in filter:
    #         c = f.split("=")[0]
    #         v = f.split("=")[1]
    #         for i, val in enumerate(df[c]):
    #             try:
    #                 if not np.isnan(val):
    #                     t = type(val)
    #                     break
    #             except:
    #                 t = type(val)
    #                 break
    #         df = df[df[c] == t(v)]

    # Filtering by Data Field Categories and Headers

to_include = []

if incat:
    cats = []
    for a in incat:
        if "-" in a:
            cats += [str(n) for n in range(int(a.split('-')[0]), int(a.split('-')[1])+1)]
        else:
            cats.append(a)

    for c in cats:
        try:
            to_include += ct.get_category_tree(c)
        except KeyError:
            print(map_key_error_msg %c)
            to_include += ct.get_category_tree_web(c)

if inhdr:
    for hdr in inhdr:
        if hdr == 'all':
            break
        if "-" in hdr:
            to_include += [str(n) for n in range(int(hdr.split('-')[0]), int(hdr.split('-')[1])+1)]
        else:
            to_include.append(hdr)

to_exclude = []

if excat:
    cats = []
    for a in excat:
        if "-" in a:
            cats += [str(n) for n in range(int(a.split('-')[0]), int(a.split('-')[1])+1)]
        else:
            cats.append(a)

    for c in cats:
        try:
            to_exclude += ct.get_category_tree(c)
        except KeyError:
            print(map_key_error_msg %c)
            to_exclude += ct.get_category_tree_web(c)
     
if exhdr:
    for hdr in exhdr:
        if "-" in hdr:
            to_exclude += [str(n) for n in range(int(hdr.split('-')[0]), int(hdr.split('-')[1])+1)]
        else:
            to_exclude.append(hdr)

### Winding Down

final_includes = [] # in terms of data fields
if inhdr and (inhdr[0] == 'all'):
    for datafield in [c.split("-")[0] for c in columns]:
        if (datafield not in to_exclude) and (datafield not in final_includes):
            final_includes.append(datafield)
elif inhdr or incat:
    for datafield in to_include:
        if (datafield not in to_exclude) and (datafield not in final_includes):
            final_includes.append(datafield)
else:
    final_includes += to_include
        
# name_map = pd.read_csv(pkg_resources(__name__, 'sorted_mapped_variable_names.csv'), index_col='datafield')
# column_rename = {}
df.dropna(axis=1, inplace=True, how='all')


final_columns = [dc for dc in defcols if dc in df.columns]
remaining_columns = [c for c in columns if c in df.columns]

for c in remaining_columns:
    if c in defcols:
        continue
    
    datafield = c.split("-")[0] 
    tp = c.split("-")[1].split(".")[0]
    inst = c.split("-")[1].split(".")[1]
    if datafield in final_includes:
        if (img_only) and (tp != '2') and (datafield not in ['20002', '41202', '41204']):
            continue
        # if (img_only) and (tp != 2) and (datafield not in ['20002', '41202', '41204']):
        #     if ("%s-2.0" %datafield in columns) or ("%s-2.1" %datafield in columns):
        #         continue
        # if int(datafield) in name_map.index:
        #     column_rename[c] = "{new_name}_{tp}.{inst}".format(new_name=name_map.loc[int(datafield), "colname"], tp=tp, inst=inst)

        final_columns.append(c)

        if c in time_between_online_cognitive_test_and_imaging.keys():
            df[time_between_online_cognitive_test_and_imaging[c]] = delta_t_months(c)
            final_columns.append(time_between_online_cognitive_test_and_imaging[c])

try:
    inventory = []
    multiples = []
    icd10_conditions = [icd10con for icd10con in icd10_conditions if icd10con in df.columns]
    if isinstance(counter, list):
        for cr in counter:
            if cr not in icd10_conditions:
                continue
            if (cr in inventory) and (cr not in multiples):
                multiples.append(cr)
            else:
                inventory.append(cr)

    for cd in condense:
        conditions = list(icd10_conditions)
        condensed = []
        for cn in conditions:
            if cn.startswith(cd):
                condensed.append(cn)
                icd10_conditions.remove(cn)
        rowsum = np.sum(df[condensed], axis=1)
        icd10_conditions.append(cd)
        df[cd] = (rowsum > 0).astype(int)
        df[cd] = df[cd].replace(0,np.nan)
    df = df[final_columns + sorted(icd10_conditions + multiples) + sorted(sr_conditions)]
except NameError:
    df = df[final_columns]

    ### Writing the Output Spreadsheet

    df.rename(columns=column_rename, inplace=True)

    if fillna is not None:
        output.fillna(fillna, inplace=True)

    try:
        df.to_csv(out, index=False)
    except UnicodeEncodeError:
        df.to_csv(out, index=False, encoding='utf-8')

    ### Writing the Output Header Key
    chk.create_html_key(df[final_columns], header_html, out, arglist)

if __name__ == "__main__":
    ukbb_parser()
