import psycopg2
import copy
import parameters
import alcohol_clinicaltrials_lib as acl
import pandas as pd
import numpy as np

# helper functions
def generate_pairs(list_a, list_b):
    """
    generate pairs to create a list of lists
    :param list_a:
    :param list_b:
    :return:
    """
    pair_list_dict = {}
    empty_list = []
    for i, a in enumerate(list_a):
        tmp_list = []
        for j, b in enumerate(list_b):
            tmp_list.append(None)
            key = str(a) + str(b)
            # pair_list_dict[key] = [i+1, j+1]
            pair_list_dict[key] = [i, j]
        empty_list.append(tmp_list)
    return(pair_list_dict, empty_list)


def df2list_of_lists(data_frame):
    """
    convert a dataframe with column and row headers (index) to a list of lists for display
    :param data_frame:
    :return:
    """
    first_row = [""] + list(data_frame.columns.values)
    row_headers = list(data_frame.index.values)
    data = data_frame.values
    list_of_lists = [first_row]
    for idx in xrange(len(row_headers)):
        list_of_lists.append([row_headers[idx]] + list(data[idx]))
    return(list_of_lists)


def generate_study_link(nct_id, prefix=None):
    """
    generate the link to the orignal study page on clinicaltrials.gov
    :param nct_id:
    :param prefix:
    :return:
    """
    if prefix is None:
        prefix = "https://clinicaltrials.gov/show/"
    return(prefix+nct_id)


def get_table_colnames(table_name, cur=None, acl_db_parameters=parameters.acl_db_params):
    """extract the column names of a table"""
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    tmp_cmd = "SELECT * FROM " + table_name + " LIMIT 0"
    cur.execute(tmp_cmd)
    colnames = [desc[0] for desc in cur.description]
    return(colnames)


def list2dict(key_list, value_list):
    """
    convert two lists to a dictionary
    :param key_list:
    :param value_list:
    :return:
    """
    my_dict = {}
    for key, value in zip(key_list, value_list):
        my_dict[key] = value
    return(my_dict)


def vstack_list(list_of_lists):
    """
    stack list of lists [[1, 2, 3], [a, b, c]] into [[1, a], [2, b], [3, c]]
    :param list_of_lists:
    :return:
    """
    stacked_list = [[] for _ in xrange(len(list_of_lists[0]))]
    for tmp_list in list_of_lists:
        for idx, item in enumerate(tmp_list):
            stacked_list[idx].append(item)
    return(stacked_list)


def db2table_dict_list(table_name, nct_id, fetchall):
    """
    convert the returned information from database into a dictionary
    :param table_name:
    :param nct_id:
    :param fetchall:
    :return:
    """
    command = "select * from " + table_name + " where nct_id='%s';" % (nct_id)
    col_names = get_table_colnames(table_name)
    basic_info = acl.query_postgresql(command, fetchall=fetchall)
    if fetchall:
        if basic_info != []:
            basic_info = vstack_list(basic_info)
        else:
            basic_info = [[] for _ in xrange(len(col_names))]
    else:
        if basic_info is None:
            basic_info = [[] for _ in xrange(len(col_names))]
    return(list2dict(col_names, basic_info))


def db2table_list_dict(table_name, nct_id, fetchall):
    command = "select * from " + table_name + " where nct_id='%s';" % (nct_id)
    col_names = get_table_colnames(table_name)
    basic_info = acl.query_postgresql(command, fetchall=fetchall)
    if not fetchall:
        return(list2dict(col_names, basic_info))
    list_dict = []
    for item in basic_info:
        tmp_dict = list2dict(col_names, item)
        list_dict.append(tmp_dict)
    return(list_dict)


def list_dict2dict_list(list_dict):
    """
    convert list of dicts into a dictionary whose values are list
    :param list_dict:
    :return:
    """
    keys = list_dict[0].keys()
    dict_list = {}
    for key in keys:
        dict_list[key] = []
    for dict in list_dict:
        for key in keys:
            dict_list[key].append(dict[key])
    return(dict_list)



# information specific functions
def extract_unique_design_outcomes(design_outcomes_dict):
    """
    extract the unique pair of design outcomes
    :param design_outcomes_dict:
    :return:
    """
    unique_design_outcomes = {"outcome_type":[], "measure": [], "time_frame": [], "description": []}
    _combined_pairs = []
    for idx in xrange(len(design_outcomes_dict["outcome_type"])):
        outcome_type = design_outcomes_dict["outcome_type"][idx]
        measurement = design_outcomes_dict["measure"][idx]
        time_frame = design_outcomes_dict["time_frame"][idx]
        description = design_outcomes_dict["description"][idx]
        tmp_combined_pair = outcome_type + measurement
        if tmp_combined_pair in _combined_pairs:
            continue
        else:
            unique_design_outcomes["outcome_type"].append(outcome_type)
            unique_design_outcomes["measure"].append(measurement)
            unique_design_outcomes["time_frame"].append(time_frame)
            unique_design_outcomes["description"].append(description)
            _combined_pairs.append(tmp_combined_pair)
    return(unique_design_outcomes)


def extract_study_design_tracking_information(designs_dict):
    study_design_model_type = "intervention_model"
    if designs_dict[study_design_model_type] == None:
        study_design_model_type = "observational_model"
    return(study_design_model_type)


def combine_intervention_other_names(interventions, intervention_other_names):
    """
    add intervention other names information to iterventions dictionary
    :param interventions:
    :param intervention_other_names:
    :return:
    """
    interventions["other_names"] = []
    if intervention_other_names["id"] == []:
        return (interventions)
    combined_dict = {}
    for idx, intervention_id in enumerate(intervention_other_names["intervention_id"]):
        if intervention_id not in combined_dict.keys():
            combined_dict[intervention_id] = [intervention_other_names["name"][idx]]
        else:
            combined_dict[intervention_id].append(intervention_other_names["name"][idx])
    for idx, intervention_id in enumerate(interventions["id"]):
        if intervention_id in combined_dict.keys():
            interventions["other_names"].append(combined_dict[intervention_id])
        else:
            interventions["other_names"].append([])
    return(interventions)


def _get_intervention(design_group_id, design_group_interventions, interventions_list_dict):
    intervention_id_list = []
    for item in design_group_interventions:
        tmp_design_group_id = item["design_group_id"]
        if tmp_design_group_id == design_group_id:
            intervention_id_list.append(item["intervention_id"])
    intervention_list = []
    for intervention in interventions_list_dict:
        tmp_intervention_id = intervention["id"]
        if tmp_intervention_id in intervention_id_list:
            intervention_list.append(intervention["intervention_type"] + ": " + intervention["name"])
    return("\n".join(intervention_list))
    # if len(intervention_list) == 1:
    #     return(intervention_list[0])
    # else:
    #     return(intervention_list)


def combine_design_group_interventions(design_groups, design_group_interventions, interventions_list_dict):
    design_groups_combined = copy.deepcopy(design_groups)
    for idx in xrange(len(design_groups)):
        design_group_id = design_groups[idx]["id"]
        design_groups_combined[idx]["interventions"] = _get_intervention(design_group_id, design_group_interventions,
                                                                         interventions_list_dict)
    return(design_groups_combined)


def generate_period_table(data_df, result_groups_dict):
    """
    generate a list of empty cells based on the row and column indexes;
    used for participant flow table.
    :param data_df:
    :param result_groups_dict:
    :return:
    """
    stages = np.unique(data_df["title"])[::-1]
    group_ids = np.unique(data_df["result_group_id"])
    group_names = [result_groups_dict[id] for id in group_ids]
    stage_group_id_pairs, empty_list = generate_pairs(stages, group_ids)
    for _, value in data_df.iterrows():
        key = value.result_group_id
        index = stage_group_id_pairs[str(value.title) + str(key)]
        empty_list[index[0]][index[1]] = value["count"]
        # print key, index, group
    data_list = [[" "] + group_names]
    for idx in xrange(len(empty_list)):
        tmp_row = [stages[idx]] + empty_list[idx]
        data_list.append(tmp_row)
    return(data_list)


def extract_milestone_groups(milestones, result_groups):
    """
    extract data to form fill in the participant flow results: how many participants started, completed, and withdrawed
    :param milestones:
    :param result_groups:
    :return:
    """
    result_groups = list_dict2dict_list(result_groups)
    result_groups_dict = list2dict(result_groups["id"], result_groups["title"])
    milestones_df = list_dict2dict_list(milestones)
    milestones_df = pd.DataFrame(milestones_df)
    period_list = np.unique(milestones_df["period"])
    data_list = []
    for period in period_list:
        tmp_df = milestones_df.loc[milestones_df["period"]==period]
        tmp_data_list = generate_period_table(tmp_df, result_groups_dict)
        data_list.append({"period": period, "data":tmp_data_list})
    return(data_list)


def result_group_id2name(df_with_result_group_id, result_groups):
    """
    add result group name to the first dataframe
    :param df_with_result_group_id:
    :param result_groups:
    :return:
    """
    dict = {}
    for item in result_groups:
        key = item["id"]
        value = item["title"]
        dict[key] = value
    result_group_titles = []
    for id in df_with_result_group_id["result_group_id"].values:
        tmp_title = dict[id]
        result_group_titles.append(tmp_title)
    df_with_result_group_id["result_group_title"] = result_group_titles
    return(df_with_result_group_id)


def extract_baseline_counts(baseline_counts, result_groups):
    bm_df = pd.DataFrame(baseline_counts)
    bm_df = result_group_id2name(bm_df, result_groups)
    categories = np.unique(bm_df["scope"])
    units = np.unique(bm_df["units"])
    category_data_list = []
    for cat in categories:
        for tmp_unit in units:
            logidx = np.logical_and(bm_df["scope"]==cat, bm_df["units"]==tmp_unit)
            if np.any(logidx):
                tmp_df = bm_df.loc[logidx][["scope", "count", "result_group_title"]]
                tmp_df = tmp_df.pivot(index="scope", columns="result_group_title", values="count")
                tmp_data = {"title": cat, "units": tmp_unit,
                            "data": df2list_of_lists(tmp_df)}
                category_data_list.append(tmp_data)
    return(category_data_list)


def combine_category_classification(df, kws):
    title_list = []
    for idx in xrange(len(df)):
        flag = True
        for keyword in kws:
            value = df[keyword].iloc[idx]
            if value != None:
                title_list.append(value)
                flag = False
        if flag:
            title_list.append("Unknown_" + str(idx))
    df["unique_category"] = title_list
    return(df)


def extract_baseline_measurements(baseline_measurements, result_groups):
    """
    structure baseline_measurement data for display
    :param baseline_measurements:
    :param result_groups:
    :return:
    """
    bm_df = pd.DataFrame(baseline_measurements)
    bm_df = result_group_id2name(bm_df, result_groups)
    bm_df = combine_category_classification(bm_df, ["category", "classification"])
    categories = np.unique(baseline_measurements["title"])
    units = np.unique(baseline_measurements["units"])
    category_data_list = []
    for cat in categories:
        for tmp_unit in units:
            logidx = np.logical_and(bm_df["title"]==cat, bm_df["units"]==tmp_unit)
            if np.any(logidx):
                tmp_df = bm_df.loc[logidx][["unique_category", "param_value", "result_group_title"]]
                tmp_df = tmp_df.pivot(index="unique_category", columns="result_group_title", values="param_value")
                tmp_data = {"title": cat, "units": tmp_unit,
                            "data": df2list_of_lists(tmp_df)}
                category_data_list.append(tmp_data)
    return(category_data_list)



