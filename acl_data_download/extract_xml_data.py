import numpy as np
import matplotlib.pylab as plt
import parameters
import xml.etree.cElementTree as ET



tree = ET.parse(parameters.xml_file_name)
root = tree.getroot()


# 2nd:

class AlcoholStudy(object):

    def __init__(self):
        self.nct_id = None
        self.official_title = None
        self.gender = None
        self.url = None
        self.conditions = []

as_list = []

study = AlcoholStudy()
for child in root:
    if child.tag != "study":
        continue
        # print child.tag, child.attrib
    if child.attrib["rank"] == "1":
        # print child.tag, child.attrib, child.text
        for subchild in child:
            # print subchild.tag, subchild.attrib, subchild.text
            pass
        study.nct_id = child.find("./nct_id").text
        study.official_title = child.find("./title").text
        study.url = child.find("./url").text
        study.gender = child.find("./gender").text
        condition_list = child.find("./conditions")
        for item in condition_list:
            study.conditions.append(item.text)
    as_list.append(study)



as_list = []
for child in root:
    study = AlcoholStudy()
    if child.tag != "study":
        continue
    study.nct_id = child.find("./nct_id").text
    study.official_title = child.find("./title").text
    study.url = child.find("./url").text
    study.gender = child.find("./gender").text
    condition_list = child.find("./conditions")
    for item in condition_list:
        study.conditions.append(item.text)
    as_list.append(study)



# example: extract nct_id, study title, gender, url
import psycopg2
conn = psycopg2.connect(parameters.acl_db_params)
cur = conn.cursor()
for study in as_list:
    query = "INSERT INTO studies (nct_id, official_title) VALUES (%s, %s);"
    data = (study.nct_id, study.official_title)
    cur.execute(query, data)

cur.execute("SELECT * from studies")
records = cur.fetchall()
