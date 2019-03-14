#!/usr/bin/env python
import pkg_resources
import pandas as pd
import datetime

def create_html_key(df, arglist, outcsv):
    info_df = pd.read_csv(pkg_resources.resource_filename(__name__, 'data/field.txt'), sep='\t')
    info_df = info_df[['field_id', 'title', 'units', 'encoding_id', 'instance_id', 'notes']]
    info_df['ix'] = info_df.field_id
    info_df.set_index('ix', inplace=True)

    columns = []
    cumu_columns = [columns.append(c.split("-")[0]) for c in df.columns if c.split("-")[0] not in columns]
    info_df = info_df[info_df.field_id.isin([int(c) for c in columns if c.isdigit()])]

    reverse_tbocti = {'time_between_pairs_matching_imaging': '20134-0.0',
                      'time_between_FI_imaging': '20135-0.0',
                      'time_between_Trails_imaging': '20136-0.0',
                      'time_between_SDMT_imaging': '20137-0.0',
                      'time_between_digit_span_imaging': '20138-0.0'}

    out_dict = {}

    for i, col in enumerate(columns):
        setup = {"field_id": col}
        if col == "eid":
            setup["title"] = 'Participant ID'
            setup["notes"] = "Encoded anonymised participant ID"
            out_dict[i] = setup
        elif col == "Age1stVisit":
            setup["title"] = "Age during Initial Visit to Assessment Center"
            setup["notes"] = 'Approximated float version of <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21003">21003-0.0</a>"'
            out_dict[i] = setup
        elif col == "AgeRepVisit":
            setup["title"] = "Age during Repeat Visit to Assessment Center"
            setup["notes"] = 'Approximated float version of <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21003">21003-1.0</a>"'
            out_dict[i] = setup
        elif col == "AgeAtScan":
            setup["title"] = "Age during Scan Visit to Assessment Center"
            setup["notes"] = 'Approximated float version of <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21003">21003-2.0</a>"'
            out_dict[i] = setup
        elif col == "Race":
            setup["title"] = "Participant Race"
            setup["notes"] = 'Converted from and uses same data encoding as <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21000">21000-*.*</a>"'
            out_dict[i] = setup
        elif col == "ISCED":
            setup["title"] = "Encoded anonymised participant ID"
            setup["notes"] = 'Converted from <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=6138">6138-*.*</a>"'
            out_dict[i] = setup
        elif col == "YearsOfEducation":
            setup["title"] = "Estimated Years of Education"
            setup["notes"] = 'Converted from <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=6138">6138-*.*</a>"'
            out_dict[i] = setup
        elif col == 'NP_controls_1':
            setup["title"] = "NeuroPsych Controls 1"
            setup["notes"] = "Exclusion ICD-10 Conditions: A8, B20-B24, B65-B83, C,  F, G, I6, Q0, S04, S06, S07, S08, S09, T36-T46, T48-50; Exclusion SR Conditions: None"
            out_dict[i] = setup
        elif col == 'NP_controls_2':
            setup["title"] = "NeuroPsych Controls 2"
            setup["notes"] = "Exclusion ICD-10 Conditions: Same as NP_controls_1; Exclusion SR Conditions: 1075, 1081, 1086, 1220, 1234, 1243, 1246, 1247, 1250, 1256, 1258, 1260, 1261, 1262, 1264, 1266, 1267, 1286, 1287, 1288, 1291, 1371, 1408, 1434, 1437, 1439"
            out_dict[i] = setup
        elif col == 'CNS_controls_1':
            setup["title"] = "NeuroImaging Controls 1"
            setup["notes"] = "Exclusion ICD-10 Conditions: C70-C72, G, I6, Q0, R90, R940, S01-S09; Exclusion SR Conditions: 1081, 1086, 1266, 1267, 1397, 1434, 1437, 1491, 1626"
            out_dict[i] = setup
        elif col == 'CNS_controls_2':
            setup["title"] = "NeuroImaging Controls 2"
            setup["notes"] = "Exclusion ICD-10 Conditions: ICD-10 conditions from CNS_controls_1 as well as F20-F29, F31, F70-F79; Exclusion SR Conditions: Self-report conditions from CNS_controls_1 as well as 1243, 1289, 1291, 1371"
            out_dict[i] = setup
        elif col in reverse_tbocti.keys():
            label = reverse_tbocti[col].split("-")[0]
            setup["title"] = reverse_tbocti[col]
            setup["units"] = "days"
            setup["notes"] = 'Number of days between online cognitive test (<a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={label}">{label}-*.*</a>) and imaging visit'.format(label=label)
            out_dict[i] = setup
        else:
            try:
                if int(col) in info_df.index.tolist():
                    info_df.loc[int(col), "field_id"] = '<a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={fi}">{fi}-*.*</a>'.format(fi=info_df.loc[int(col), "field_id"]) 
                    info_df.loc[int(col), "encoding_id"] = '<a href="http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id={fi}">{fi}</a>'.format(fi=info_df.loc[int(col), "encoding_id"]) 
                    info_df.loc[int(col), "instance_id"] = '<a href="http://biobank.ctsu.ox.ac.uk/crystal/instance.cgi?id={fi}">{fi}</a>'.format(fi=info_df.loc[int(col), "instance_id"]) 
                    if not isinstance(info_df.loc[int(col), "notes"], float):
                        info_df.loc[int(col), "notes"] = info_df.loc[int(col), "notes"].replace("<", "\<").replace(">", "\>")
                else:
                    info_df.loc[int(col), "field_id"] = '<a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={fi}">{fi}-*.*</a>'.format(fi=col)
            except ValueError:
                continue

    out_df = pd.DataFrame.from_dict(out_dict, orient="index")
    info_df.sort_index(inplace=True)
    try:
        out_df = pd.concat([out_df, info_df], ignore_index=True, sort=True)
    except TypeError:
        out_df = pd.concat([out_df, info_df], ignore_index=True)
    out_df = out_df[['field_id', 'title', 'units', 'encoding_id', 'instance_id', 'notes']]
    out_df.fillna("", inplace=True)
    html = outcsv.split(".csv")[0] + "_header_key.html"
    out_df.to_html(html, escape=False, index=False)

    with open(html, 'r') as f:
        ll = f.read()
    with open(html, 'w') as f:
        todays_date = datetime.datetime.today()
        f.write('<BODY>\n{arglist}</br>was run on {year}/{month}/{day} at {hour}:{minute}:{second}\n</BODY></br></br></br>'.format(arglist=arglist, 
            year=todays_date.year, month=todays_date.month, day=todays_date.day, hour=todays_date.hour, minute=todays_date.minute, second=todays_date.second))
        f.write(ll)
    return
