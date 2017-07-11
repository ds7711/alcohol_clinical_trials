import numpy as np

# parameters for downloading .xml data from clinicaltrials.org
main_site = "https://clinicaltrials.gov/beta/"
search_url = "https://clinicaltrials.gov/beta/results?term=college&type=&rslt=&age_v=&gndr=&cond=Alcoholic+OR+alcoholism+OR+alcohol&intr=&titles=&outc=&spons=&lead=&id=&cntry1=NA%3AUS&state1=&cntry2=&state2=&cntry3=&state3=&locn=&rcv_s=&rcv_e=&lup_s=&lup_e="
search_url_separating_kw = "results"
download_specification = "&down_flds=all&down_fmt=xml"
download_kw = "/download_fields"
xml_file_name = "acl_db.xml"

# download_kes = ["down_flds=all", "down_fmt=xml"]
# seprator = "&"


# parameters for the acl_database
db_created = False
postgresql_params = "dbname=postgres user=postgres host=localhost password=7711"
acl_db_name = "acl_database"
_acl_db_password = 7711
_acl_db_username = "postgres"
# following string is used to connect to the database
acl_db_params = "dbname=" + acl_db_name + " " + "user=" + _acl_db_username + " " + "password=" + str(_acl_db_password)
# acl_db_params = "dbname=acl_database user=postgres password=7711" # parameters used to connect to the database



# .xml to AACT schema-like database
# columns in the np.array:
#   1st: column name of the database table
#   2nd: data type of the column
#   3rd: extra specification for the column (e.g., NOT NULL or PRIMARY KEY)
#   4th: keywords to query results from .xml for the column
#   5th: is returned result a list? False / True
#   6th: data type for insert entries (e.g., %s )






# Perhaps two separate tables are better


# aact_schema
commands = (
    """
    CREATE TABLE studies (
        nct_id CHARACTER(11) NOT NULL,
        official_title TEXT NOT NULL,
        start_month_year VARCHAR(255),
        verification_month_year VARCHAR(255),
        completion_month_year VARCHAR(255),
        study_type VARCHAR(255),
        acronym VARCHAR(255),
        baseline_population TEXT,
        overall_status VARCHAR(255),
        last_known_status VARCHAR(255),
        phase VARCHAR(255),
        enrollment BIGINT,
        enrollment_type VARCHAR(255),
        source VARCHAR(255),
        number_of_arms BIGINT,
        number_of_groups BIGINT,
        limitations_and_caveats VARCHAR(255),
        PRIMARY KEY (nct_id)
    )
    """
    ,
    """ CREATE TABLE conditions
    (
        nct_id CHARACTER(11) NOT NULL,
        id SERIAL,
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
    )
    """
    ,
    """ CREATE TABLE eligibilities
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            gender VARCHAR(25) NOT NULL,
            minimum_age VARCHAR(25),
            maximum_age VARCHAR(25),
            healthy_volunteers VARCHAR(255),
            population TEXT,
            gender_description TEXT,
            criteria TEXT,
            age_groups VARCHAR(255),
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE links
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            url VARCHAR(500) NOT NULL,
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE outcomes
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            outcome_type VARCHAR(255),
            title TEXT,
            description TEXT,
            time_frame TEXT,
            population TEXT,
            units VARCHAR(255),
            units_analyzed VARCHAR(255),
            anticipated_posting_month_year VARCHAR(255),
            dispersion_type VARCHAR(255),
            param_type VARCHAR(255),
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE interventions
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            intervention_type VARCHAR(255),
            name VARCHAR(255),
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE keywords
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            name VARCHAR(255),
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE designs
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            allocation VARCHAR(255),
            intervention_model VARCHAR(255),
            intervention_model_description VARCHAR(255),
            primary_purpose VARCHAR(255),
            description VARCHAR(255),
            observational_model VARCHAR(255),
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE result_groups
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            ctgov_group_code VARCHAR(255),
            result_type VARCHAR(255),
            title VARCHAR(255),
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE outcome_counts
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            outcome_id INTEGER,
            result_group_id INTEGER,
            ctgov_group_code VARCHAR(255),
            scope VARCHAR(255),
            units VARCHAR(255),
            count INTEGER,
            PRIMARY KEY (id)
        )
    """
    ,
)


# Queries used to fetch data from .xml file
# Each dictionary stores information for one table.
# They key for each dictionary stores the name of the table, its value stores the column name and how data are fetched.



""" CREATE TABLE outcomes
    (
        nct_id CHARACTER(11) NOT NULL,
        id SERIAL,
        outcome_type VARCHAR(255),
        title TEXT,
        description TEXT,
        time_frame TEXT,
        population TEXT,
        units VARCHAR(255),
        units_analyzed VARCHAR(255),
        anticipated_posting_month_year VARCHAR(255),
        dispersion_type VARCHAR(255),
        param_type VARCHAR(255),
        PRIMARY KEY (id)
    )
"""

xml2db_queries = [
    {"studies": [["nct_id", "nct_id", False, "%s"],
                 ["official_title", "title", False, "%s"],
                 ["enrollment", "enrollment", False, "%s"],
                 ["acronym", "acronym", False, "%s"],
                 ["start_month_year", "start_date", False, "%s"],
                 ["completion_month_year", "completion_date", False, "%s"],
                 ["verification_month_year", "last_verified", False, "%s"],
                 ["study_type", "study_types", False, "%s"]]},
    {"conditions": [["nct_id", "nct_id", False, "%s"],
                    ["name", "conditions", True, "%s"]]},
    {"eligibilities": [["nct_id", "nct_id", False, "%s"],
                       ["gender", "gender", False, "%s"],
                       ["minimum_age", "min_age", False, "%s"],
                       ["maximum_age", "max_age", False, "%s"],
                       ["age_groups", "age_groups", True, "%s"]]},
    {"links": [["nct_id", "nct_id", False, "%s"],
               ["url", "url", False, "%s"]]},
    {"outcomes": [["nct_id", "nct_id", False, "%s"],
                  ["title", "title", False, "%s"]]},
]

