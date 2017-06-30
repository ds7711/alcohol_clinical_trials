# import required modules
# connect to database
import psycopg2
import parameters

# database parameters

def create_tables():
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
        conn = psycopg2.connect(parameters.acl_db_params)
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



if __name__ == '__main__':
    create_tables()
