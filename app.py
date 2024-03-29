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



############### filtering criterion goes here #############################
# subset studies, can use Python function or SQL commands
num_studies = 1000
command = "select nct_id, official_title, first_received_results_date from studies limit %d;" % (num_studies)
nct_id_title_list = acl.query_postgresql(command, fetchall=True)
tmp_nct_id_list = []
for item in nct_id_title_list:
    if item[2] is not None:
        tmp_nct_id_list.append(item)
nct_id_title_list = tmp_nct_id_list
nct_id = nct_id_title_list[-1][0]

############### filtering criterion goes here #############################


app = Flask(__name__)

@app.route('/study_list/')
def main():
    study_list = nct_id_title_list
    return render_template("index.html", **locals())

@app.route('/study_list/<string:nct_id>')
def display_study(nct_id):

    # the first part uses dbl.db2table_dict_list function whereas the 2nd part uses dbl.db2table_list_dict
    ### basic study information
    studies = dbl.db2table_dict_list("studies", nct_id, fetchall=False)
    original_study_link = dbl.generate_study_link(nct_id, prefix=parameters.original_study_link_prefix)

    ### design outcome information --> Tracking Information
    design_outcomes = dbl.db2table_dict_list("design_outcomes", nct_id, fetchall=True)
    unique_design_outcomes = dbl.extract_unique_design_outcomes(design_outcomes)

    ### descriptive information
    brief_summaries = dbl.db2table_dict_list("brief_summaries", nct_id, fetchall=False)
    detailed_descriptions = dbl.db2table_dict_list("detailed_descriptions", nct_id, fetchall=False)
    designs = dbl.db2table_dict_list("designs", nct_id, fetchall=False)
    study_design_model_type = dbl.extract_study_design_tracking_information(designs)
    study_design_model = designs[study_design_model_type]
    conditions = dbl.db2table_dict_list("conditions", nct_id, fetchall=True)
    # intervention group
    interventions = dbl.db2table_dict_list("interventions", nct_id, fetchall=True)
    intervention_other_names = dbl.db2table_dict_list("intervention_other_names", nct_id, fetchall=True)
    interventions = dbl.combine_intervention_other_names(interventions, intervention_other_names)
    # the first part uses dbl.db2table_dict_list function whereas the 2nd part uses dbl.db2table_list_dict

    # study arms
    design_groups = dbl.db2table_list_dict("design_groups", nct_id, fetchall=True)
    design_group_interventions = dbl.db2table_list_dict("design_group_interventions", nct_id, fetchall=True)
    interventions_list_dict = dbl.db2table_list_dict("interventions", nct_id, fetchall=True)
    design_groups_combined = dbl.combine_design_group_interventions(design_groups,
                                                                    design_group_interventions,
                                                                    interventions_list_dict)
    # Publications
    study_references = dbl.db2table_list_dict("study_references", nct_id, fetchall=True)

    ### Recruitment Information
    # eligibilities
    eligibilities = dbl.db2table_dict_list("eligibilities", nct_id, fetchall=False)

    ### display study results if available
    if studies["first_received_results_date"] is None:
        studies["first_received_results_date"] = False
        ### render the html page
        return(render_template("study.html", **locals()))
    else:
        # participant flow section
        participant_flows = dbl.db2table_dict_list("participant_flows", nct_id, fetchall=False)
        result_groups = dbl.db2table_list_dict("result_groups", nct_id, fetchall=True)
        milestones = dbl.db2table_list_dict("milestones", nct_id, fetchall=True)
        milestone_groups = dbl.extract_milestone_groups(milestones, result_groups)

        # baseline
        baseline_counts = dbl.db2table_dict_list("baseline_counts", nct_id, fetchall=True)
        baseline_counts_group = dbl.extract_baseline_counts(baseline_counts, result_groups)
        baseline_measurements = dbl.db2table_dict_list("baseline_measurements", nct_id, fetchall=True)
        baseline_measurements_group = dbl.extract_baseline_measurements(baseline_measurements, result_groups)

        # outcome
        outcomes = dbl.db2table_list_dict("outcomes", nct_id, fetchall=True)
        outcome_counts = dbl.db2table_dict_list("outcome_counts", nct_id, fetchall=True)

        outcome_counts_group = dbl.extract_outcome_counts(outcome_counts, result_groups)
        outcome_measurements = dbl.db2table_dict_list("outcome_measurements", nct_id, fetchall=True)
        outcome_measurements_group = dbl.extract_outcome_measurements(outcome_measurements, result_groups)
        outcome_combined = dbl.combine_outcome_data(outcomes, outcome_counts_group, outcome_measurements_group)

        # to add events


        
        # to add dropwithdraw list

        ### render the html page
        return (render_template("study.html", **locals()))


if __name__ == '__main__':
    url = "http://127.0.0.1:5000/study_list/"
    webbrowser.open_new(url)
    app.run()


