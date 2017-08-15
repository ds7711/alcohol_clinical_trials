import psycopg2
import parameters
import alcohol_clinicaltrials_lib as acl


def get_table_colnames(table_name, cur=None, acl_db_parameters=parameters.acl_db_params):
    conn = psycopg2.connect(acl_db_parameters)
    cur = conn.cursor()
    tmp_cmd = "SELECT * FROM " + table_name + " LIMIT 0"
    cur.execute(tmp_cmd)
    colnames = [desc[0] for desc in cur.description]
    return(colnames)


def list2dict(key_list, value_list):
    my_dict = {}
    for key, value in zip(key_list, value_list):
        my_dict[key] = value
    return(my_dict)


def vstack_list(list_of_lists):
    stacked_list = [[] for _ in xrange(len(list_of_lists[0]))]
    for tmp_list in list_of_lists:
        for idx, item in enumerate(tmp_list):
            stacked_list[idx].append(item)
    return(stacked_list)


def db2table_dict(table_name, nct_id, fetchall):
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