import alcohol_clinicaltrials_lib as acl
import xml.etree.cElementTree as ET
import psycopg2
import parameters # cutomized parameters for the script, for editing

"""
data type:
VARCHAR(255),
CHARACTER(11) NOT NULL,
TEXT,
BIGINT,
"""

def create_tables(acl_db_parameters):
    """ create tables in the PostgreSQL database"""
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
            id INTEGER NOT NULL, 
            name VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        )
        """
        ,
        """ CREATE TABLE eligibilities 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                gender VARCHAR(25) NOT NULL,
                PRIMARY KEY (id)
            )
        """
        ,
        """ CREATE TABLE links 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                url VARCHAR(255) NOT NULL,
                description VARCHAR(255),
                PRIMARY KEY (id)
            )
        """
        ,
        """ CREATE TABLE outcomes 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
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
        """ CREATE TABLE intervations 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                intervation_type VARCHAR(255),
                name VARCHAR(255),
                description TEXT,
                PRIMARY KEY (id)
            )
        """
        ,
        """ CREATE TABLE keywords 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                name VARCHAR(255),
                PRIMARY KEY (id)
            )
        """
        ,
        """ CREATE TABLE designs 
            (
                nct_id CHARACTER(11) NOT NULL, 
                id INTEGER NOT NULL, 
                allocation VARCHAR(255),
                intervation_model VARCHAR(255),
                intervation_model_description VARCHAR(255),
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
                id INTEGER NOT NULL PRIMARY KEY, 
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
                id INTEGER NOT NULL, 
                outcome_id INTEGER,
                result_group_id INTEGER,
                ctgov_group_code VARCHAR(255),
                scope VARCHAR(255),
                units VARCHAR(255),
                count INTEGER,
                PRIMARY KEY (id),
            )
        """
        # ,
        # """ CREATE TABLE outcomes
        #     (
        #         nct_id CHARACTER(11) NOT NULL,
        #         id INTEGER NOT NULL,
        #         outcome_type VARCHAR(255)
        #     )
        # """
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

acl.delete_postgresql_db(parameters.acl_db_name, parameters.postgresql_params)


acl.create_postgresql_db(parameters.acl_db_name, parameters.postgresql_params)
study_list = acl.extract_xml_data(parameters.xml_file_name)
acl.write_to_db(study_list, parameters.acl_db_params)