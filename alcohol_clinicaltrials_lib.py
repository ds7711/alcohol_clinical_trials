# note
# unknown query keyword label: unknown_kw


# import required modules
import datetime
import zipfile
import parameters
import itertools
import copy
import xml.etree.cElementTree as ET
import urllib2
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# 1st: input search url and create download url to get the NCT_ID list
def separate_search_url(search_url, separating_kw=parameters.search_url_separating_kw):
    index = search_url.find(separating_kw)
    kw_length = len(separating_kw)
    cut_index = index + kw_length
    search_affix = search_url[:cut_index]
    search_specification = search_url[cut_index:]
    return(search_affix, search_specification)


def download_all_studies(search_url, zip_filename=parameters.zip_filename):
    zip_download_affix = "https://clinicaltrials.gov/ct2/download_studies"
    _, search_specification = separate_search_url(search_url)
    download_url = zip_download_affix + search_specification
    response = urllib2.urlopen(download_url)
    xml_string = response.read()
    with open(zip_filename, "wb") as thefile:
        thefile.write(xml_string)
    return(zip_filename)



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


def aact_query(command_string):
    conn = None
    db_conn_parameters = "dbname=aact user=postgres host=localhost password=7711"
    conn = psycopg2.connect(db_conn_parameters)
    cur = conn.cursor()
    cur.execute(command_string)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return(records)


### helper function

def xml2db_log(nct_id, error_message, log_name=parameters.log_filename):
    with open(log_name, "a") as thefile:
        log_string = nct_id + ": " + error_message +"\n"
        thefile.write(log_string)


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
    return(new_data)


def generate_query(table_name, col_name_list, col_type_list=None):
    """
    generate the query used to add data to database
    :param table_name: table name in the relational database
    :param col_name_list:
    :param col_type_list: if col_type_list is omitted, infer it
    :return:
    """
    join_kw = ", "
    if col_type_list is None:
        col_type_list = ["%s"] * len(col_name_list)
    query = "INSERT INTO " + table_name + " (" + join_kw.join(col_name_list) + ") " + " VALUES " + \
            "(" + join_kw.join(col_type_list) + ");"
    return(query)


def str2bool(my_string):
    if my_string == "Yes":
        return(True)
    else:
        return(False)


def str2int(my_string):
    """convert a string to an integer"""
    try:
        return(int(my_string))
    except:
        return(None)


def str2float(my_string):
    try:
        return(float(my_string))
    except:
        return(None)


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


def str2p_value(my_string):
    """
    extract p_value from expression (e.g., <0.01)
    :param my_string:
    :return:
    """
    def is_number(string):
        """
        test whether the single character contained in the string can be converted into an integer
        :param string:
        :return:
        """
        try:
            int(string)
            return (True)
        except:
            return (False)
    idx = 0
    while (not is_number(my_string[idx])) and (my_string[idx]!="."):
        idx += 1
    p_value = my_string[idx:]
    return(float(p_value))


def str2p_value_modifier(my_string):
    """
    extract p_value modifier (minus sign) from expression (e.g., <0.01)
    :param my_string:
    :return:
    """
    def is_number(string):
        """
        test whether the single character contained in the string can be converted into an integer
        :param string:
        :return:
        """
        try:
            int(string)
            return (True)
        except:
            return (False)
    idx = 0
    while (not is_number(my_string[idx])) and (my_string[idx]!="."):
        idx += 1
    p_value_modifier = my_string[:idx]
    return(p_value_modifier)


type_conversion_funcs = {"%bool": str2bool,"%d": str2int, "%my": str2monthyear,
                         "%p_value": str2p_value, "%p_value_modifier": str2p_value_modifier,
                         "%f": str2float}

def xmldict_query(xml_dict, key):
    dictionary = xml_dict.attrib
    if key in dictionary.keys():
        return(dictionary[key])
    else:
        return(None)

def xml_attrib_extract(my_xml, xml_dict_query_list):
    """
    extract attribute information from an simple XML structure
    :param my_xml:
    :param xml_dict_query_list:
        a list of lists: each list contains three strings,
            the 1st one is the corresponding column name in the database table;
            the 2nd one is the corresponding query keyword used for the xml attribute;
            the 3rd one is reserved for future purpose
            the 4th one is for possible type conversion
    :return:
    """
    values = []
    col_names = []
    for item in xml_dict_query_list:
        tmp_col_name = item[0]
        col_names.append(tmp_col_name)
        query_kw = item[1]
        tmp_type = item[3]
        tmp_value = xmldict_query(my_xml, query_kw)
        if tmp_type != "%s":
            tmp_value = type_conversion_funcs[tmp_type](tmp_value)
        values.append(tmp_value)
    return(col_names, values)


def xml_find(study_xml, keyword, return_string):
    """
    handle exception to prevent error
    :param study_xml:
    :param keyword:
    :return:
    """
    result = study_xml.find("./" + keyword)
    if result is None:
        return(None)
    else:
        if return_string:
            return(result.text)
        else:
            return(result)


def xml_findall(study_xml, keyword, return_string=True):
    keyword = "./" + keyword
    results = study_xml.findall(keyword)
    if results:  #short hand for results == []
        if return_string:
            return([item.text for item in results])
        else:
            return(results)
    else:
        return([])


def all_queries(study_xml, query_list):
    """
    single query, but may contain multiple simple returns. e.g., condition
    :param study_xml:
    :param query_list:
    :return:
    """
    col_name = query_list[0]
    col_type = query_list[-1]
    query_kw = query_list[1]
    query_kw = "./" + query_kw
    query_results = study_xml.findall(query_kw)
    query_results = [item.text for item in query_results]
    if query_results is not None:
        return([col_name, col_type, query_results])
    else:
        return(None)


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
    col_names = []
    data = []
    basic_col_type = "%s"
    for query_list in query_lists:
        query_result = simple_query(study_xml, query_list)
        if query_result is None:
            col_names.append(query_list[0])
            data.append(None)
        else:
            col_name, col_type, tmp_data = query_result
            col_names.append(col_name)
            if col_type != basic_col_type:
                tmp_data = type_conversion_funcs[col_type](tmp_data)
            data.append(tmp_data)
    return(col_names, data)


def hierarchical_query(study_xml, main_kw, sub_query_list, multiple_returns=True):
    data = []
    tmp_col_names = []
    main_kw = "./" + main_kw
    if multiple_returns:
        complex_object_list = study_xml.findall(main_kw)
        if complex_object_list:
            for xml_item in complex_object_list:
                tmp_col_names, tmp_data = simple_query_list(xml_item, sub_query_list)
                data.append(tmp_data)
        else:
            return([], [])
    else:
        complex_object = study_xml.find(main_kw)
        if complex_object is not None:
            tmp_col_names, data = simple_query_list(complex_object, sub_query_list)
            data = [data]
        else:
            return([], [])
    return(tmp_col_names, data)



def batch_xml2db(zip_filename, acl_db_parameters=parameters.acl_db_params):
    studies_zip = zipfile.ZipFile(zip_filename, "r")
    for idx, xml_filename in enumerate(studies_zip.namelist()):
        with studies_zip.open(xml_filename) as xml_file:
            xml_string = xml_file.read()
        if idx > 100:
            break
        study_xml = ET.fromstring(xml_string)
        print("%dth study: %s" % (idx+1, xml_filename[:-4]))
        print("\n")
        individual_xml2db(study_xml, acl_db_parameters)


def studies2db(study_xml, cur):
    """
    extract data about studies and write into the database
    :param study_xml: study_xml object used to extract data
    :param cur: cursor object used for writing
    :return: the cursor object
    """
    table_name = "studies"  # name of the table
    # xmldb_queries structure:
        # each row includes information for one column in the table
        # 1st: name of the column,
        # 2nd: keyword used to extract data from xml object
        # 3rd: obsolete for now, may be useful in the future
        # 4th: type of the data, default %s, if other, data will be converted accordingly.
            # e.g.,  %d indicate the extracted data will be first converted into a number and then write into the database
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
    col_names, data = simple_query_list(study_xml, xmldb_queries)
    query = generate_query(table_name, col_names)  # query string used by cursor object (psycopg2) to write to the database
    cur.execute(query, data)
    return(cur)


def eligibilities2db(study_xml, cur):
    """
    extract data and write to eligibilities table, detail see studies2db
    :param study_xml:
    :param cur:
    :return:
    """
    table_name = "eligibilities"
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
    col_names, data = simple_query_list(study_xml, xmldb_queries)
    query = generate_query(table_name, col_names)
    cur.execute(query, data)
    return(cur)


def conditions2db(study_xml, cur):
    table_name = "conditions"
    col_names = ["nct_id", "name"]
    nct_id = study_xml.find("./id_info/nct_id").text
    condition_list = study_xml.findall("./condition")
    conditions = [item.text for item in condition_list]
    query = generate_query(table_name, col_names)
    data = augment_data([nct_id, conditions], [1])
    for tmp_data in data:
        cur.execute(query, tmp_data)
    return(cur)


def keywords2db(study_xml, cur):
    table_name = "keywords"
    col_names = ["nct_id", "name"]
    nct_id = study_xml.find("./id_info/nct_id").text
    query = generate_query(table_name, col_names)
    keyword_list = xml_findall(study_xml, "keyword")
    if keyword_list != []:
        for keyword in keyword_list:
            data = [nct_id, keyword]
            cur.execute(query, data)
    return(cur)


def brief_summaries2db(study_xml, cur):
    table_name = "brief_summaries"
    query_entry = ["brief_summaries", "brief_summary/textblock", False, "%s"]
    nct_id = study_xml.find("./id_info/nct_id").text
    col_names = ["nct_id", "description"]
    _, _, brief_summaries = all_queries(study_xml, query_entry)
    query = generate_query(table_name, col_names)
    data = augment_data([nct_id, brief_summaries], [1])
    for tmp_data in data:
        cur.execute(query, tmp_data)
    return(cur)


class Intervention2DB_Obj(object):
    """
    write interventions information into the database, use object to keep track of the id
    """
    def __init__(self):
        self.intervention_detailed_id = 1  # primary key for table interventions, foreign key for table intervention_other_name
        self.intervention_id = 1
        self.nct_id = None
        self.design_group_id = 1

    def intervention_other_names(self, intervention_xml, cur):
        table_name = "intervention_other_names"
        col_names = ["nct_id", "intervention_id", "name"]
        col_types = ["%s"] * len(col_names)
        query = generate_query(table_name, col_names, col_types)
        other_name_list = intervention_xml.findall("./other_name")
        if other_name_list == []:
            return(None)
        else:
            other_name_list = [item.text for item in other_name_list]
            data = augment_data([self.nct_id, self.intervention_id, other_name_list], [-1])
            for tmp_data in data:
                cur.execute(query, tmp_data)
        return(cur)

    def design_group_func(self, study_xml, cur):
        table_name = "design_groups"
        col_names = ["nct_id", "id", "group_type", "title", "description"]
        query = generate_query(table_name, col_names)
        nct_id = study_xml.find("./id_info/nct_id").text

        main_query_kw = "arm_group"
        sub_query_list = [["group_type", "arm_group_type", False, "%s"],
                          ["title", "arm_group_label", False, "%s"],
                          ["description", "description", False, "%s"]]
        _, data = hierarchical_query(study_xml, main_query_kw, sub_query_list, multiple_returns=True)

        design_group_data = []
        for tmp_data in data:
            tmp_all_data = [nct_id, self.design_group_id] + tmp_data
            try:
                cur.execute(query, tmp_all_data)
            except:
                print(query, tmp_all_data)
                raise("Eror")
            design_group_data.append(tmp_all_data)
            self.design_group_id += 1

        return(design_group_data)

    def intervention_func_detailed(self, study_xml, cur):
        table_name = "interventions_detailed"
        col_names = ["nct_id", "id", "intervention_type", "name", "description"]
        query = generate_query(table_name, col_names)

        nct_id = study_xml.find("./id_info/nct_id").text
        self.nct_id = nct_id

        intervention_list = study_xml.findall("./intervention")

        for xml_item in intervention_list:
            intervention_type = xml_find(xml_item, "intervention_type", return_string=True)
            intervention_name = xml_find(xml_item, "intervention_name", return_string=True)
            intervention_description = xml_item.findall("./arm_group_label")  # unknown query kw
            if intervention_description == []:
                tmp_data = [nct_id, self.intervention_detailed_id, intervention_type, intervention_name, None]
                cur.execute(query, tmp_data)
                # self.intervention_other_names(xml_item, cur=cur)  # complete the other funcitons
                self.intervention_detailed_id += 1
            else:
                for item in intervention_description:
                    tmp_data = [nct_id, self.intervention_detailed_id, intervention_type, intervention_name,
                                item.text]
                    cur.execute(query, tmp_data)
                    # self.intervention_other_names(xml_item, cur=cur)  # complete the other funcitons
                    self.intervention_detailed_id += 1
        return(cur)

    def intervention_func(self, study_xml, cur):
        table_name = "interventions"
        col_names = ["nct_id", "id", "intervention_type", "name", "description"]
        query = generate_query(table_name, col_names)

        nct_id = study_xml.find("./id_info/nct_id").text
        self.nct_id = nct_id

        intervention_list = study_xml.findall("./intervention")

        intervention_design_group_dict = {}

        for xml_item in intervention_list:
            intervention_type = xml_find(xml_item, "intervention_type", return_string=True)
            intervention_name = xml_find(xml_item, "intervention_name", return_string=True)
            intervention_description = xml_find(xml_item, "description", return_string=True)
            intervention_details = xml_item.findall("./arm_group_label")
            tmp_data = [nct_id, self.intervention_id, intervention_type, intervention_name, intervention_description]
            cur.execute(query, tmp_data)
            self.intervention_other_names(xml_item, cur=cur)  # complete the other funcitons

            if intervention_details != []:
                for item in intervention_details:
                    intervention_design_group_dict[item.text] = self.intervention_id
            self.intervention_id += 1
        return(intervention_design_group_dict)

    def design_group_interventions_func(self, intervention_design_group_dict, design_group_data, cur):
        table_name = "design_group_interventions"
        col_names = ["nct_id", "design_group_id", "intervention_id"]
        query = generate_query(table_name, col_names)
        for item in design_group_data:
            design_group_id = item[1]
            intervention_group_key = item[3]
            try:
                intervention_id = intervention_design_group_dict[intervention_group_key]
            except:
                # print(self.nct_id)
                # print(intervention_design_group_dict)
                # print(design_group_data)
                intervention_id = None
            data = [self.nct_id, design_group_id, intervention_id]
            cur.execute(query, data)
        return(cur)

    def main_func(self, study_xml, cur):
        self.intervention_func_detailed(study_xml=study_xml, cur=cur)
        intervention_design_group_dict = self.intervention_func(study_xml=study_xml, cur=cur)
        design_group_data = self.design_group_func(study_xml=study_xml, cur=cur)
        self.design_group_interventions_func(intervention_design_group_dict, design_group_data, cur=cur)


interventions2db = Intervention2DB_Obj()


def links2db(study_xml, cur):
    table_name = "links"
    xmldb_queries = [["nct_id", "id_info/nct_id", False, "%s"],
                     ["url", "required_header/url", False, "%s"],
                     ["description", "required_header/download_date", False, "%s"]  # unknown query kw and content
                    ]
    col_names, data = simple_query_list(study_xml, xmldb_queries)
    query = generate_query(table_name, col_names)
    cur.execute(query, data)
    return(cur)
    pass


def study_references2db(study_xml, cur):
    table_name = "study_references"
    nct_id = study_xml.find("./id_info/nct_id").text
    main_kw = "reference"
    sub_query_list = [["citation", "citation", False, "%s"],
                      ["pmid", "PMID", False, "%s"],
                      ["reference_type", "unknown_kw???", False, "%s"]
                      ]
    col_names, data = hierarchical_query(study_xml, main_kw, sub_query_list, multiple_returns=True)
    col_names = ["nct_id"] + col_names
    query = generate_query(table_name, col_names)
    for tmp_data in data:
        tmp_data = [nct_id] + tmp_data
        cur.execute(query, tmp_data)


def browse_conditions2db(study_xml, cur):
    table_name = "browse_conditions"
    col_names = ["nct_id", "mesh_term"]
    query = generate_query(table_name, col_names)
    nct_id = study_xml.find("./id_info/nct_id").text
    browse_condition_xml = xml_find(study_xml, "condition_browse", return_string=False)
    if browse_condition_xml is not None:
        mesh_term_list = xml_findall(browse_condition_xml, "mesh_term")
        for mesh_term in mesh_term_list:
            data = [nct_id, mesh_term]
            cur.execute(query, data)


def browse_inerventions2db(study_xml, cur):
    table_name = "browse_interventions"
    col_names = ["nct_id", "mesh_term"]
    query = generate_query(table_name, col_names)
    nct_id = study_xml.find("./id_info/nct_id").text
    browse_condition_xml = xml_find(study_xml, "intervention_browse", return_string=False)
    if browse_condition_xml is not None:
        mesh_term_list = xml_findall(browse_condition_xml, "mesh_term")
        for mesh_term in mesh_term_list:
            data = [nct_id, mesh_term]
            cur.execute(query, data)


def detailed_descriptions2db(study_xml, cur):
    table_name = "detailed_descriptions"
    col_names = ["nct_id", "description"]
    query = generate_query(table_name, col_names)
    nct_id = study_xml.find("./id_info/nct_id").text
    detailed_description = xml_find(study_xml, "/detailed_description/textblock", return_string=True)
    if detailed_description is not None:
        data = [nct_id, detailed_description]
        cur.execute(query, data)


def participant_flows2db(study_xml, cur):
    table_name = "participant_flows"
    xmldb_queries = [["nct_id", "id_info/nct_id", False, "%s"],
                     ["recruitment_details", "clinical_results/participant_flow/recruitment_details", False, "%s"],
                     ["pre_assignment_details", "clinical_results/participant_flow/pre_assignment_details", False, "%s"],
                     ]
    col_names, data = simple_query_list(study_xml, xmldb_queries)
    query = generate_query(table_name, col_names)
    cur.execute(query, data)
    return(cur)


def result_contacts2db(study_xml, cur):
    table_name = "result_contacts"
    col_names = ["nct_id", "organization", "name", "phone", "email"]
    query = generate_query(table_name, col_names)
    point_of_contact_xml = xml_find(study_xml, "clinical_results/point_of_contact", return_string=False)
    nct_id = study_xml.find("./id_info/nct_id").text
    if point_of_contact_xml is not None:
        xmldb_queries = [["organization", "organization", False, "%s"],
                         ["name", "name_or_title", False, "%s"],
                         ["phone", "phone", False, "%s"],
                         ["email", "email", False, "%s"]]
        _, data = simple_query_list(point_of_contact_xml, xmldb_queries)
        data = [nct_id] + data
        cur.execute(query, data)
        return(cur)


def overall_officials2db(study_xml, cur):
    table_name = "overall_officials"
    nct_id = study_xml.find("./id_info/nct_id").text
    main_kw = "overall_official"
    sub_query_list = [["name", "last_name", False, "%s"],
                      ["role", "role", False, "%s"],
                      ["affiliation", "affiliation", False, "%s"]
                      ]
    col_names, data = hierarchical_query(study_xml, main_kw, sub_query_list, multiple_returns=True)
    col_names = ["nct_id"] + col_names
    query = generate_query(table_name, col_names)
    for tmp_data in data:
        tmp_data = [nct_id] + tmp_data
        cur.execute(query, tmp_data)
    return(cur)


def sponsors2db(study_xml, cur):
    table_name = "sponsors"
    nct_id = study_xml.find("./id_info/nct_id").text
    sponsors_xml = xml_find(study_xml, "sponsors", return_string=False)
    xmldb_queries = [["agency_class", "agency_class", False, "%s"],
                     ["name", "agency", False, "%s"]
                     ]
    col_names = ["nct_id", "lead_or_collaborator", "agency_class", "name"]
    query = generate_query(table_name, col_names)
    if sponsors_xml is not None:
        lead_sponsor_xml = xml_find(sponsors_xml, "lead_sponsor", return_string=False)
        if lead_sponsor_xml is not None:
            lead_or_collaborator = "lead"
            _, tmp_data = simple_query_list(lead_sponsor_xml, xmldb_queries)
            data = [nct_id, lead_or_collaborator] + tmp_data
            cur.execute(query, data)
        collaborator_sponsor_xml = xml_find(sponsors_xml, "collaborator", return_string=False)
        if collaborator_sponsor_xml is not None:
            lead_or_collaborator = "collaborator"
            _, tmp_data = simple_query_list(collaborator_sponsor_xml, xmldb_queries)
            # print(tmp_data)
            data = [nct_id, lead_or_collaborator] + tmp_data
            # print(data)
            cur.execute(query, data)
        return(cur)


def id_information2db(study_xml, cur):
    table_name = "id_information"
    col_names = ["nct_id", "id_type", "id_value"]
    id_info_xml = study_xml.find("./id_info")
    nct_id = id_info_xml.find("./nct_id").text
    query = generate_query(table_name, col_names)
    id_type_query_list = [["org_study_id", "org_study_id"],
                          ["secondary_id", "secondary_id"],
                          ["nct_alias", "nct_alias"]
                          ]
    for id_type_query in id_type_query_list:
        id_type = id_type_query[0]
        id_query = id_type_query[1]
        id_value = xml_find(id_info_xml, id_query, return_string=True)
        if id_value is not None:
            data = [nct_id, id_type, id_value]
            cur.execute(query, data)
    return (cur)


### functions that are partial done
def countries2db(study_xml, cur):
    table_name = "countries"
    col_names = ["nct_id", "name", "removed"]
    query = generate_query(table_name, col_names)
    nct_id = study_xml.find("./id_info/nct_id").text
    countries_xml = xml_find(study_xml, "location_countries", return_string=False)
    if countries_xml is not None:
        country_list = xml_findall(countries_xml, "country")
        removed = None  # unknown query kw !!
        for country in country_list:
            data = [nct_id, country, removed]
            cur.execute(query, data)
        return(cur)


def central_contacts2db(study_xml, cur):
    "missing example data"
    table_name = "central_contacts"
    nct_id = study_xml.find("./id_info/nct_id").text
    pass


def responsible_parties2db(study_xml, cur):
    table_name = "responsible_parties"
    nct_id = study_xml.find("./id_info/nct_id").text
    main_kw = "responsible_party"
    sub_query_list = [["responsible_party_type", "responsible_party_type", False, "%s"],
                      ["name", "name", False, "%s"],
                      ["title", "title", False, "%s"],
                      ["organization", "organization", False, "%s"],
                      ["affiliation", "affiliation", False, "%s"]
                      ]
    col_names, data = hierarchical_query(study_xml, main_kw, sub_query_list, multiple_returns=True)
    col_names = ["nct_id"] + col_names
    query = generate_query(table_name, col_names)
    for tmp_data in data:
        tmp_data = [nct_id] + tmp_data
        cur.execute(query, tmp_data)
    return(cur)


def designs2db(study_xml, cur):
    table_name = "designs"
    nct_id = study_xml.find("./id_info/nct_id").text
    study_design_info_xml = study_xml.find("./study_design_info")
    if study_design_info_xml is not None:
        xmldb_queries = [["allocation", "allocation", False, "%s"],
                         ["intervention_model", "intervention_model", False, "%s"],
                         ["primary_purpose", "primary_purpose", False, "%s"],
                         ["masking", "masking", False, "%s"],
                         ["time_perspective", "time_perspective", False, "%s"],
                         ["intervention_model_description", "intervention_model_description", False, "%s"],
                         ["masking_description", "masking_description", False, "%s"],
                         ["observational_model", "observational_model", False, "%s"]  # unknown query kw and content
                         ]
        col_names, data = simple_query_list(study_design_info_xml, xmldb_queries)
        col_names = ["nct_id"] + col_names
        query = generate_query(table_name, col_names)
        data = [nct_id] + data
        cur.execute(query, data)
        return(cur)

def result_agreements2db(study_xml, cur):
    table_name = "result_agreements"
    col_names = ["nct_id", "pi_employee", "agreement"]
    query = generate_query(table_name, col_names)
    certain_agreement_xml = xml_find(study_xml, "clinical_results/certain_agreements", return_string=False)
    nct_id = study_xml.find("./id_info/nct_id").text
    if certain_agreement_xml is not None:
        xmldb_queries = [["pi_employee", "pi_employee", False, "%s"],
                         ["agreement", "restrictive_agreement", False, "%s"]]
        _, data = simple_query_list(certain_agreement_xml, xmldb_queries)
        data = [nct_id] + data
        cur.execute(query, data)


### functions to finish
# to refer to AACT database



class Clinical_Results(object):

    def __init__(self):
        self.nct_id = None
        self.result_group_id = 1
        self.outcome_id = 1
        self.outcome_analysis_id = 1
        self.ctgov_group_code2result_group_id = {}
        self.ctgov_group_code2result_group_title = {}

    def _add2result_group_dict(self, query, data, cur):
        """
        update the result_group_id dictionary, if exception, write to log file
        :param ctgov_code:
        :return:
        """
        ctgov_code = data[-3]
        ctgov_code_title = data[-2]
        if ctgov_code not in self.ctgov_group_code2result_group_id.keys():
            self.ctgov_group_code2result_group_id[ctgov_code] = self.result_group_id
            self.ctgov_group_code2result_group_title[ctgov_code] = ctgov_code_title
            cur.execute(query, data)
            self.result_group_id += 1
            return(True)
        else:
            if self.ctgov_group_code2result_group_title[ctgov_code] != ctgov_code_title:
                error_message = "ctgov code is not unique in the .xml file. %s refer to both %s and %s." \
                                % (ctgov_code, self.ctgov_group_code2result_group_title[ctgov_code], ctgov_code_title)
                xml2db_log(self.nct_id, error_message)
                return(False)

    def result_outcome_main(self, study_xml, cur):
        # reset the dictionary for each study
        self.ctgov_group_code2result_group_id = {}
        self.ctgov_group_code2result_group_title = {}
        results_xml = study_xml.find("./clinical_results")
        if results_xml is None: # if no results are available, jump to the next part
            return(None)
        self.nct_id = study_xml.find("./id_info/nct_id").text
        self.results_group_func(results_xml, cur)
        self.outcomes_func(results_xml, cur)
        self.milestones_func(results_xml, cur)
        self.reported_events_func(results_xml, cur)
        self.baseline_counts_func(results_xml, cur)
        # print(outcome_data)

    def results_group_func(self, results_xml, cur):

        table_name = "result_groups"
        col_names = ["nct_id", "id", "result_type", "ctgov_group_code", "title", "description"]
        query = generate_query(table_name, col_names)

        def group_info_func(group_xml):
            xmldb_queries = [["title", "title", False, "%s"],
                             ["description", "description", False, "%s"],
                             ]
            ctgov_group_code = group_xml.attrib["group_id"]
            _, data = simple_query_list(group_xml, xmldb_queries)
            return(ctgov_group_code, data)

        def participant_results_group_id(results_xml, cur):
            result_type = "participant_flow"
            participant_results_xml = results_xml.find("./participant_flow/group_list")
            if participant_results_xml is None:
                return(None)
            else:
                results_group_list = participant_results_xml.findall("./group")
                if results_group_list != []:
                    for child in results_group_list:
                        ctgov_group_code, data = group_info_func(child)
                        data = [self.nct_id, self.result_group_id, result_type, ctgov_group_code] + data
                        self._add2result_group_dict(query, data, cur)
                return(None)

        def baseline_results_group_id(results_xml, cur):
            result_type = "baseline"
            baseline_results_xml = results_xml.find("./baseline")
            if baseline_results_xml is None:
                return(None)
            else:
                group_list_xml = baseline_results_xml.find("./group_list")
                if group_list_xml is None:
                    return(None)
                else:
                    group_xml_list = group_list_xml.findall("./group")
                    if group_xml_list != []:
                        for group_xml in group_xml_list:
                            ctgov_group_code, data = group_info_func(group_xml)
                            data = [self.nct_id, self.result_group_id, result_type, ctgov_group_code] + data
                            self._add2result_group_dict(query, data, cur)

                    return (None)

        def outcome_results_group_id(results_xml, cur):
            result_type = "outcome"
            outcome_results_xml = results_xml.find("./outcome_list")
            if outcome_results_xml is None:
                return(None)
            else:
                outcome_xml_list = outcome_results_xml.findall("./outcome")
                if outcome_xml_list != []:
                    for outcome_xml in outcome_xml_list:
                        group_list_xml = outcome_xml.find("./group_list")
                        if group_list_xml is not None:
                            group_xml_list = group_list_xml.findall("./group")
                            for group_xml in group_xml_list:
                                ctgov_group_code, data = group_info_func(group_xml)
                                data = [self.nct_id, self.result_group_id, result_type, ctgov_group_code] + data
                                self._add2result_group_dict(query, data, cur)
                return(None)

        def reported_events_results_group_id(results_xml, cur):
            result_type = "reported_events"
            reported_events_xml = results_xml.find("./reported_events")
            if reported_events_xml is None:
                return(None)
            else:
                reported_events_group_xml = reported_events_xml.find("./group_list")
                if reported_events_group_xml is not None:
                    group_xml_list = reported_events_group_xml.findall("./group")
                    if group_xml_list != []:
                        for group_xml in group_xml_list:
                            ctgov_group_code, data = group_info_func(group_xml)
                            data = [self.nct_id, self.result_group_id, result_type, ctgov_group_code] + data
                            self._add2result_group_dict(query, data, cur)
                return(cur)

        results_group_func_list = [participant_results_group_id, baseline_results_group_id,
                                   outcome_results_group_id, reported_events_results_group_id]
        for func in results_group_func_list:
            func(results_xml, cur)

    def outcomes_func(self, results_xml, cur):
        table_name = "outcomes"
        col_names_partial = ["nct_id", "id"]
        outcomes_data = []
        outcomes_xml = results_xml.find("./outcome_list")
        if outcomes_xml is []:
            return([])
        else:
            outcome_list = outcomes_xml.findall("./outcome")
            xmldb_queries = [["outcome_type", "type", False, "%s"],
                             ["title", "title", False, "%s"],
                             ["description", "description", False, "%s"],  # unknown query kw !!!
                             ["time_frame", "time_frame", False, "%s"],
                             ["population", "population", False, "%s"],
                             ["units", "measure/units", False, "%s"],
                             ["units_analyzed", "measure/units_analyzed", False, "%s"],
                             ["anticipated_posting_month_year", "posting_date", False, "%s"],  # unknown query kw !!!
                             ["dispersion_type", "measure/dispersion", False, "%s"],
                             ["param_type", "measure/param", False, "%s"]
                             ]
            if outcome_list != []:
                for child_outcome in outcome_list:
                    tmp_col_names, tmp_data = simple_query_list(child_outcome, xmldb_queries)
                    col_names = col_names_partial + tmp_col_names
                    query = generate_query(table_name, col_names)
                    data = [self.nct_id, self.outcome_id] + tmp_data
                    cur.execute(query, data)

                    ### other functions

                    # outcome_analyses  (measure sub_struct)
                    outcome_analyses_xml = xml_find(child_outcome, "analysis_list", return_string=False)
                    if outcome_analyses_xml is not None:
                        self.outcome_analyses_func(outcome_analyses_xml, cur)

                    # outcome_counts
                    analyzed_list_xml = xml_find(child_outcome, "measure/analyzed_list", return_string=False)
                    if analyzed_list_xml is not None:
                        self.outcome_counts_func(analyzed_list_xml, cur)

                    # outcome_measurements
                    self.outcome_measurements_func(child_outcome, cur)

                    ### other functions

                    outcomes_data.append(data)
                    self.outcome_id += 1
        return(outcomes_data)

    def outcome_counts_func(self, analyzed_list_xml, cur):
        """
        write data into table outcome_counts.
            requires the data from table result group and outcome
        :param analyzed_list_xml:
        :param cur:
        :return:
        """
        table_name = "outcome_counts"
        col_names = ["nct_id",  "outcome_id", "result_group_id", "units", "scope",
                     "ctgov_group_code", "count"]
        query = generate_query(table_name, col_names)
        analyzed_xml_list = analyzed_list_xml.findall("./analyzed")
        for analyzed_xml in analyzed_xml_list:
            units = xml_find(analyzed_xml, "units", return_string=True)
            scope = xml_find(analyzed_xml, "scope", return_string=True)
            count_xml_list = analyzed_xml.find("./count_list")
            if count_xml_list is not None:
                count_xml_list = count_xml_list.findall("./count")
                if count_xml_list != []:
                    for count_xml in count_xml_list:
                        count_dict = count_xml.attrib
                        ctgov_group_code, count_value = count_dict["group_id"], count_dict["value"]
                        count_value = int(count_value)
                        if ctgov_group_code in self.ctgov_group_code2result_group_id.keys():
                            results_group_id = self.ctgov_group_code2result_group_id[ctgov_group_code]
                        else:
                            results_group_id = None
                        data = [self.nct_id, self.outcome_id, results_group_id,
                                units, scope, ctgov_group_code, count_value]
                        cur.execute(query, data)

    def outcome_analyses_func(self, outcome_analyses_list_xml, cur):
        """
        to finish, need an xml file that contains these values
        :param outcome_analyses_xml:
        :param cur:
        :return:
        """
        table_name = "outcome_analyses"
        xmldb_queries = [["non_inferiority_type", "non_inferiority_type", False, "%s"],
                         ["non_inferiority_description", "non_inferiority_desc", False, "%s"],
                         ["param_type", "param_type", False, "%s"],
                         ["param_value", "param_value", False, "%f"],
                         ["dispersion_type", "dispersion_type", False, "%s"],
                         ["dispersion_value", "dispersion_value", False, "%f"],
                         ["p_value", "p_value", False, "%p_value"],
                         ["p_value_modifier", "p_value", False, "%p_value_modifier"],  # extra calculation may be needed
                         ["ci_n_sides", "ci_n_sides", False, "%s"],
                         ["ci_percent", "ci_percent", False, "%f"],
                         ["ci_lower_limit", "ci_lower_limit", False, "%f"],
                         ["ci_upper_limit", "ci_upper_limit", False, "%f"],
                         ["ci_upper_limit_na_comment", "ci_upper_limit_na_comment", False, "%s"],
                         ["p_value_description", "p_value_desc", False, "%s"],
                         ["method", "method", False, "%s"],
                         ["method_description", "method_desc", False, "%s"],
                         ["estimate_description", "estimate_desc", False, "%s"],
                         ["other_analysis_description", "other_analysis_desc", False, "%s"],
                         ["groups_description", "group_desc", False, "%s"]
                         ]
        for outcome_analysis_xml in outcome_analyses_list_xml.findall("./analysis"):
            col_names, data = simple_query_list(outcome_analysis_xml, xmldb_queries)
            col_names = ["id" , "nct_id", "outcome_id"] + col_names
            query = generate_query(table_name, col_names)
            data = [self.outcome_analysis_id , self.nct_id, self.outcome_id] + data
            cur.execute(query, data)

            ### other functions
            self.outcome_analysis_groups_func(outcome_analysis_xml, cur)
            ### other functions

            self.outcome_analysis_id += 1
        return(cur)

    def outcome_analysis_groups_func(self, outcome_analysis_xml, cur):
        table_name = "outcome_analysis_groups"
        col_names = ["nct_id", "result_group_id", "outcome_analysis_id", "ctgov_group_code"]
        query = generate_query(table_name, col_names)
        group_id_list_xml = xml_find(outcome_analysis_xml, "group_id_list", return_string=False)
        if group_id_list_xml is not None:
            group_id_list = xml_findall(group_id_list_xml, "group_id")
            for group_id in group_id_list:
                result_group_id = self.ctgov_group_code2result_group_id[group_id]
                data = [self.nct_id, result_group_id, self.outcome_analysis_id, group_id]
                cur.execute(query, data)
            return(cur)

    def outcome_measurements_func(self, outcome_analysis_xml, cur):
        table_name = "outcome_measurements"
        outcome_id = self.outcome_id
        xmldb_queries = [
            ["title", "title", False, "%s"],
            ["description", "description", False, "%s"],
            ["units", "units", False, "%s"],
            ["param_type", "param", False, "%s"],
            ["dispersion_type", "dispersion", False, "%s"]
        ]
        for measure_xml in xml_findall(outcome_analysis_xml, "measure", return_string=False):
            partial_col_names, partial_data = simple_query_list(measure_xml, xmldb_queries)
            col_names = ["nct_id", "outcome_id", "result_group_id"] + partial_col_names + \
                        ["classification", "ctgov_group_code", "dispersion_value",
                         "dispersion_value_num", "param_value", "param_value_num",
                         "dispersion_lower_limit", "dispersion_upper_limit"]
            query = generate_query(table_name, col_names)
            class_list_xml = xml_find(measure_xml, "class_list", return_string=False)
            if class_list_xml is not None:
                for class_xml in class_list_xml.findall("./class"):
                    classification = xml_find(class_xml, "title", return_string=True)
                    category_list_xml = xml_find(class_xml, "category_list", return_string=False)
                    if category_list_xml is not None:
                        for category_xml in category_list_xml.findall("./category"):
                            measurement_list_xml = xml_find(category_xml, "measurement_list", return_string=False)
                            if measurement_list_xml is not None:
                                for measurement_xml in measurement_list_xml.findall("./measurement"):
                                    ctgov_group_code = xmldict_query(measurement_xml, "group_id")
                                    result_group_code = self.ctgov_group_code2result_group_id[ctgov_group_code]
                                    dispersion_value = xmldict_query(measurement_xml, "spread")
                                    dispersion_value_num = str2float(dispersion_value)
                                    param_value = xmldict_query(measurement_xml, "value")
                                    param_value_num = str2float(param_value)
                                    dispersion_lower_limit = str2float(xmldict_query(measurement_xml, "lower_limit"))
                                    dispersion_upper_limit = str2float(xmldict_query(measurement_xml, "upper_limit"))
                                    data = [self.nct_id, outcome_id, result_group_code] + partial_data + \
                                        [classification, ctgov_group_code, dispersion_value,
                                         dispersion_value_num, param_value, param_value_num,
                                         dispersion_lower_limit, dispersion_upper_limit]
                                    cur.execute(query, data)
        return(cur)

    def reported_events_func(self, results_xml, cur):

        def events_query(overall_events_xml, event_type, time_frame, description, table_name, cur):
            xml_dict_query = [["ctgov_group_code", "group_id", False, "%s"],
                              ["subjects_affected", "subjects_affected", False, "%d"],
                              ["subjects_at_risk", "subjects_at_risk", False, "%d"],
                              ["event_count", "events", False, "%d"]
                              ]
            xmldb_queries = [["default_assessment", "default_assessment", False, "%s"],
                             ["default_vocab", "default_vocab", False, "%s"],
                             ["frequency_threshold", "frequency_threshold", False, "%f"]
                             ]
            tmp_col_names, tmp_data = simple_query_list(overall_events_xml, xmldb_queries)
            category_list_xml = xml_find(overall_events_xml, "category_list", return_string=False)
            for category_xml in category_list_xml.findall("./category"):
                organ_system = xml_find(category_xml, "title", return_string=True)
                event_list_xml = xml_find(category_xml, "event_list", return_string=False)
                for event_xml in event_list_xml.findall("./event"):
                    sub_title_xml = xml_find(event_xml, "sub_title", return_string=False)
                    adverse_event_term = sub_title_xml.text
                    vocab = xmldict_query(sub_title_xml, "vocab")
                    assessment = xml_find(event_xml, "assessment", return_string=True)
                    for counts_xml in event_xml.findall("./counts"):
                        counts_col_names, counts_data = xml_attrib_extract(counts_xml, xml_dict_query)
                        result_group_id = self.ctgov_group_code2result_group_id[counts_data[0]]
                        col_names = ["nct_id", "result_group_id", "event_type", "time_frame", "description"] + \
                                    tmp_col_names + ["organ_system", "adverse_event_term", "vocab", "assessment"] + \
                                     counts_col_names
                        query = generate_query(table_name, col_names)
                        data = [self.nct_id, result_group_id, event_type, time_frame, description] + tmp_data + \
                               [organ_system, adverse_event_term, vocab, assessment] + counts_data
                        cur.execute(query, data)

        table_name = "reported_events"
        reported_events_xml = xml_find(results_xml, "reported_events", return_string=False)
        if reported_events_xml is not None:
            time_frame = xml_find(reported_events_xml, "time_frame", return_string=True)
            description = xml_find(reported_events_xml, "desc", return_string=True)
            serious_events_xml = xml_find(reported_events_xml, "serious_events", return_string=False)
            if serious_events_xml is not None:
                event_type = "serious"
                events_query(serious_events_xml, event_type, time_frame, description, table_name, cur)

            other_events_xml = xml_find(reported_events_xml, "other_events", return_string=False)
            if other_events_xml is not None:
                event_type = "other"
                events_query(other_events_xml, event_type, time_frame, description, table_name, cur)

    def baseline_counts_func(self, results_xml, cur):
        table_name = "baseline_counts"
        xmldb_queries = [["units", "units", False, "%s"],
                         ["scope", "scope", False, "%s"]
                         ]
        xml_dict_queries = [["ctgov_group_code", "group_id", False, "%s"],
                            ["count", "value", False, "%d"]
                            ]

        baseline_analyzed_list_xml = xml_find(results_xml, "baseline/analyzed_list", return_string=False)
        if baseline_analyzed_list_xml is not None:
            for analyzed_xml in baseline_analyzed_list_xml.findall("./analyzed"):
                tmp_col_names, tmp_data = simple_query_list(analyzed_xml, xmldb_queries)
                count_list_xml = xml_find(analyzed_xml, "count_list", return_string=False)
                if count_list_xml is not None:
                    for count_xml in count_list_xml.findall("./count"):
                        count_col_names, count_data = xml_attrib_extract(count_xml, xml_dict_queries)
                        result_group_id = self.ctgov_group_code2result_group_id[count_data[0]]
                        col_names = ["nct_id", "result_group_id"] + tmp_col_names + count_col_names
                        query = generate_query(table_name, col_names)
                        data = [self.nct_id, result_group_id] + tmp_data + count_data
                        cur.execute(query, data)

    def baseline_measurements_func(self, results_xml, cur):
        pass

    def milestones_func(self, results_xml, cur):
        table_name = "milestones"
        col_names = ["nct_id", "result_group_id", "period", "title", "ctgov_group_code", "description", "count"]
        query = generate_query(table_name, col_names)
        xml_dict_query = [["group_id", "group_id", False, "%s"],
                          ["count", "count", False, "%d"],
                          ]
        period_list_xml = xml_find(results_xml, "participant_flow/period_list", return_string=False)
        if period_list_xml is not None:
            for period_xml in period_list_xml.findall("./period"):
                period = xml_find(period_xml, "title", return_string=True)

                self.drop_withdrawals_func(period_xml, cur, period)  # drop_withdraw functions

                milestone_list_xml = xml_find(period_xml, "milestone_list", return_string=False)
                for milestone_xml in milestone_list_xml.findall("./milestone"):
                    title = xml_find(milestone_xml, "title", return_string=True)
                    description = xml_find(milestone_xml, "unknown_kw!!!", return_string=True)  # unknown query kw
                    participant_list_xml = milestone_xml.find("./participants_list")
                    for participants_xml in participant_list_xml.findall("./participants"):
                        _, tmp_data = xml_attrib_extract(participants_xml, xml_dict_query)
                        ctgov_group_code, count = tmp_data
                        result_group_id = self.ctgov_group_code2result_group_id[ctgov_group_code]
                        data = [self.nct_id, result_group_id, period, title, ctgov_group_code, description, count]
                        cur.execute(query, data)

    def drop_withdrawals_func(self, milestone_period_xml, cur, period):
        table_name = "drop_withdrawals"
        xml_dict_query = [["group_id", "group_id", False, "%s"],
                          ["count", "count", False, "%d"],
                          ]
        col_names = ["nct_id", "result_group_id", "period", "reason", "ctgov_group_code", "count"]
        query = generate_query(table_name, col_names)
        drop_withdraw_reason_list_xml = xml_find(milestone_period_xml, "drop_withdraw_reason_list", return_string=False)
        if drop_withdraw_reason_list_xml is not None:
            for drop_withdraw_reason_xml in drop_withdraw_reason_list_xml.findall("./drop_withdraw_reason"):
                reason = xml_find(drop_withdraw_reason_xml, "title", return_string=True)
                participant_list_xml = drop_withdraw_reason_xml.find("./participants_list")
                for participants_xml in participant_list_xml.findall("./participants"):
                    _, tmp_data = xml_attrib_extract(participants_xml, xml_dict_query)
                    ctgov_group_code, count = tmp_data
                    result_group_id = self.ctgov_group_code2result_group_id[ctgov_group_code]
                    data = [self.nct_id, result_group_id, period, reason, ctgov_group_code, count]
                    cur.execute(query, data)



clinical_results2db = Clinical_Results()


table_funcs = [studies2db, eligibilities2db, conditions2db, links2db, brief_summaries2db,
               interventions2db.main_func, keywords2db, clinical_results2db.result_outcome_main,
               designs2db, study_references2db, browse_conditions2db, browse_inerventions2db,
               detailed_descriptions2db, participant_flows2db, result_agreements2db, result_contacts2db,
               overall_officials2db, responsible_parties2db, sponsors2db, countries2db, id_information2db]


def individual_xml2db(study_xml, acl_db_parameters=parameters.acl_db_params):
    conn = None
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()

    # for debugging:
    # study_xml = ET.parse("NCT01937130.xml").getroot()
    # query, data = conditions2db(study_xml)
    # if type(data) is list:
    #     for tmp_data in data:
    #         cur.execute(query, tmp_data)
    # else:
    #     cur.execute(query, data)

    for tmp_func in table_funcs:
        tmp_func(study_xml, cur)

    conn.commit()
    conn.close()
    return(None)


def debug_xml2db(xml_filename, test_func, acl_db_parameters=parameters.acl_db_params):
    # study_xml = ET.parse(xml_filename).getroot()


    study_xml = ET.parse(xml_filename).getroot()

    conn = None
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    test_func(study_xml, cur)




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


### !!!!!!!!!!!!!!!!!!!!! obsolete functions: to delete !!!!!!!!!!!!!!!!!!!!!
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