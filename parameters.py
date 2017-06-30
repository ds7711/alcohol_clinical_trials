
# parameters for downloading .xml data from clinicaltrials.org
main_site = "https://clinicaltrials.gov/beta/"
search_url = "https://clinicaltrials.gov/beta/results?term=college&type=&rslt=&age_v=&gndr=&cond=Alcoholic+OR+alcoholism+OR+alcohol&intr=&titles=&outc=&spons=&lead=&id=&cntry1=NA%3AUS&state1=&cntry2=&state2=&cntry3=&state3=&locn=&rcv_s=&rcv_e=&lup_s=&lup_e="
search_url_separating_kw = "results"
download_specification = "&down_flds=all&down_fmt=xml"
download_kw = "/download_fields"
xml_file_name = "acl_db.xml"

# download_kes = ["down_flds=all", "down_fmt=xml"]
# seprator = "&"


# parameters for the acl_database
db_created = True
postgresql_params = "dbname=postgres user=postgres host=localhost password=7711"
acl_db_name = "acl_database"
_acl_db_password = 7711
_acl_db_username = "postgres"
# following string is used to connect to the database
acl_db_params = "dbname=" + acl_db_name + " " + "user=" + _acl_db_username + " " + "password=" + str(_acl_db_password)
# acl_db_params = "dbname=acl_database user=postgres password=7711" # parameters used to connect to the database


