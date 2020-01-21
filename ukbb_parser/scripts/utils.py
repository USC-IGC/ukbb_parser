#!/usr/bin/env python
import pandas as pd
import os

def read_spreadsheet(datafile, filetype='csv'):
    delimiter = ','
    file_reader = pd.read_csv
    if filetype=='unknown':
        if datafile.endswith(".csv"):
            file_reader = pd.read_csv
        elif datafile.endswith(".xls") or datafile.endswith(".xlsx"):
            file_reader = pd.read_excel
            delimiter = None
        elif datafile.endswith(".txt") or datafile.endswith(".tsv"):
            file_reader = pd.read_csv
            delimiter = "\t"
        else:
            file_reader = pd.read_csv
            delimiter='\s+'
    file_size = os.stat(datafile).st_size # This is in bytes
    if file_size > 500000000:
        chunk_size=10000
        if not datafile.endswith(".xls") or not datafile.endswith(".xlsx"):
            with open(datafile, "r") as f:
                first_line = f.readline().strip()
                num_columns = len(first_line.split(delimiter))
                chunk_size = int(chunk_size*6000/num_columns)
            print("Number of Columns:", num_columns, "\nChunk size:", chunk_size)
        if delimiter:
            reader_object = file_reader(datafile, chunksize=chunk_size, encoding='ISO-8859-1', sep=delimiter)
        else:
            reader_object = file_reader(datafile, chunksize=chunk_size, encoding='ISO-8859-1')
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
            dataFrame = file_reader(datafile, encoding='ISO-8859-1', sep=delimiter)
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
                        if item not in cattree.keys():
                            print("Warning: Category {} not found in mapped tree".format(item))
                        else:
                            inner(cattree[item])

    if category not in cattree.keys():
        print("Warning: Category {} not found in mapped tree".format(category))
    else:
        inner(cattree[category])

    return ns.results 
