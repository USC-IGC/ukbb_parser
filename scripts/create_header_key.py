#!/usr/bin/env python
import pkg_resources
import pandas as pd
import datetime

def create_html_key(df, arglist, outcsv):
    info_df = pd.read_table(pkg_resources.resource_filename(__name__, 'field.txt'))
    info_df = info_df[['field_id', 'title', 'units', 'encoding_id', 'instance_id', 'notes']]
    info_df['ix'] = info_df.field_id
    info_df.set_index('ix', inplace=True)

    columns = [c.split("-")[0] for c in df.columns]
    columns = list(set(columns))
    info_df = info_df[info_df.ix.isin([int(c) for c in columns if c.isdigit()])]

    reverse_tbocti = {'time_between_pairs_matching_imaging': '20134-0.0',
                      'time_between_FI_imaging': '20135-0.0',
                      'time_between_Trails_imaging': '20136-0.0',
                      'time_between_SDMT_imaging': '20137-0.0',
                      'time_between_digit_span_imaging': '20138-0.0'}

    out_dict = {}

    for i, col in enumerate(columns):
        setup = {"field_id": col}
        if col == "eid":
            setup["title"].append('Participant ID')
            setup["notes"].append("Encoded anonymised participant ID")
            out_dict[i] = setup
        elif col == "Age1stVisit":
            setup["title"].append("Age during Initial Visit to Assessment Center")
            setup["notes"].append('Approximated float version of <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21003">21003-0.0</a>"')
            out_dict[i] = setup
        elif col == "AgeRepVisit":
            setup["title"].append("Age during Repeat Visit to Assessment Center")
            setup["notes"].append('Approximated float version of <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21003">21003-1.0</a>"')
            out_dict[i] = setup
        elif col == "AgeAtScan":
            setup["title"].append("Age during Scan Visit to Assessment Center")
            setup["notes"].append('Approximated float version of <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21003">21003-2.0</a>"')
            out_dict[i] = setup
        elif col == "Race":
            setup["title"].append("Participant Race")
            setup["notes"].append('Converted from and uses same data encoding as <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=21000">21000-*.*</a>"')
            out_dict[i] = setup
        elif col == "ISCED":
            setup["title"].append("Encoded anonymised participant ID")
            setup["notes"].append('Converted from <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=6138">6138-*.*</a>"')
            out_dict[i] = setup
        elif col == "YearsOfEducation":
            setup["title"].append("Estimated Years of Education")
            setup["notes"].append('Converted from <a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=6138">6138-*.*</a>"')
            out_dict[i] = setup
        elif col in reverse_tbocti.keys():
            label = reverse_tbocti[col].split("-")[0]
            setup["title"].append(reverse_tbocti[col])
            setup["notes"].append('Number of days between online cognitive test (<a href="http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={label}">{label}-*.*</a>) and imaging visit'.format(label=label))
            out_dict[i] = setup
        else:
            info_df.loc[int(col), "field_id"] = "http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={}".format(info_df.loc[int(col), "field_id"]) 
            info_df.loc[int(col), "encoding_id"] = "http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={}".format(info_df.loc[int(col), "encoding_id"]) 
            info_df.loc[int(col), "instance_id"] = "http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id={}".format(info_df.loc[int(col), "instance_id"]) 

    out_df = pd.DataFrame.from_dict(out_dict, orient="index")
    out_df = pd.concat([out_df, info_df], ignore_index=True)
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
