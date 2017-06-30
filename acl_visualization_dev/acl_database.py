
# import required modules/libraries
import numpy as np
import pandas as pd
import matplotlib.pylab as plt # plotting module
import psycopg2 # database connection module


#
condition_keywords = ["Alcohol Abstinence"]

conn = psycopg2.connect("dbname=aact user=postgres password=7711")
cur = conn.cursor()
cur.execute("select * from conditions where name='Alcohol Abstinence'")
condition_table = cur.fetchall()

# subset the data based on the age
cur.execute("select * from eligibilities")
records = cur.fetchall()

max_age = 25
min_age = 16

nct_id_list = []

for item in records:
    if item[4] == "" or item[5] == "":
        continue
    if item[4] == "N/A" or float(item[4][:2]) < min_age:
        continue
    if item[5] == "N/A" or float(item[5][:2]) > max_age:
        continue
    nct_id_list.append(item[1])

nct_id_list = np.unique(nct_id_list)
