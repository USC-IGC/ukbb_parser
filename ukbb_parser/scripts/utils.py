#!/usr/bin/env python
import pandas as pd
import os

def read_csv(csv):
    csv_size = os.stat(csv).st_size # This is in bytes
    if csv_size > 500000000:
        csv_reader = pd.read_csv(csv, chunksize=15000)
        chunk_list = []
        for chunk in csv_reader:
            print("Loading {}...".format(csv))
            chunk_list.append(chunk)
        dataFrame = pd.concat(chunk_list, ignore_index=True)
        del chunk, chunk_list
    else:
        dataFrame = pd.read_csv(csv)
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
