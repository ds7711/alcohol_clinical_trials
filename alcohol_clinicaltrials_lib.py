# import required modules
import parameters
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
    return(study_list)


def create_postgresql_db(acl_db_name, admin_params):
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

def delete_postgresql_db(acl_db_name, admin_params):
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

def create_tables(acl_db_parameters):
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE studies (
            nct_id CHARACTER(11) NOT NULL,
            official_title varchar(255) NOT NULL,
            PRIMARY KEY (nct_id)
        )
        """,
        """ CREATE TABLE conditions 
        (
            nct_id CHARACTER(11) NOT NULL, 
            id INTEGER NOT NULL, 
            name VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        )
        """,
        """ CREATE TABLE eligibilities 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                gender VARCHAR(25) NOT NULL,
                PRIMARY KEY (id)
            )
        """,
        """ CREATE TABLE links 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                url VARCHAR(255) NOT NULL,
                description VARCHAR(255),
                PRIMARY KEY (id)
            )
        """,
        """ CREATE TABLE outcomes 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                outcome_type VARCHAR(255)
            )
        """
        )
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


def query_postgresql(command_string, db_conn_parameters):
    conn = None
    conn = psycopg2.connect(db_conn_parameters)
    cur = conn.cursor()
    cur.execute(command_string)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return(records)