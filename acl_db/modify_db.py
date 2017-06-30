import psycopg2
import parameters

# delete a table
# conn = psycopg2.connect(acl_db_params)
# cur = conn.cursor()
# cur.execute("DROP TABLE studies")

# connect to the tables
conn = psycopg2.connect(parameters.acl_db_params)
cur = conn.cursor()

# insert data into the tables
nct_id_list = ['NCT03135236', 'NCT03135223', 'NCT03135210']
official_title_list = ["a", "b", "c"]
gender_list = ["f", "m", "all"]
url_list = ["1", "2", "3"]

query = "INSERT INTO studies (nct_id, official_title) VALUES (%s, %s);"
data = (nct_id_list[0], official_title_list[0])

query = "INSERT INTO links (nct_id, url, id) VALUES (%s, %s, %s);"
data = (nct_id_list[1], url_list[1], 1)

cur.execute(query, data)
conn.commit()

cur.execute("select * from studies")
records = cur.fetchall()
print(records)

conn.commit()
conn.close()
