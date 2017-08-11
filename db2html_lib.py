import psycopg2
import parameters


def get_table_colnames(table_name, cur=None, acl_db_parameters=parameters.acl_db_params):
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    tmp_cmd = "SELECT * FROM " + table_name + " LIMIT 0"
    cur.execute(tmp_cmd)
    colnames = [desc[0] for desc in cur.description]
    return(colnames)


def list2dict(key_list, value_list):
    pass