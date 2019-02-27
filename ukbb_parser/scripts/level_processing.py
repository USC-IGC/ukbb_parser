#!/usr/bin/env python
import pandas as pd

def level_processing(dataFrame, datatype, datafields, level_map, code, level, sublevels):
    # Parse Input
    if level != "S":
        level = int(level)

    if datatype == "icd10":
        code_column = "Coding"
        parent_column = "Parent"
        selectable_column = "Selectable"
        col_pref = "icd10_"
        level_map_df = pd.read_csv(level_map, index_col=code_column)
    elif datatype in ["self_report", "careers"]:
        code_column = "coding"
        parent_column = "parent_id"
        selectable_column = "selectable"
        if datatype == "self_report":
            col_pref = "sr_"
        elif datatype == "careers":
            col_pref = "job_"
        level_map_df = pd.read_csv(level_map, index_col=code_column)

    # Breakdown Input Codes and Inventory
    if level == "S":
        selectable = level_map.loc[level_map[selectable_column] == "Y"]
        codes_to_inventory = selectable.index.tolist()
        for s in codes_to_inventory:
            dataFrame.loc[dataFrame[datafields].isin([s]).any(axis=1), col_pref+str(s).replace(" ", "_")] = 1   
            return dataFrame
    else:
        codes_dict = {}
        codes_to_inventory = get_level_codes(datatype, level_map_df, level, code)
        for cti in codes_to_inventory:
            codes_dict[cti] = {"branches": [cti],
                               "leaves": []}
        inventory_codes_dict = get_sublevel_data(codes_dict, level_map_df, parent_column, selectable_column, level)
        for k,v in inventory_codes_dict.items():
            dataFrame.loc[dataFrame[datafields].isin(v['leaves']).any(axis=1), col_pref+str(k).replace(" ", "_")] = 1   
            if sublevels == True:
                for l in v['leaves']:
                    dataFrame.loc[dataFrame[datafields].isin([l]).any(axis=1), col_pref+str(l).replace(" ", "_")] = 1   
        return dataFrame

def get_sublevel_data(codes_dict, level_map, parent_column, selectable_column, level):
    while level < 5:
        for k, v in codes_dict.items():
            branches = []
            for c in v['branches']:
                children = level_map.loc[level_map[parent_column] == c]
                branches += children.loc[children[selectable_column] == "N"].index.tolist()
                codes_dict[k]['leaves'] += children.loc[children[selectable_column] == "Y"].index.tolist()
                if level_map.loc[c, selectable_column] == "Y":
                    codes_dict[k]['leaves'].append(c)
            codes_dict[k]['branches'] = branches
        level += 1

    return codes_dict


def get_level_codes(datatype, level_map, level, code):
    codes_to_inventory = []

    if datatype == "icd10":
        if code == "all":
            codes_to_inventory = level_map.loc[level_map.Level == level].index.tolist()
        elif ("-" in code) and (level in [3, 4]):
            level_df = level_map.loc[level_map.Level == level]
            codes_to_inventory += level_df.loc[code.split("-")[0]+"0" : code.split("-")[1]+"99999999"].index.tolist()
        elif "-" in code:
            level_df = level_map.loc[level_map.Level == level]
            codes_to_inventory += level_df.loc[code.split("-")[0] : code.split("-")[1]].index.tolist()
        else:
            codes_to_inventory += level_map.loc[code+"0" : code+"99999999"].index.tolist()
    elif datatype in ["self_report", "careers"]:
        if code == "all":
            codes_to_inventory = level_map.loc[level_map.Level == level].index.tolist()
        elif "-" in code:
            level_df = level_map.loc[level_map.Level == level]
            code_range += list(range(int(code.split("-")[0]), int(code.split("-")[1]) + 1))
            codes_to_inventory += level_df.loc[level_df.index.isin(code_range)].index.tolist()
        else:
            codes_to_inventory.append(int(code))
    return codes_to_inventory

