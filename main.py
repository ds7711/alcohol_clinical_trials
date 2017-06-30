import alcohol_clinicaltrials_lib as acl
import xml.etree.cElementTree as ET
import psycopg2
import parameters # cutomized parameters for the script, for editing


# 1st: download xml file according to customized search criterion
# instructions:
#   use advanced search on clinicaltrials.org and copy the search url
#   input that and the scripts will automatically download all the data in .xml format

search_url = parameters.search_url
acl.download_xml_file(search_url, xml_filename=parameters.xml_file_name)


# 2nd: convert xml to relational database
# structure of the database is similar to that of aact (clinical trials)
# to finish later
# for expandibility in the future
# possibility to search through the database
# convert xml file into data object

acl.delete_postgresql_db(parameters.acl_db_name, parameters.postgresql_params)

if not parameters.db_created: # if database doesn't exist, create the db
    acl.create_postgresql_db(parameters.acl_db_name, parameters.postgresql_params)
    acl.create_tables(parameters.acl_db_params)
    study_list = acl.extract_xml_data(parameters.xml_file_name)
    acl.write_to_db(study_list, parameters.acl_db_params)

studies_from_db = acl.query_postgresql("SELECT * FROM studies")
print(len(studies_from_db), studies_from_db)

# 3rd: display xml file in a user-friendly way
# goals:
#   a. an index page that lists all the studies that satisfy certain criterion
#   b. content pages that display each study as a webpage
#   c. extract data from XML file and fill the data into a template and display it in a webpage


# possible search/filter modality here
# e.g., select only a subset of entries from the database
# one could use database syntax and customized python function


# acl.query_postgresql("SELECT * FROM conditions WHERE nct_id=" + nct_id, parameters.acl_db_params)\


# convert study list into dictionary for display
def list2dict(my_list):
    my_dict = {}
    for idx, item in enumerate(my_list):
        tmp_dict = {}
        tmp_dict["name"] = item[0]
        tmp_dict["price"] = item[1]
        my_dict[str(idx)] = tmp_dict
    return(my_dict)

STUDY_DICT = list2dict(study_list)


# 4th: use FLASK for display
from flask import Flask, render_template, abort
# example data
study_name = "alcohol study"
app = Flask(__name__)
# PRODUCTS = study_dict


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', study_dict=STUDY_DICT)

@app.route('/study/<key>')
def product(key):
    study = STUDY_DICT.get(key)
    if not product:
        abort(404)
    return render_template('product.html', study=study)

if __name__ == '__main__':
    import webbrowser
    url = "http://127.0.0.1:5000/"
    webbrowser.open_new(url)
    app.run()


# 4th: additional functionalities (search, visualization)
# to finish later


# Time estimation
# Page display: 3-4 weeks
# XML to relational database: 3-4 weeks
# search & additional functions: ???


# hola to overcome the blocking issues



# get the names of all tables
conn = None
conn = psycopg2.connect(parameters.acl_db_params)
cur = conn.cursor()
cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
for table in cur.fetchall():
    print(table)
cur.close()
conn.close()



# test
conn = psycopg2.connect(parameters.acl_db_params)
cur = conn.cursor()
cur.execute("SELECT * from studies")
records = cur.fetchall()
cur.close()
conn.close()
print(records)


# extract the nct_id from the database
conn = None
conn = psycopg2.connect(parameters.acl_db_params)
cur = conn.cursor()
cur.execute("SELECT * from studies")
study_list = cur.fetchall()
cur.close()
conn.close()
print(study_list)

conn = None
conn = psycopg2.connect(parameters.acl_db_params)
cur = conn.cursor()
cur.execute("SELECT nct_id from studies")
nct_id_list = cur.fetchall()
cur.close()
conn.close()
print(nct_id_list)