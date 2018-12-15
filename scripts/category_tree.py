#!/usr/bin/env python
import pandas as pd

map_key_error_msg = """


Hmm... We couldn't find %s in the pre-parsed tree.
We're searching through the website now.
This might take some extra time.

Please note that the website has a few infinite loops, so if the parsing takes more than an hour, please kill the command and email Alyssa Zhu <alyssahz@usc.edu> the requested category numbers. Thanks!


"""

def get_category_tree(category, mapped_json=cattree):
    fields = []

    if "categories" in mapped_json[category].keys():
        subcategories = mapped_json[category]["categories"]
        while len(subcategories) != 0:
            subcategories1 = []
            for s in subcategories:
                if "categories" in mapped_json[s].keys():
                    subcategories1 += mapped_json[s]["categories"]
                if "fields" in mapped_json[s].keys():
                    fields += mapped_json[s]["fields"]
            subcategories = subcategories1
    if "fields" in mapped_json[category].keys():
        fields += mapped_json[category]["fields"]

    return fields


def get_category_tree_web(category):
 
    fields = []

    df = pd.read_html("http://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id="+category)
    if df[0].ix[0][0] == "Field ID":
        fields += list(df[0][0].values[1:])
    else:
        subcategories = df[0][0].values[1:]
        while len(subcategories) != 0:
            subcategories1 = []
            for s in subcategories:
                df_sub = pd.read_html("http://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id="+s)
                if df_sub[0].ix[0][0] == "Field ID":
                    fields += list(df_sub[0][0].values[1:])
                else:
                    subcategories1 += list(df_sub[0][0].values[1:])
            subcategories = subcategories1

    return fields
