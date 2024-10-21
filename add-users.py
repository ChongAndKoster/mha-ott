import codecs
import os
import numpy as np
import pandas as pd
import csv
import sys
import math
import datetime
import time
import pickle
from tqdm import tqdm
from pytz import timezone

from random import shuffle

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','overcoming_thinking_traps.settings')

import django
django.setup()

from study.models import UserDetails

users = ['bmosser@uw.edu', 'pullmann@uw.edu', 'irgf@uw.edu', 'rouvere@uw.edu', 'mbromane@uw.edu', 'althoff@cs.washington.edu', 'crytting@cs.washington.edu', 'ilin@cs.washington.edu', 'ashshar@cs.washington.edu', 'krushton@mhanational.org', 'jmarion@mhanational.org', 'tnguyen@mhanational.org']


'''
class UserDetails(BaseModel):
	username = models.TextField(default='')
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


for username in users:
	# delete curr username
	UserDetails.objects.filter(username=username).delete()

	# get today's date
	date_started = datetime.datetime.now()
	# print('date_started: ', date_started)

	# pacific time zone
	date_started = date_started.astimezone(timezone('US/Pacific'))

	# print('date_started: ', date_started)

	week_1_start = date_started
	week_1_date = week_1_start.date()
	week_1_start = datetime.datetime.combine(week_1_date, datetime.datetime.min.time()) + datetime.timedelta(minutes=1)
	week_1_datetime = datetime.datetime.combine(week_1_date, datetime.datetime.max.time())
	week_1_datetime = week_1_datetime - datetime.timedelta(minutes=1)
	week_1_expire = week_1_datetime + datetime.timedelta(days=6)
	week_1_start = week_1_start.astimezone(timezone('US/Pacific'))
	week_1_expire = week_1_expire.astimezone(timezone('US/Pacific'))

	# print('week_1_start: ', week_1_start)
	# print('week_1_expire: ', week_1_expire)

	week_2_start = date_started + datetime.timedelta(days=7)
	week_2_date = week_2_start.date()
	week_2_start = datetime.datetime.combine(week_2_date, datetime.datetime.min.time()) + datetime.timedelta(minutes=1)
	week_2_datetime = datetime.datetime.combine(week_2_date, datetime.datetime.max.time())
	week_2_datetime = week_2_datetime - datetime.timedelta(minutes=1)
	week_2_expire = week_2_datetime + datetime.timedelta(days=6)
	week_2_start = week_2_start.astimezone(timezone('US/Pacific'))
	week_2_expire = week_2_expire.astimezone(timezone('US/Pacific'))

	week_3_start = date_started + datetime.timedelta(days=14)
	week_3_date = week_3_start.date()
	week_3_start = datetime.datetime.combine(week_3_date, datetime.datetime.min.time()) + datetime.timedelta(minutes=1)
	week_3_datetime = datetime.datetime.combine(week_3_date, datetime.datetime.max.time())
	week_3_datetime = week_3_datetime - datetime.timedelta(minutes=1)
	week_3_expire = week_3_datetime + datetime.timedelta(days=6)
	week_3_start = week_3_start.astimezone(timezone('US/Pacific'))
	week_3_expire = week_3_expire.astimezone(timezone('US/Pacific'))

	week_4_start = date_started + datetime.timedelta(days=21)
	week_4_date = week_4_start.date()
	week_4_start = datetime.datetime.combine(week_4_date, datetime.datetime.min.time()) + datetime.timedelta(minutes=1)
	week_4_datetime = datetime.datetime.combine(week_4_date, datetime.datetime.max.time())
	week_4_datetime = week_4_datetime - datetime.timedelta(minutes=1)
	week_4_expire = week_4_datetime + datetime.timedelta(days=6)
	week_4_start = week_4_start.astimezone(timezone('US/Pacific'))
	week_4_expire = week_4_expire.astimezone(timezone('US/Pacific'))

	# if username == 'test1':
	# 	condition = '1'
	# elif username == 'test2':
	# 	condition = '2'

	# sample '1' or '2'
	condition = np.random.choice(['1', '2'], p=[0.5, 0.5])

	# create user
	user = UserDetails(username=username, date_started=date_started, week_1_start=week_1_start, week_1_expire=week_1_expire, week_2_start=week_2_start, week_2_expire=week_2_expire, week_3_start=week_3_start, week_3_expire=week_3_expire, week_4_start=week_4_start, week_4_expire=week_4_expire, condition=condition)
	user.save()

	print(user.username, condition)