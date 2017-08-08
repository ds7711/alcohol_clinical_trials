import alcohol_clinicaltrials_lib as acl
import psycopg2
import parameters # cutomized parameters for the script, for editing

# 3rd: display xml file in a user-friendly way
# goals:
#   a. an index page that lists all the studies that satisfy certain criterion
#   b. content pages that display each study as a webpage
#   c. extract data from XML file and fill the data into a template and display it in a webpage

nct_id = "NCT00130923"

records = acl.query_postgresql("select * from studies where nct_id = " + nct_id)

# possible search/filter modality here
# e.g., select only a subset of entries from the database
# one could use database syntax and customized python function






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



test_xml2db = False

if test_xml2db:
    # 1st: create the relational database
    try:
        acl.delete_postgresql_db(parameters.acl_db_name, parameters.postgresql_params)
    except:
        pass
    if not parameters.db_created: # if database doesn't exist, create the db
        acl.create_postgresql_db(parameters.acl_db_name, parameters.postgresql_params)
        acl.create_tables(parameters.acl_db_params, parameters.commands)

    # 2nd: download xml file according to customized search criterion
    # instructions:
    #   use advanced search on clinicaltrials.org and copy the search url
    #   input that and the scripts will automatically download all the data in .xml format
    search_url = parameters.search_url
    search_url = "https://clinicaltrials.gov/ct2/results?term=alcohol&age_v=&age=1&gndr=&type=&rslt=&Search=Apply"
    zip_filename = acl.download_all_studies(search_url, zip_filename=parameters.zip_filename)

    ### debug
    # acl.debug_xml2db("NCT01937130_results.xml", test_func=acl.clinical_results2db.result_outcome_main)
    # acl.debug_xml2db("./data/NCT02274688.xml", test_func=acl.eligibilities2db)

    # convert .xml files into database
    acl.batch_xml2db(zip_filename)