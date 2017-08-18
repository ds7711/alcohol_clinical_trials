import psycopg2
import parameters
import alcohol_clinicaltrials_lib as acl


def extract_unique_design_outcomes(design_outcomes_dict):
    """
    extract the unique pair of design outcomes
    :param design_outcomes_dict:
    :return:
    """
    unique_design_outcomes = {"outcome_type":[], "measure": []}
    _combined_pairs = []
    for idx in xrange(len(design_outcomes_dict["outcome_type"])):
        outcome_type = design_outcomes_dict["outcome_type"][idx]
        measurement = design_outcomes_dict["measure"][idx]
        tmp_combined_pair = outcome_type + measurement
        if tmp_combined_pair in _combined_pairs:
            continue
        else:
            unique_design_outcomes["outcome_type"].append(outcome_type)
            unique_design_outcomes["measure"].append(measurement)
            _combined_pairs.append(tmp_combined_pair)
    return(unique_design_outcomes)


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


def db2table_dict(table_name, nct_id, fetchall):
    """
    convert the returned information from database into a dictionary
    :param table_name:
    :param nct_id:
    :param fetchall:
    :return:
    """
    command = "select * from " + table_name + " where nct_id='%s';" % (nct_id)
    if fetchall:
        basic_info = acl.query_postgresql(command, fetchall=True)
        basic_info = vstack_list(basic_info)
    else:
        basic_info = acl.query_postgresql(command, fetchall=False)
    return(list2dict(get_table_colnames(table_name), basic_info))


### no use in html
def get_dict_data(my_dict, key):
    if key in my_dict.keys():
        return(my_dict[key])
    else:
        return(None)