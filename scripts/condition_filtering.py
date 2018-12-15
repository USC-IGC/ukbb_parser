#!/usr/bin/env python
import pandas as pd

def cohort_filter(df, exc=None, inc=None, sr=None, count=None):
    icd_cols = []

    for c in df.columns:
        if c.startswith('41202') or c.startswith('41204'):
            icd_cols.append(c)
        if exc['sr'] or inc['sr'] or sr:
            if c.startswith('20002'):
                icd_cols.append(c)

    decision = {}
    to_keep = []
    to_discard = []

    df2 = df.copy()
    icd10_conditions = []
    sr_conditions = []

    print("\n\nIt's time to filter by conditions now. This will usually take anywhere between 2-20 minutes... Doo De Doo...\n\n")
    print("Although please note if you haven't created a conditions database and asked for --icd10_count all this can take about an hour.\n\n")

    for i, row in df.iterrows():
        exclude_subject = 0
        for c in icd_cols:
            if exclude_subject == 1:
                break
            try:
                if np.isnan(row[c]):
                    continue
            except TypeError:
                pass
            if c.startswith('41202') or c.startswith('41204'):
                if (count == 'all') or (isinstance(count, list) and row[c] in count):
                    df2 = df2.set_value(i, row[c], 1)
                    if row[c] not in icd10_conditions:
                        icd10_conditions.append(row[c])
                for e in exc['icd']:
                    if row[c].startswith(e):
                        decision[row['eid']] = "exclude"
                        exclude_subject = 1
                        break
                for n in inc['icd']:
                    if row[c].startswith(n):
                        decision[row['eid']] = "include"
                        break
            if c.startswith('20002'):
                if (sr == 'all') or (isinstance(sr, list) and row[c] in sr):
                    df2 = df2.set_value(i, int(row[c]), 1)
                    if row[c] not in sr_conditions:
                        sr_conditions.append(int(row[c]))
                if row[c] in exc['sr']:
                    decision[row['eid']] = "exclude"
                    exclude_subject = 1
                elif row[c] in inc['sr']:
                    decision[row['eid']] = "include"

    for (k,i) in decision.items():
        if i == "exclude":
            to_discard.append(k)
        elif i == "include":
            to_keep.append(k)
    
    df2 = df2[~df2['eid'].isin(to_discard)]
    if (len(inc['icd']) != 0) or (len(inc['sr']) != 0):
        df2 = df2[df2['eid'].isin(to_keep)]

    return df2, icd10_conditions, sr_conditions
    
