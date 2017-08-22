import alcohol_clinicaltrials_lib as acl
import webbrowser
import db2html_lib as dbl
import parameters

# sovle the encoding problem
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 4th: use FLASK for display
from flask import Flask, render_template, abort, url_for, redirect

# get some basic data for display
num_studies = 100
command = "select nct_id, official_title from studies limit %d;" % (num_studies)
nct_id_title_list = acl.query_postgresql(command, fetchall=True)
nct_id = nct_id_title_list[-1][0]
nct_id = "NCT02315885"  # NCT02315885


app = Flask(__name__)

@app.route('/study_list/')
def main():
    study_list = nct_id_title_list
    return render_template("index.html", **locals())

@app.route('/study_list/<string:nct_id>')
def display_study(nct_id):
    ### basic study information
    studies = dbl.db2table_dict("studies", nct_id, fetchall=False)
    original_study_link = dbl.generate_study_link(nct_id, prefix=parameters.original_study_link_prefix)

    ### design outcome information --> Tracking Information
    design_outcomes = dbl.db2table_dict("design_outcomes", nct_id, fetchall=True)
    unique_design_outcomes = dbl.extract_unique_design_outcomes(design_outcomes)

    ### descriptive information
    brief_summaries = dbl.db2table_dict("brief_summaries", nct_id, fetchall=False)
    detailed_descriptions = dbl.db2table_dict("detailed_descriptions", nct_id, fetchall=False)
    designs = dbl.db2table_dict("designs", nct_id, fetchall=False)
    study_design_model_type = dbl.extract_study_design_tracking_information(designs)
    study_design_model = designs[study_design_model_type]
    conditions = dbl.db2table_dict("conditions", nct_id, fetchall=True)
    # intervention group
    interventions = dbl.db2table_dict("interventions", nct_id, fetchall=True)
    intervention_other_names = dbl.db2table_dict("intervention_other_names", nct_id, fetchall=True)
    interventions = dbl.combine_intervention_other_names(interventions, intervention_other_names)
    # to add intervention other names
    ###
    return(render_template("study.html", **locals()))


if __name__ == '__main__':
    url = "http://127.0.0.1:5000/study_list/"
    webbrowser.open_new(url)
    app.run()



