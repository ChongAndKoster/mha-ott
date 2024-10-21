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


curr_date = datetime.datetime.now().astimezone(timezone('US/Pacific'))

print('curr_date: ', curr_date)

# date_started = '2023-11-21 00:01:00+00'
# date_started = datetime.datetime.strptime(date_started, '%Y-%m-%d %H:%M:%S+00')

# get date_started from UserDetails
date_started = UserDetails.objects.filter(username = 'xxxmorganscrighton93xxx@gmail.com')[0].week_1_start

print('date_started: ', date_started)

# compute week_no
week_no = (curr_date - date_started).days // 7 + 1

print((curr_date - date_started))
print('week_no: ', week_no)