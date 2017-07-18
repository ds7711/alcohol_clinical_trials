# import required modules
import datetime
import parameters
import itertools
import copy
import xml.etree.cElementTree as ET
import urllib2
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# 1st: input search url and create download url to get the NCT_ID list
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


def create_individual_study_xml_url(nct_id, individual_study_xml_url=parameters.individual_study_xml_url):
    return(individual_study_xml_url[0] + nct_id + individual_study_xml_url[1])



# Create and delete database, add new relational table in the database
### note: one could also write a function that takes a list as input and generate the corresponding create table string\n
### as output. This will solve the problem of small typos and other errors
def create_tables(acl_db_parameters, commands):
    """ create tables in the PostgreSQL database"""
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


def query_postgresql(command_string, db_conn_parameters=parameters.acl_db_params):
    conn = None
    conn = psycopg2.connect(db_conn_parameters)
    cur = conn.cursor()
    cur.execute(command_string)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return(records)



### helper function
def str2bool(my_string):
    if my_string == "Yes":
        return(True)
    else:
        return(False)


def str2num(my_string):
    """convert a string to an integer"""
    return(int(my_string))


def str2monthyear(my_string):
    """convert month year string to python date object"""
    month2number = {'': 0,
                    'Apr': 4,
                    'Aug': 8,
                    'Dec': 12,
                    'Feb': 2,
                    'Jan': 1,
                    'Jul': 7,
                    'Jun': 6,
                    'Mar': 3,
                    'May': 5,
                    'Nov': 11,
                    'Oct': 10,
                    'Sep': 9,
                    'April': 4,
                    'August': 8,
                    'December': 12,
                    'February': 2,
                    'January': 1,
                    'July': 7,
                    'June': 6,
                    'March': 3,
                    'November': 11,
                    'October': 10,
                    'September': 9
                    }
    try:
        month, year = str.split(my_string)
        day = 1
    except:
        month, day, year = str.split(my_string)
        day = int(day[:-1])
    month = month2number[month]
    year = int(year)
    return(datetime.date(year, month, day))


type_conversion_funcs = {"%bool": str2bool,"%d": str2num, "%my": str2monthyear}


def simple_query(study_xml, query_list):
    col_name = query_list[0]
    col_type = query_list[-1]
    query_kw = query_list[1]
    query = "./" + query_kw
    query_result = study_xml.find(query)
    if query_result is None:
        return(None)
    else:
        return([col_name, col_type, query_result.text])


def simple_query_list(study_xml, query_lists):
    col_names = ""
    col_types = ""
    basic_col_type = "%s"
    data = []
    for query_list in query_lists:
        query_result = simple_query(study_xml, query_list)
        if query_result is None:
            continue
        else:
            col_name, col_type, tmp_data = query_result
            col_names = col_names + col_name + ", "
            col_types = col_types + basic_col_type + ", "
            if col_type != basic_col_type:
                tmp_data = type_conversion_funcs[col_type](tmp_data)
            data.append(tmp_data)
    return(col_names, col_types, data)


def example_write_to_db(study_list, acl_db_parameters):
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


def study_xml2db(study_xml, xml2db_queries=parameters.xml2db_queries, acl_db_parameters=parameters.acl_db_params):
    pass
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
                tmp_data = study_xml.find("./" + col[1])
                if tmp_data is not None:
                    tmp_data = tmp_data.text
            else:
                list_idx.append(idx)
                tmp_data = study_xml.findall("./" + col[1])
                if tmp_data is not None:
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


def batch_xml2db(xml_string, acl_db_parameters=parameters.acl_db_params):
    root = ET.fromstring(xml_string)
    debug_idx = 0
    for child in root:
        if debug_idx > 3:
            break
        if child.tag != "study":
            continue
        nct_id = child.find("./nct_id").text # get the nct_id of the study
        # create the url to fetch the xml string for each study
        individual_study_xml_url = create_individual_study_xml_url(nct_id, parameters.individual_study_xml_url)
        # fetch the xml file
        tmp_response = urllib2.urlopen(individual_study_xml_url)
        tmp_xml_string = tmp_response.read()
        tmp_root = ET.fromstring(tmp_xml_string)
        individual_xml2db(tmp_root, acl_db_parameters)
        debug_idx += 1


def studies2db(study_xml):
    table_name = "studies"
    list_flag = False
    xmldb_queries = [["nct_id", "id_info/nct_id", False, "%s"],
                     ["official_title", "official_title", False, "%s"],
                     ["start_month_year", "start_date", False, "%s"],
                     ["start_date", "start_date", False, "%my"],
                     ["completion_month_year", "completion_date", False, "%s"],
                     ["completion_date", "completion_date", False, "%my"],
                     ["primary_completion_month_year", "primary_completion_date", False, "%s"],
                     ["primary_completion_date", "primary_completion_date", False, "%my"],
                     ["verification_month_year", "verification_date", False, "%s"],
                     ["verification_date", "verification_date", False, "%my"],
                     ["study_type", "study_type", False, "%s"],
                     ["acronym", "acronym", False, "%s"],  # unknown query kw
                     ["baseline_population", "baseline_population", False, "%s"],
                     ["overall_status", "overall_status", False, "%s"],
                     ["last_known_status", "last_known_status", False, "%s"],  # unknown query kw
                     ["phase", "phase", False, "%s"],
                     ["enrollment", "enrollment", False, "%d"],
                     ["enrollment_type", "enrollment", False, "%s"],
                     ["source", "source", False, "%s"],
                     ["number_of_arms", "number_of_arms", False, "%d"],
                     ["number_of_groups", "number_of_groups", False, "%d"],  # unknown query kw
                     ["limitations_and_caveats", "unknown", False, "%s"],  # unknown query kw
                     ["last_changed_date", "lastchanged_date", False, "%my"],
                     ["brief_title", "brief_title", False, "%s"],
                     ["why_stopped", "why_stopped", False, "%s"],
                     ["has_expanded_access_type", "has_expanded_access", False, "%s"],
                     ["has_expanded_access", "has_expanded_access", False, "%bool"]
                    ]
    col_names, col_types, data = simple_query_list(study_xml, xmldb_queries)
    query = "INSERT INTO " + table_name + " (" + col_names[:-2] + ") " + " VALUES " + \
            "(" + col_types[:-2] + ");"
    return(query, data, list_flag)


def eligibilities2db(study_xml):
    table_name = "eligibilities"
    list_flag = False
    xmldb_queries = [["nct_id", "id_info/nct_id", False, "%s"],
                     ["gender", "eligibility/gender", False, "%s"],
                     ["minimum_age_type", "eligibility/minimum_age", "%s"],
                     # ["minimum_age", "minimum_age", "%age"],
                     ["maximum_age_type", "eligibility/maximum_age", "%s"],
                     # ["maximum_age", "maximum_age", "%age"],
                     ["healthy_volunteers", "eligibility/healthy_volunteers", False, "%s"],
                     ["age_groups", "eligibility/age_groups", False, "%s"],  #unknown query kw
                     ["criteria", "eligibility/criteria/textblock", False, "%s"]
                    ]
    col_names, col_types, data = simple_query_list(study_xml, xmldb_queries)
    query = "INSERT INTO " + table_name + " (" + col_names[:-2] + ") " + " VALUES " + \
            "(" + col_types[:-2] + ");"
    return(query, data, list_flag)


def conditions2db(study_xml):
    table_name = "conditions"
    list_flag = True
    col_names = "nct_id, name, "
    col_types = "%s, %s, "
    nct_id = study_xml.find("./id_info/nct_id").text
    condition_list = study_xml.findall("./condition")
    conditions = [item.text for item in condition_list]
    query = "INSERT INTO " + table_name + " (" + col_names[:-2] + ") " + " VALUES " + \
            "(" + col_types[:-2] + ");"
    data = augment_data([nct_id, conditions], [1])
    return(query, data, list_flag)


def links2db(study_xml):
    table_name = "links"
    list_flag = False
    xmldb_queries = [["nct_id", "id_info/nct_id", False, "%s"],
                     ["url", "required_header/url", False, "%s"],
                     ["description", "required_header/download_date", False, "%s"]  # unknown query kw and content
                    ]
    col_names, col_types, data = simple_query_list(study_xml, xmldb_queries)
    query = "INSERT INTO " + table_name + " (" + col_names[:-2] + ") " + " VALUES " + \
            "(" + col_types[:-2] + ");"
    return(query, data, list_flag)


table_funcs = [studies2db, eligibilities2db, conditions2db, links2db]


def individual_xml2db(study_xml, acl_db_parameters=parameters.acl_db_params):
    conn = None
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    # query, data = conditions2db(study_xml)
    # if type(data) is list:
    #     for tmp_data in data:
    #         cur.execute(query, tmp_data)
    # else:
    #     cur.execute(query, data)
    for tmp_func in table_funcs:
        query, data, list_flag = tmp_func(study_xml)
        if list_flag:
            for tmp_data in data:
                cur.execute(query, tmp_data)
        else:
            cur.execute(query, data)
    conn.commit()
    conn.close()
    return(None)








def augment_data(my_list, list_idx):
    list_of_lists = [my_list[idx] for idx in list_idx]
    combinations = itertools.product(*list_of_lists)
    new_data = []
    for item in combinations:
        for iii, idx in enumerate(list_idx):
            entry = my_list
            entry[idx] = item[iii]
        new_data.append(copy.deepcopy(entry))
        # print entry
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


# The following functions extract data from xml and write to corresponding table
# def extract_xml_data(study_xml):
#     tmp_study = AlcoholStudy()
#     tmp_study.nct_id = study_xml.find("./id_info").find("./nct_id").text
#     tmp_study.url = study_xml.find("./required_header").find("./url").text
#     tmp_study.official_title = study_xml.find("./official_title").text
#
#


class AlcoholStudy(object):
    def __init__(self):
        self.nct_id = None
        self.official_title = None
        self.gender = None
        self.url = None
        self.conditions = []


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