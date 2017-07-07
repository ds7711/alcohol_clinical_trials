# import required modules
import parameters
import itertools
import copy
import xml.etree.cElementTree as ET
import urllib2
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# 1st: create download url and download url from the website
def get_xml_string(search_url):
    """
    get the search results (.xml) as a string
    :param search_url: url used for search
    :return:
    """
    index = search_url.find(parameters.search_url_separating_kw)
    kw_length = len(parameters.search_url_separating_kw)
    cut_index = index + kw_length
    base_url = search_url[:cut_index]
    search_specification = search_url[cut_index:]
    search_string = base_url + parameters.download_kw + search_specification + parameters.download_specification
    response = urllib2.urlopen(search_string)
    xml_string = response.read()
    return(xml_string)


def download_xml_file(search_url, xml_filename=parameters.xml_file_name):
    """
    write the string as a .xml file
    :param search_url:
    :return:
    """
    xml_string = get_xml_string(search_url)
    with open(xml_filename, "wb") as thefile:
        thefile.write(xml_string)
    return(None)


class AlcoholStudy(object):

    def __init__(self):
        self.nct_id = None
        self.official_title = None
        self.gender = None
        self.url = None
        self.conditions = []



### note: one could also write a function that takes a list as input and generate the corresponding create table string\n
### as output. This will solve the problem of small typos and other errors
def create_tables(acl_db_parameters):
    """ create tables in the PostgreSQL database"""
    commands = parameters.commands
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(acl_db_parameters)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_postgresql_db(acl_db_name, admin_params=parameters.postgresql_params):
    """
    create new database
    :param acl_db_name:
    :param admin_params:
    :return:
    """
    conn = None
    conn = psycopg2.connect(admin_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE ' + acl_db_name)
    cur.close()
    conn.close()


def delete_postgresql_db(acl_db_name, admin_params=parameters.postgresql_params):
    """
    delete previous database
    :param acl_db_name:
    :param admin_params:
    :return:
    """
    conn = None
    conn = psycopg2.connect(admin_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('DROP DATABASE ' + acl_db_name)
    cur.close()
    conn.close()


def write_to_db(study_list, acl_db_parameters):
    """
    write records in study_list into acl_db_parameters (filename specified by acl_db_parameters)
    :param study_list:
    :param acl_db_parameters:
    :return:
    """
    conn = None
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    for study in study_list:
        query = "INSERT INTO studies (nct_id, official_title) VALUES (%s, %s);"
        data = (study.nct_id, study.official_title)
        cur.execute(query, data)
    conn.commit()
    conn.close()
    return(None)


def query_postgresql(command_string, db_conn_parameters=parameters.acl_db_params):
    conn = None
    conn = psycopg2.connect(db_conn_parameters)
    cur = conn.cursor()
    cur.execute(command_string)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return(records)


def study_xml2db(study_xml, xml2db_queries=parameters.xml2db_queries, acl_db_parameters=parameters.acl_db_params):
    conn = None
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    for table_dict in xml2db_queries:
        table_name = table_dict.keys()[0]
        table_cols = table_dict.values()[0]
        col_names = ""
        col_insert_params = ""
        data = []
        list_idx = [] # indexes of the queries that return a list
        for idx, col in enumerate(table_cols):
            col_names = col_names + col[0] + ", "
            col_insert_params = col_insert_params + col[-1] + ", "
            if not col[2]: # if the queried result from .xml is not a list, obtain its value directly
                tmp_data = study_xml.find("./" + col[1]).text
            else:
                list_idx.append(idx)
                tmp_data = study_xml.find("./" + col[1])
                tmp_data = [item.text for item in tmp_data]
            data.append(tmp_data)
        query = "INSERT INTO " + table_name + " (" + col_names[:-2] + ") " + " VALUES " + \
                "(" + col_insert_params[:-2] + ");"
        if len(list_idx) == 0:
            cur.execute(query, data)
        else:
            augmented_data = augment_data(data, list_idx)
            for data in augmented_data:
                cur.execute(query, data)

    conn.commit()
    conn.close()
    return(None)

def xml_file2db(xml_filename):
    tree = ET.parse(xml_filename)
    root = tree.getroot()
    study_list = []
    for child in root:
        study = AlcoholStudy()
        if child.tag != "study":
            continue
        study_xml2db(child)

test = True
if test:
    def extract_xml_data(xml_filename):
        tree = ET.parse(xml_filename)
        root = tree.getroot()
        study_list = []
        for child in root:
            study = AlcoholStudy()
            if child.tag != "study":
                continue
            study.nct_id = child.find("./nct_id").text
            study.official_title = child.find("./title").text
            study.url = child.find("./url").text
            study.gender = child.find("./gender").text
            condition_list = child.find("./conditions")
            for item in condition_list:
                study.conditions.append(item.text)
            study_list.append(study)
        return (study_list)
else:
    def extract_xml_data(xml_filename):
        tree = ET.parse(xml_filename)
        root = tree.getroot()
        study_list = []
        for child in root:
            study = AlcoholStudy()
            if child.tag != "study":
                continue
            study.nct_id = child.find("./nct_id").text
            study.official_title = child.find("./title").text
            study.url = child.find("./url").text
            study.gender = child.find("./gender").text
            condition_list = child.find("./conditions")
            for item in condition_list:
                study.conditions.append(item.text)
            study_list.append(study)
        return (study_list)

def augment_data(my_list, list_idx):
    list_of_lists = [my_list[idx] for idx in list_idx]
    combinations = itertools.product(*list_of_lists)
    new_data = []
    for item in combinations:
        for iii, idx in enumerate(list_idx):
            entry = my_list
            entry[idx] = item[iii]
        new_data.append(copy.deepcopy(entry))
        print entry
    return (new_data)


### Reference Backup only
# xml2db_schema = [
#     {"studies": [["nct_id", "CHARACTER(11)", "NOT NULL PRIMARY KEY", "nct_id", False, "%s"],
#                  ["official_title", "TEXT", "NOT NULL", "title", False, "%s"],
#                  ["enrollment_type", "VARCHAR(255)", "", "enrollment", False, "%s"],
#                  ["start_month_year", "VARCHAR(255)", "", "start_date", False, "%s"],
#                  ["completion_month_year", "VARCHAR(255)", "", "completion_date", False, "%s"]
#                  ]},
#     {"conditions": [["nct_id", "CHARACTER(11)", "NOT NULL", "nct_id", False, "%s"],
#                     ["id", "SERIAL", "NOT NULL", "NO_KW", False, ""]
#                    ]}
# ]
#
# def create_table_commands(table_dict):
#     table_name = table_dict.keys()[0]
#     table_cols = table_dict.values()[0]
#     space_separator = " "
#     start_str = "CREATE TABLE " + table_name + space_separator + "("
#     end_str = ")"
#     main_command = ""
#     for col in table_cols:
#         main_command = main_command + col[0] + space_separator + col[1] + space_separator + col[2] + ","
#     command = start_str + main_command[:-1] + end_str
#     return(command)