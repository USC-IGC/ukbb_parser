#!/usr/bin/env python
import pandas as pd
import os

def read_spreadsheet(datafile, filetype='csv'):
    delimiter = None
    file_reader = pd.read_csv
    if filetype=='unknown':
        if datafile.endswith(".csv"):
            file_reader = pd.read_csv
        elif datafile.endswith(".xls") or datafile.endswith(".xlsx"):
            file_reader = pd.read_excel
        else:
            file_reader = pd.read_csv
            delimiter = "\t"
    file_size = os.stat(datafile).st_size # This is in bytes
    if file_size > 500000000:
        if delimiter:
            reader_object = file_reader(datafile, chunksize=15000, encoding='ISO-8859-1', delimiter=delimiter)
        else:
            reader_object = file_reader(datafile, chunksize=15000, encoding='ISO-8859-1')
        chunk_list = []
        counter = 1
        for chunk in reader_object:
            print("Loading chunk {}...".format(counter))
            counter += 1
            chunk_list.append(chunk)
        dataFrame = pd.concat(chunk_list, ignore_index=True)
        del chunk, chunk_list
    else:
        if delimiter:
            dataFrame = file_reader(datafile, encoding='ISO-8859-1', delimiter=delimiter)
        else:
            dataFrame = file_reader(datafile, encoding='ISO-8859-1')

    return dataFrame

def find_icd10_ix_range(dataFrame, start_loc, end_loc):

    if start_loc not in dataFrame.index.tolist():
        need_start = True
    else:
        need_start = False

    if end_loc not in dataFrame.index.tolist():
        need_end = True
    else:
        need_end = False

    if need_start or need_end:
        for ix in dataFrame.index.tolist():
            if ix.startswith(start_loc) and ix[1].isdigit() and need_start:
                start_loc = ix
                need_start = False
            if ix.startswith(end_loc) and ix[1].isdigit() and need_end:
                end_loc = ix
                need_end = False
            if not need_start and not need_end:
                break

    return start_loc, end_loc

def find_icd10_letter_ixs(dataFrame, letter):
    ixs = []

    for ix in dataFrame.index.tolist():
        if ix.startswith(letter) and ix[1].isdigit():
            ixs.append(ix)

    return ixs
