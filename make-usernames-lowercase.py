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

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','overcoming_thinking_traps.settings')

import django
django.setup()

import pandas as pd

import psycopg2


from study.models import *


conn = psycopg2.connect(database=os.environ['OTT_DBNAME'], user = os.environ['OTT_DBUSER'], password = os.environ['OTT_DBPASS'], host = os.environ['OTT_DBHOST'], port = "5432")
conn = psycopg2.connect(database=os.environ['OTT_DBNAME'], user = os.environ['OTT_DBUSER'], password = os.environ['OTT_DBPASS'], host = os.environ['OTT_DBHOST'] + ".postgres.database.azure.com", port = "5432")
cur = conn.cursor()


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

# make all existing usernames lowercase

cur.execute("SELECT username FROM study_userdetails")
rows = cur.fetchall()

for row in rows:
	username = row[0]
	username = username.lower()
	cur.execute("UPDATE study_userdetails SET username = %s WHERE username = %s", (username, row[0]))



'''
class ThoughtRecord(BaseModel):
	thought_record_id = models.AutoField(primary_key=True)
	username = models.TextField(default='')

	referral_code = models.TextField(default='')

	week_no = models.IntegerField(default=0)
	
	skip_step = models.TextField(default='')
	remove_negative_feeling = models.IntegerField(default=0)
	prompt_to_use = models.TextField(default='')
	refresh_btn = models.IntegerField(default=0)
	more_suggestions_btn = models.IntegerField(default=0)
	descriptive_thought_Q = models.IntegerField(default=0, null=True)
	loading_time = models.FloatField(default=0, null=True)
	A_A = models.IntegerField(default=0, null=True)
	multiple_cognitive_distortions = models.IntegerField(default=0, null=True)
	extra_q = models.IntegerField(default=0, null=True)
	emotion_questions = models.TextField(default='', null=True)
	personalize = models.IntegerField(default=0, null=True)
	readable = models.IntegerField(default=0, null=True)
	psychoeducation = models.IntegerField(default=0, null=True)
	ai = models.IntegerField(default=0, null=True)
	include_emotions = models.IntegerField(default=0, null=True)
'''

# make all existing usernames lowercase

cur.execute("SELECT username FROM study_thoughtrecord")

rows = cur.fetchall()

for row in rows:
	username = row[0]
	username = username.lower()
	cur.execute("UPDATE study_thoughtrecord SET username = %s WHERE username = %s", (username, row[0]))


'''
class Psychoeducation(BaseModel):
	username = models.TextField(default='')
'''

# make all existing usernames lowercase

cur.execute("SELECT username FROM study_psychoeducation")

rows = cur.fetchall()

for row in rows:
	username = row[0]
	username = username.lower()
	cur.execute("UPDATE study_psychoeducation SET username = %s WHERE username = %s", (username, row[0]))

'''
class Homepage(BaseModel):
	username = models.TextField(default='')
'''

# make all existing usernames lowercase

cur.execute("SELECT username FROM study_homepage")
rows = cur.fetchall()

for row in rows:
	username = row[0]
	username = username.lower()
	cur.execute("UPDATE study_homepage SET username = %s WHERE username = %s", (username, row[0]))


from users.models import CustomUser

# make all existing usernames lowercase

cur.execute("SELECT username FROM users_customuser")
rows = cur.fetchall()

for row in rows:
	username = row[0]
	username = username.lower()
	cur.execute("UPDATE users_customuser SET username = %s WHERE username = %s", (username, row[0]))


conn.commit()

cur.close()

conn.close()