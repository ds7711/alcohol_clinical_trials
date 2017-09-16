import alcohol_clinicaltrials_lib as acl
import parameters # cutomized parameters for the script, for editing

def main(search_url):

    # possible search/filter modality here
    # e.g., select only a subset of entries from the database
    # one could use database syntax and customized python function


    test_xml2db = True

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
        zip_filename = acl.download_all_studies(search_url, zip_filename=parameters.zip_filename)


        acl.batch_xml2db(zip_filename)

if __name__== "__main__":
    search_url = parameters.search_url
    main(search_url)


### for debugging only
# debug = True
# if debug:
#     try:
#         acl.delete_postgresql_db(parameters.acl_db_debug, parameters.postgresql_params)
#     except:
#         pass
#     if not parameters.db_created:  # if database doesn't exist, create the db
#         acl.create_postgresql_db(parameters.acl_db_debug, parameters.postgresql_params)
#         acl.create_tables(parameters.acl_db_debug_params, parameters.commands)
#     # acl.debug_xml2db("./data/NCT02274688.xml", test_func=acl.design_outcomes2db)
#     acl.debug_xml2db("NCT00630955_bm.xml", test_func=acl.clinical_results2db.result_outcome_main)