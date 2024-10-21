import codecs
import os
import numpy as np
import csv
import sys
import math
import datetime
import time
import pickle
from random import shuffle
from pytz import timezone

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','overcoming_thinking_traps.settings')

import django
django.setup()

import pandas as pd

import psycopg2


from study.models import *

'''class UserDetails(BaseModel):
	username = models.TextField(default='')
	study_id = models.TextField(default='')
	n8m95 = models.TextField(default='')
	earnings = models.FloatField(default=0)
	condition = models.TextField(default='')
	date_started = models.DateTimeField(null=True)

	week_1_start = models.DateTimeField(null=True)
	week_1_expire = models.DateTimeField(null=True)

	week_2_start = models.DateTimeField(null=True)
	week_2_expire = models.DateTimeField(null=True)

	week_3_start = models.DateTimeField(null=True)
	week_3_expire = models.DateTimeField(null=True)

	week_4_start = models.DateTimeField(null=True)
	week_4_expire = models.DateTimeField(null=True)

	week_1_use = models.IntegerField(default=0)
	week_2_use = models.IntegerField(default=0)
	week_3_use = models.IntegerField(default=0)
	week_4_use = models.IntegerField(default=0)

	survey_1_status = models.IntegerField(default=0)
	survey_2_status = models.IntegerField(default=0)
	survey_3_status = models.IntegerField(default=0)
	survey_4_status = models.IntegerField(default=0)
	survey_5_status = models.IntegerField(default=0)
	survey_8_status = models.IntegerField(default=0)
'''

# convert all datetimes in UserDetails to pacific time by reducing eight hours

def convert_to_pacific_time(date):
	date = date + datetime.timedelta(hours=8)
	return date


# conn = psycopg2.connect(database=os.environ['OTT_DBNAME'], user = os.environ['OTT_DBUSER'], password = os.environ['OTT_DBPASS'], host = os.environ['OTT_DBHOST'] + ".postgres.database.azure.com", port = "5432")
conn = psycopg2.connect(database=os.environ['OTT_DBNAME'], user = os.environ['OTT_DBUSER'], password = os.environ['OTT_DBPASS'], host = os.environ['OTT_DBHOST'], port = "5432")
cur = conn.cursor()


cur.execute("SELECT username,date_started,week_1_start,week_1_expire,week_2_start,week_2_expire,week_3_start,week_3_expire,week_4_start,week_4_expire FROM study_userdetails")
rows = cur.fetchall()

for row in rows:
	username = row[0]
	date_started = row[1]
	week_1_start = row[2]
	week_1_expire = row[3]
	week_2_start = row[4]
	week_2_expire = row[5]
	week_3_start = row[6]
	week_3_expire = row[7]
	week_4_start = row[8]
	week_4_expire = row[9]

	date_started = convert_to_pacific_time(date_started)
	week_1_start = convert_to_pacific_time(week_1_start)
	week_1_expire = convert_to_pacific_time(week_1_expire)
	week_2_start = convert_to_pacific_time(week_2_start)
	week_2_expire = convert_to_pacific_time(week_2_expire)
	week_3_start = convert_to_pacific_time(week_3_start)
	week_3_expire = convert_to_pacific_time(week_3_expire)
	week_4_start = convert_to_pacific_time(week_4_start)
	week_4_expire = convert_to_pacific_time(week_4_expire)

	cur.execute("UPDATE study_userdetails SET date_started = %s, week_1_start = %s, week_1_expire = %s, week_2_start = %s, week_2_expire = %s, week_3_start = %s, week_3_expire = %s, week_4_start = %s, week_4_expire = %s WHERE username = %s", (date_started, week_1_start, week_1_expire, week_2_start, week_2_expire, week_3_start, week_3_expire, week_4_start, week_4_expire, username))

conn.commit()
cur.close()
conn.close()