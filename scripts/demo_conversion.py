#!/usr/bin/env python
import numpy as np

def calculate_float_ages(dataFrame):
    for i, v in enumerate(["Age1stVisit", "AgeRepVisit", "AgeAtScan"]):
        try:
            y = [int(d.split('-')[0]) for d in dataFrame["53-%i.0" %i]]
            m = [int(d.split('-')[1]) for d in dataFrame["53-%i.0" %i]]
            dataFrame[v] = y - dataFrame['34-0.0'] + (m-dataFrame["52-0.0"])/12.
        except AttributeError:
            ages = []
            for j, d in enumerate(dataFrame["53-%i.0" %i]):
                if isinstance(d, str):
                    y = int(d.split('-')[0])
                    m = int(d.split('-')[1])
                    ages.append(y - dataFrame['34-0.0'][j] + (m-dataFrame["52-0.0"][j])/12.)
                else:
                    ages.append(np.nan)
            dataFrame[v] = ages
    return dataFrame

def add_ethnicity_columns(dataFrame):

    def convert_ethnicity(val):
        if np.isnan(val):
            new_val = np.nan
        elif len(str(int(val))) == 4:
            new_val = int(str(int(val))[0])
        elif val == 5:
            new_val = 3 
        elif val < 0:
            new_val = np.nan
        else:
            new_val = val
        return new_val 

    ethn = []

    for c in dataFrame.columns:
        if c.startswith('21000'):
            ethn.append(c)

    converted_ethn = dataFrame[ethn]

    for c in ethn:
        converted_ethn[c] = [convert_ethnicity(v) for v in converted_ethn[c]]

    single_ethn = []

    for i, row in converted_ethn.iterrows():
        if len(converted_ethn.loc[i, ethn].value_counts()) > 1:
            possibilities = list(converted_ethn.loc[i, ethn].value_counts().keys())
            if 2 in possibilities:
                single_ethn.append(2)
            elif 6 in possibilities:
                possibilities.remove(6)
                single_ethn.append(possibilities[0])
            else:
                single_ethn.append(possibilities[0])
        elif len(converted_ethn.loc[i, ethn].value_counts()) == 0:
            single_ethn.append(np.nan)
        else:
            single_ethn.append(converted_ethn.loc[i, ethn].value_counts().keys()[0])

    dataFrame['Race'] = single_ethn

return dataFrame

def add_education_columns(dataFrame):

    ukbb2eduyrs = {1: 19,
                   2: 13,
                   3: 10,
                   4: 10,
                   5: 19,
                   6: 15,
                   -7: 7,
                   -3: np.nan}

    eduyrs2isced = {19: 5,
                    15: 6,
                    13: 3,
                    10: 2,
                    7: 1}

    quals = []

    for c in dataFrame.columns:
        if c.startswith('6138-'):
            quals.append(c)

    converted_quals = dataFrame[['eid'] + quals]
    for c in quals:
        converted_quals = converted_quals.replace({c: ukbb2eduyrs})

    dataFrame['YearsOfEducation'] = np.nanmax(converted_quals[quals], axis=1)
    dataFrame['ISCED'] = dataFrame['YearsOfEducation'].replace(eduyrs2isced)

    return dataFrame
