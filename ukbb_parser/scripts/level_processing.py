#!/usr/bin/env python
import pandas as pd
from ukbb_parser.scripts.utils import find_icd10_ix_range

def level_processing(dataFrame, datatype, datafields, level_map, code, level, sublevels):
    # Parse Input
    if level != "S":
        level = int(level)

    if datatype == "icd10":
        code_column = "Coding"
        parent_column = "Parent"
        node_column = "Node"
        selectable_column = "Selectable"
        col_pref = "icd10_"
        level_map_df = pd.read_csv(level_map, index_col=code_column)
    elif datatype in ["self_report", "careers"]:
        code_column = "coding"
        parent_column = "parent_id"
        node_column = "node_id"
        selectable_column = "selectable"
        if datatype == "self_report":
            col_pref = "sr_"
        elif datatype == "careers":
            col_pref = "job_"
        level_map_df = pd.read_csv(level_map, index_col=code_column)

    # Breakdown Input Codes and Inventory
    if level == "S":
        selectable = level_map_df.loc[level_map_df[selectable_column].isin(["Y", "Yes"])]
        codes_to_inventory = selectable.index.tolist()
        for s in codes_to_inventory:
            dataFrame[col_pref+str(s).replace(" ", "_")] = dataFrame[datafields].isin([s]).any(axis=1).astype(int)
        return dataFrame
    else:
        codes_dict = {}
        codes_to_inventory = get_level_codes(datatype, level_map_df, level, code)
        for cti in codes_to_inventory:
            codes_dict[cti] = {"branches": [cti],
                               "leaves": []}
        inventory_codes_dict = get_sublevel_data(codes_dict, level_map_df, parent_column, node_column, selectable_column, level)
        for k,v in inventory_codes_dict.items():
            dataFrame[col_pref+str(k).replace(" ", "_")] = dataFrame[datafields].isin(v['leaves']).any(axis=1).astype(int)
            if sublevels == True:
                for l in v['leaves']:
                    dataFrame[col_pref+str(l).replace(" ", "_")] = dataFrame[datafields].isin([l]).any(axis=1).astype(int)
        return dataFrame

def get_sublevel_data(codes_dict, level_map, parent_column, node_column, selectable_column, level):
    while level < 5:
        for k, v in codes_dict.items():
            branches = []
            for c in v['branches']:
                try:
                    node_id = level_map.loc[c, node_column]
                    if level_map.loc[c, selectable_column] in ["Y", "Yes"]:
                        codes_dict[k]['leaves'].append(c)
                    sr_neg_1 = False
                except KeyError:
                    node_id = level_map.loc[level_map.meaning == c, node_column].values[0]
                    sr_neg_1 = True
                if node_id in level_map[parent_column].tolist():
                    children = level_map.loc[level_map[parent_column] == node_id]
                elif str(node_id) in level_map[parent_column].tolist():
                    children = level_map.loc[level_map[parent_column] == str(node_id)]
                else:
                    continue
                if sr_neg_1:
                    branches += children.loc[children[selectable_column].isin(["N", "No"]), "meaning"].tolist()
                else:
                    branches += children.loc[children[selectable_column].isin(["N", "No"])].index.tolist()
                codes_dict[k]['leaves'] += children.loc[children[selectable_column].isin(["Y", "Yes"])].index.tolist()
            codes_dict[k]['branches'] = branches
        level += 1

    return codes_dict


def get_level_codes(datatype, level_map, level, code):
    codes_to_inventory = []

    if datatype == "icd10":
        if code == "all":
            codes_to_inventory = level_map.loc[level_map.Level == level].index.tolist()
        elif ("-" in code) and ("Block" not in code):
            start_loc = code.split("-")[0] 
            end_loc = code.split("-")[1]
            level_df = level_map.loc[level_map.Level == level]
            start_loc, end_loc = find_icd10_ix_range(level_df, start_loc, end_loc)
            codes_to_inventory += level_df.loc[start_loc: end_loc].index.tolist()
        else:
            codes_to_inventory.append(code)
    elif datatype == "self_report":
        if code == "all":
            level_codes = level_map.loc[level_map.Level == level]
            codes_to_inventory = []
            for i, row in level_codes.iterrows():
                if i == -1:
                    codes_to_inventory.append(row["meaning"])
                else:
                    codes_to_inventory.append(int(i))
        elif "-" in code:
            level_df = level_map.loc[level_map.Level == level]
            code_range += list(range(int(code.split("-")[0]), int(code.split("-")[1]) + 1))
            codes_to_inventory += level_df.loc[level_df.index.isin(code_range)].index.tolist()
        elif not code[0].isdigit():
            codes_to_inventory.append(code)
        else:
            codes_to_inventory.append(int(code))
    elif datatype ==  "careers":
        if code == "all":
            codes_to_inventory = level_map.loc[level_map.Level == level].index.tolist()
        elif "-" in code:
            level_df = level_map.loc[level_map.Level == level]
            code_range += list(range(int(code.split("-")[0]), int(code.split("-")[1]) + 1))
            codes_to_inventory += level_df.loc[level_df.index.isin(code_range)].index.tolist()
        else:
            codes_to_inventory.append(int(code))
    return codes_to_inventory

