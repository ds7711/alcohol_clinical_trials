import datetime

# xml2database log filename
current_time = datetime.datetime.now()
suffix = str(current_time)[:-16] + "-" + str(current_time)[-15:-13]
log_filename = "xml2db_log_" + suffix + ".txt"

# parameters for downloading .xml data from clinicaltrials.org
search_url = "https://clinicaltrials.gov/ct2/results?term=college&cond=Alcoholic+OR+alcoholism+OR+alcohol&cntry1=NA%3AUS&age_v=&gndr=&type=&rslt=With&Search=Apply"
zip_download_affix = "https://clinicaltrials.gov/ct2/download_studies?"
search_url_separating_kw = "results"
zip_filename = "acl_results.zip"

# old website
main_site = "https://clinicaltrials.gov/beta/"
download_specification = "&down_flds=all&down_fmt=xml"
download_kw = "/download_fields"
xml_file_name = "acl_db.xml"
individual_study_xml_url = ["https://clinicaltrials.gov/ct2/show/", "?displayxml=true"] # used to create the
# download_keys = ["down_flds=all", "down_fmt=xml"]
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



# aact_schema
commands = (
    """
    CREATE TABLE studies (
        nct_id CHARACTER(11) NOT NULL,
        official_title TEXT,
        start_month_year VARCHAR(255),
        start_date DATE, 
        verification_month_year VARCHAR(255),
        verification_date DATE,
        completion_month_year VARCHAR(255),
        completion_date DATE,
        primary_completion_month_year VARCHAR(255),
        primary_completion_date DATE,
        last_changed_date DATE,
        study_type VARCHAR(255),
        acronym VARCHAR(255),
        baseline_population TEXT,
        overall_status VARCHAR(255),
        last_known_status VARCHAR(255),
        phase VARCHAR(255),
        enrollment INT,
        enrollment_type VARCHAR(255),
        source VARCHAR(255),
        number_of_arms INT,
        number_of_groups INT,
        limitations_and_caveats VARCHAR(255),
        brief_title VARCHAR(255),
        why_stopped VARCHAR(255), 
        has_expanded_access_type VARCHAR(25), 
        has_expanded_access BOOLEAN,
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
            minimum_age_type VARCHAR(25),
            minimum_age INT,
            maximum_age_type VARCHAR(25),
            maximum_age INT,
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
    """ CREATE TABLE interventions
        (
            nct_id CHARACTER(11) NOT NULL,
            id INTEGER,
            intervention_type VARCHAR(255),
            name VARCHAR(255),
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    # intervention_detailed treat experiment group with different dose as different design group
    # e.g., drug group may be divided into low, middle, high three group
    """ CREATE TABLE interventions_detailed
        (
            nct_id CHARACTER(11) NOT NULL,
            id INTEGER,
            intervention_type VARCHAR(255),
            name VARCHAR(255),
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE intervention_other_names
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL, 
            intervention_id INTEGER,
            name VARCHAR(255),
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE design_groups
        (
            nct_id CHARACTER(11) NOT NULL,
            id INTEGER,
            group_type VARCHAR(255),
            title VARCHAR(255),
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE design_group_interventions
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            design_group_id INTEGER,
            intervention_id INTEGER,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE brief_summaries
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE result_groups
        (
            nct_id CHARACTER(11) NOT NULL,
            id INTEGER,
            ctgov_group_code VARCHAR(255),
            result_type VARCHAR(255),
            title VARCHAR(255),
            description TEXT,
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE outcomes
        (
            nct_id CHARACTER(11) NOT NULL,
            id INTEGER,
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
    """ CREATE TABLE reported_events
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            result_group_id INTEGER,
            ctgov_group_code VARCHAR(255),
            time_frame TEXT,
            event_type VARCHAR(255),
            default_vocab VARCHAR(255),
            default_assessment VARCHAR(255),
            subjects_affected VARCHAR(255),
            subjects_at_risk VARCHAR(255),
            description TEXT,
            event_count INTEGER,
            organ_system VARCHAR(255),
            adverse_event_term VARCHAR(255),
            frequent_threshold INTEGER,
            vocal VARCHAR(255),
            assessment VARCHAR(255),
            PRIMARY KEY (id)
        )
    """
    ,
    """ CREATE TABLE outcome_analyses
        (
            nct_id CHARACTER(11) NOT NULL,
            id SERIAL,
            outcome_id INTEGER,
            non_inferiority_type VARCHAR(255),
            non_inferiority_description TEXT,
            param_type VARCHAR(255),
            param_value NUMERIC,
            dispersion_type VARCHAR(255),
            dispersion_value NUMERIC,
            p_value FLOAT,
            p_value_modifier VARCHAR(255),
            p_value_description TEXT,
            ci_n_sides VARCHAR(255),
            ci_percent NUMERIC,
            ci_lower_limit NUMERIC,
            ci_upper_limit NUMERIC,
            ci_upper_limit_na_comment VARCHAR(255),
            method VARCHAR(255),
            method_description TEXT,
            description TEXT,
            estimate_description TEXT,
            groups_description TEXT,
            other_analysis_description TEXT,
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
)








# Queries used to fetch data from .xml file
# Each dictionary stores information for one table.
# They key for each dictionary stores the name of the table, its value stores the column name and how data are fetched.


xml2db_queries = [
    {"studies": [["nct_id", "id_info/nct_id", False, "%s"],
                 ["official_title", "official_title", False, "%s"],
                 ["enrollment", "enrollment", False, "%s"],
                 ["start_month_year", "start_date", False, "%s"],
                 ["completion_month_year", "completion_date", False, "%s"],
                 ["verification_month_year", "verification_date", False, "%s"],
                 ["study_type", "study_type", False, "%s"]]},
    {"conditions": [["nct_id", "id_info/nct_id", False, "%s"],
                    ["name", "conditions", True, "%s"]]},
    {"eligibilities": [["nct_id", "id_info/nct_id", False, "%s"],
                       ["gender", "eligibility/gender", False, "%s"],
                       ["minimum_age", "min_age", False, "%s"],
                       ["maximum_age", "max_age", False, "%s"],
                       ["age_groups", "age_groups", True, "%s"]]},
    {"links": [["nct_id", "id_info/nct_id", False, "%s"],
               ["url", "required_header/url", False, "%s"]]}
]





# .xml to AACT schema-like database
# columns in the np.array:
#   1st: column name of the database table
#   2nd: data type of the column
#   3rd: extra specification for the column (e.g., NOT NULL or PRIMARY KEY)
#   4th: keywords to query results from .xml for the column
#   5th: is returned result a list? False / True
#   6th: data type for insert entries (e.g., %s )






# Perhaps two separate tables are better