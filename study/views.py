from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
import hashlib
# Create your views here.

import codecs
import os
import requests
from requests.exceptions import ConnectTimeout


import numpy as np 
import json 
import pprint
import time
from random import shuffle
import datetime
import pandas as pd
from pytz import timezone
import random


from django.contrib.auth.decorators import login_required

from .redcap_sync import redcap_sync

from .models import ToolUseAssignments, \
					UserDetails, \
					ThoughtRecord, \
					Thought, \
					Emotion, \
					Situation, \
					Thinking_Trap_Generated, \
					Thinking_Trap_Selected, \
					Reframes_Generated, \
					Reframe_Selected, \
					Reframe_Final, \
					Outcome, \
					Step_Logs, \
					Start_Over, \
					Show_More_Thinking_Traps, \
					Flag_Inappropriate, \
					Demographics, \
					OpenAI_Error, \
					Consent, \
					Next_Check_Error, \
					Safety_Filter, \
					URL_Clicks, \
					Refresh_Btn, \
					Feedback, \
					Reframes_More_Help, \
					Psychoeducation, \
					Homepage, \
					Redcap_Consent, \
					Redcap_Week_No, \
					Redcap_Payments
# Create your views here.

def cognitive_restructuring(request):
	email = request.GET.get('email', None)

	if email:
		# save psychoeducaiton
		curr_psychoeducation = Psychoeducation(username = email)
		curr_psychoeducation.save()
		return render(request, "study/cognitive_restructuring.html", {})
	else:
		return redirect('/study/error.html')

def error_message(request):
	return render(request, "study/error.html", {'error_msg': 'Error'})


def check_redcap(request):
	# if request.method == 'POST':
	
	return render(request, "study/check_redcap.html", {})

def admin(request):
	# if request.method == 'POST':
	return render(request, "study/admin.html", {})



def get_users():

	userdetails = UserDetails.objects.all()

	TOTAL_USERS = set()
	USERS_WEEK_4_PLUS = set()
	ONE_WEEK_COMPLETED = set()
	TWO_WEEKS_COMPLETED = set()
	THREE_WEEKS_COMPLETED = set()
	FOUR_WEEKS_COMPLETED = set()

	ONE_SURVEY_COMPLETED = set()
	TWO_SURVEY_COMPLETED = set()
	THREE_SURVEY_COMPLETED = set()
	FOUR_SURVEY_COMPLETED = set()


	CONDITION_0_USERS = set()
	CONDITION_1_USERS = set()
	CONDITION_2_USERS = set()

	TOOL_USAGE = {}




	userdetails_df = pd.DataFrame(list(userdetails.values()), columns=['created_at', 'updated_at', 'username', 'study_id', 'n8m95', 'earnings', 'condition', 'date_started', 'week_1_start', 'week_1_expire', 'week_2_start', 'week_2_expire', 'week_3_start', 'week_3_expire', 'week_4_start', 'week_4_expire', 'week_1_use', 'week_2_use', 'week_3_use', 'week_4_use', 'survey_1_status', 'survey_2_status', 'survey_3_status', 'survey_4_status', 'survey_5_status', 'survey_8_status'])

	# get all consent
	redcap_consent = Redcap_Consent.objects.all()

	redcap_consent_df = pd.DataFrame(list(redcap_consent.values()), columns=['created_at', 'updated_at', 'study_id', 'n8m95', 'redcap_event_name', 'consent_yn', 'consent_complete'])

	# merge
	all_users = pd.merge(userdetails_df, redcap_consent_df, on = 'study_id', how = 'inner')

	redcap_week_no = Redcap_Week_No.objects.all()
	redcap_payments = Redcap_Payments.objects.all()

	redcap_week_no_df = pd.DataFrame(list(redcap_week_no.values()), columns=['created_at', 'updated_at', 'study_id', 'w1', 'w2', 'w3', 'w4', 'w5', 'w8'])
	redcap_payments_df = pd.DataFrame(list(redcap_payments.values()), columns=['created_at', 'updated_at', 'study_id', 'w1_paid', 'w1_amt', 'pay_date_w1', 'w2_paid', 'w2_amt', 'pay_date_w2', 'w3_paid', 'w3_amt', 'pay_date_w3', 'w4_paid', 'w4_amt', 'pay_date_w4', 'w5_paid', 'w5_amt', 'pay_date_w5', 'w8_paid', 'w8_amt', 'pay_date_w8'])

	# sort by updated_at
	redcap_week_no_df = redcap_week_no_df.sort_values(by = ['updated_at'], ascending = True)
	redcap_payments_df = redcap_payments_df.sort_values(by = ['updated_at'], ascending = True)

	# deduplicate by study_id, keep last
	redcap_week_no_df = redcap_week_no_df.drop_duplicates(subset=['study_id'], keep='last')
	redcap_payments_df = redcap_payments_df.drop_duplicates(subset=['study_id'], keep='last')

	# fillna with ''
	redcap_week_no_df = redcap_week_no_df.fillna('')
	redcap_payments_df = redcap_payments_df.fillna('')

	# merge
	all_users = pd.merge(all_users, redcap_week_no_df, on = 'study_id', how = 'left')
	all_users = pd.merge(all_users, redcap_payments_df, on = 'study_id', how = 'left')

	# fillna with ''
	all_users = all_users.fillna('')

	# make 'study_id' to int
	all_users = all_users.astype({'study_id': 'int64'})

	all_users = all_users.loc[all_users['study_id'] >= 70]

	all_users = all_users.loc[all_users['consent_complete'] == '2']

	# localize date_started to US/Pacific

	all_users['date_started'] = pd.to_datetime(all_users['date_started'])
	# all_users['date_started'] = all_users['date_started'].dt.tz_convert('US/Pacific')


	all_users['week_1_remaining'] = 3 - all_users['week_1_use']
	all_users['week_2_remaining'] = 3 - all_users['week_2_use']
	all_users['week_3_remaining'] = 3 - all_users['week_3_use']
	all_users['week_4_remaining'] = 3 - all_users['week_4_use']
	

	curr_datetime = datetime.datetime.now()
	curr_datetime = curr_datetime.astimezone(timezone('US/Pacific'))



	CONDITION_MAP = {'0': 'Pure control', '1': 'DIY, without AI', '2': 'DIY, with AI'}

	all_users['condition'] = all_users['condition'].map(CONDITION_MAP)

	# make 'date_started' to date only
	all_users['date_started'] = all_users['date_started'].dt.date

	# sort by study_id
	all_users = all_users.sort_values(by = ['date_started'], ascending = True)


	# for condition == 1 or 2, sum week_1_status

	print(all_users.groupby(['condition', 'survey_1_status']).size())
	


	data = []

	cnt = 1

	for idx, elem in all_users.iterrows():
		week_1_expire = elem['week_1_expire']
		week_2_expire = elem['week_2_expire']
		week_3_expire = elem['week_3_expire']
		week_4_expire = elem['week_4_expire']

		week_1_start = elem['week_1_start']
		week_2_start = elem['week_2_start']
		week_3_start = elem['week_3_start']
		week_4_start = elem['week_4_start']

		# week_1_start + 
		week_5_start = week_1_start + datetime.timedelta(days=28)
		week_8_start = week_1_start + datetime.timedelta(days=49)

		week_1_remaining = elem['week_1_remaining']
		week_2_remaining = elem['week_2_remaining']
		week_3_remaining = elem['week_3_remaining']
		week_4_remaining = elem['week_4_remaining']

		survey_1_status = elem['survey_1_status']
		survey_2_status = elem['survey_2_status']
		survey_3_status = elem['survey_3_status']
		survey_4_status = elem['survey_4_status']
		survey_5_status = elem['survey_5_status']
		survey_8_status = elem['survey_8_status']

		TOTAL_USERS.add(elem['study_id'])


		if curr_datetime > week_1_expire and week_1_remaining > 0:
			week_1_status = 'expired'
		elif curr_datetime > week_1_start and week_1_remaining <= 0:
			week_1_status = 'completed'
		elif curr_datetime > week_1_start and week_1_remaining > 0:
			week_1_status = 'active'
		else:
			week_1_status = 'TBA'

		if curr_datetime > week_2_expire and week_2_remaining > 0:
			week_2_status = 'expired'
		elif curr_datetime > week_2_start and week_2_remaining <= 0:
			week_2_status = 'completed'
		elif curr_datetime > week_2_start and week_2_remaining > 0:
			week_2_status = 'active'
		else:
			week_2_status = 'TBA'

		if curr_datetime > week_3_expire and week_3_remaining > 0:
			week_3_status = 'expired'
		elif curr_datetime > week_3_start and week_3_remaining <= 0:
			week_3_status = 'completed'
		elif curr_datetime > week_3_start and week_3_remaining > 0:
			week_3_status = 'active'
		else:
			week_3_status = 'TBA'
		
		if curr_datetime > week_4_expire and week_4_remaining > 0:
			week_4_status = 'expired'
		elif curr_datetime > week_4_start and week_4_remaining <= 0:
			week_4_status = 'completed'
		elif curr_datetime > week_4_start and week_4_remaining > 0:
			week_4_status = 'active'
		else:
			week_4_status = 'TBA'


		total_earnings = 0
		total_remaining_earnings = 0
		total_possible_earnings = 0

		week_1_earnings = 0
		week_2_earnings = 0
		week_3_earnings = 0
		week_4_earnings = 0
		week_5_earnings = 0
		week_8_earnings = 0

		if week_1_status == 'TBA' or week_1_status == 'active':
			total_possible_earnings += 5
		elif week_1_status == 'completed':
			total_earnings += 5
			week_1_earnings += 5
			total_possible_earnings += 5

		if week_2_status == 'TBA' or week_2_status == 'active':
			total_possible_earnings += 5
		elif week_2_status == 'completed':
			total_earnings += 5
			week_2_earnings += 5
			total_possible_earnings += 5

		
		if week_3_status == 'TBA' or week_3_status == 'active':
			total_possible_earnings += 5
		elif week_3_status == 'completed':
			total_earnings += 5
			week_3_earnings += 5
			total_possible_earnings += 5

		if week_4_status == 'TBA' or week_4_status == 'active':
			total_possible_earnings += 5
		elif week_4_status == 'completed':
			total_earnings += 5
			week_4_earnings += 5
			total_possible_earnings += 5

		
		if survey_1_status == 1:
			total_earnings += 5
			week_1_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_2_status == 1:
			total_earnings += 5
			week_2_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_3_status == 1:
			total_earnings += 5
			week_3_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_4_status == 1:
			total_earnings += 5
			week_4_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_5_status == 1:
			total_earnings += 10
			week_5_earnings += 10
			total_possible_earnings += 10
		else:
			total_possible_earnings += 10

		if survey_8_status == 1:
			total_earnings += 10
			week_8_earnings += 10
			total_possible_earnings += 10
		else:
			total_possible_earnings += 10


		curr_week = ''
		if week_4_status == 'active' or week_4_status == 'completed':
			curr_week = 'Week 4'
		elif week_3_status == 'active' or week_3_status == 'completed':
			curr_week = 'Week 3'
		elif week_2_status == 'active' or week_2_status == 'completed':
			curr_week = 'Week 2'
		elif week_1_status == 'active' or week_1_status == 'completed':
			curr_week = 'Week 1'
		elif curr_datetime > week_5_start and curr_datetime < week_8_start:
			curr_week = 'Week 5'
		elif curr_datetime > week_8_start:
			curr_week = 'Week 8'

		if week_4_status == 'completed' or curr_week == 'Week 5' or curr_week == 'Week 8':
			USERS_WEEK_4_PLUS.add(elem['study_id'])

		if week_1_status == 'completed' and week_2_status == 'completed' and week_3_status == 'completed' and week_4_status == 'completed':
			FOUR_WEEKS_COMPLETED.add(elem['study_id'])

		if (week_1_status == 'completed' and week_2_status == 'completed' and week_3_status == 'completed') or (week_2_status == 'completed' and week_3_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_3_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_2_status == 'completed' and week_4_status == 'completed'):
			THREE_WEEKS_COMPLETED.add(elem['study_id'])
		
		if (week_1_status == 'completed' and week_2_status == 'completed') or (week_2_status == 'completed' and week_3_status == 'completed') or (week_3_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_3_status == 'completed') or (week_2_status == 'completed' and week_4_status == 'completed'):
			TWO_WEEKS_COMPLETED.add(elem['study_id'])
		
		if week_1_status == 'completed' or week_2_status == 'completed' or week_3_status == 'completed' or week_4_status == 'completed':
			ONE_WEEK_COMPLETED.add(elem['study_id'])


		if survey_1_status == 1 and survey_2_status == 1 and survey_3_status == 1 and survey_4_status == 1:
			FOUR_SURVEY_COMPLETED.add(elem['study_id'])
		
		if (survey_1_status == 1 and survey_2_status == 1 and survey_3_status == 1) or (survey_2_status == 1 and survey_3_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_3_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_2_status == 1 and survey_4_status == 1):
			THREE_SURVEY_COMPLETED.add(elem['study_id'])
		
		if (survey_1_status == 1 and survey_2_status == 1) or (survey_2_status == 1 and survey_3_status == 1) or (survey_3_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_3_status == 1) or (survey_2_status == 1 and survey_4_status == 1):
			TWO_SURVEY_COMPLETED.add(elem['study_id'])
		
		if survey_1_status == 1 or survey_2_status == 1 or survey_3_status == 1 or survey_4_status == 1:
			ONE_SURVEY_COMPLETED.add(elem['study_id'])
		

		# fill 0 with ''

		if elem['week_1_use'] == 0:
			elem['week_1_use'] = ''
		if elem['week_2_use'] == 0:
			elem['week_2_use'] = ''
		if elem['week_3_use'] == 0:
			elem['week_3_use'] = ''
		if elem['week_4_use'] == 0:
			elem['week_4_use'] = ''
		if elem['survey_1_status'] == 0:
			elem['survey_1_status'] = ''
		if elem['survey_2_status'] == 0:
			elem['survey_2_status'] = ''
		if elem['survey_3_status'] == 0:
			elem['survey_3_status'] = ''
		if elem['survey_4_status'] == 0:
			elem['survey_4_status'] = ''
		if elem['survey_5_status'] == 0:
			elem['survey_5_status'] = ''
		if elem['survey_8_status'] == 0:
			elem['survey_8_status'] = ''

		if elem['condition'] == 'Pure control':
			CONDITION_0_USERS.add(elem['study_id'])
		elif elem['condition'] == 'DIY, without AI':
			CONDITION_1_USERS.add(elem['study_id'])
		elif elem['condition'] == 'DIY, with AI':
			CONDITION_2_USERS.add(elem['study_id'])

		try:
			week_1_use = int(elem['week_1_use'])
		except:
			week_1_use = 0
		
		try:
			week_2_use = int(elem['week_2_use'])
		except:
			week_2_use = 0
		
		try:
			week_3_use = int(elem['week_3_use'])
		except:
			week_3_use = 0
		
		try:
			week_4_use = int(elem['week_4_use'])
		except:
			week_4_use = 0

		TOOL_USAGE[elem['study_id']] = week_1_use + week_2_use + week_3_use + week_4_use
		
		# 'w1', 'w2', 'w3', 'w4', 'w5', 'w8'

		# 'w1_paid', 'w1_amt', 'pay_date_w1', 'w2_paid', 'w2_amt', 'pay_date_w2', 'w3_paid', 'w3_amt', 'pay_date_w3', 'w4_paid', 'w4_amt', 'pay_date_w4', 'w5_paid', 'w5_amt', 'pay_date_w5', 'w8_paid', 'w8_amt', 'pay_date_w8'

		# curr_data = [cnt, elem['study_id'], elem['date_started'], elem['condition'], total_earnings, curr_week, elem['week_1_use'], elem['survey_1_status'], elem['week_2_use'], elem['survey_2_status'], elem['week_3_use'], elem['survey_3_status'], elem['week_4_use'], elem['survey_4_status'], elem['survey_5_status'], elem['survey_8_status'], elem['w1'], elem['w1_paid'], elem['w1_amt'], elem['pay_date_w1'], elem['w2'], elem['w2_paid'], elem['w2_amt'], elem['pay_date_w2'], elem['w3'], elem['w3_paid'], elem['w3_amt'], elem['pay_date_w3'], elem['w4'], elem['w4_paid'], elem['w4_amt'], elem['pay_date_w4'], elem['w5'], elem['w5_paid'], elem['w5_amt'], elem['pay_date_w5'], elem['w8'], elem['w8_paid'], elem['w8_amt'], elem['pay_date_w8'], week_1_earnings, week_2_earnings, week_3_earnings, week_4_earnings, week_5_earnings, week_8_earnings, total_possible_earnings, elem['week_1_remaining'], elem['week_2_remaining'], elem['week_3_remaining'], elem['week_4_remaining'], week_1_status, week_2_status, week_3_status, week_4_status, elem['survey_1_status'], elem['survey_2_status'], elem['survey_3_status'], elem['survey_4_status'], elem['survey_5_status'], elem['survey_8_status']]

		# data.append(curr_data)

		cnt += 1

	# print('TOTAL_USERS:', len(TOTAL_USERS))
	# print('USERS_WEEK_4_PLUS:', len(USERS_WEEK_4_PLUS))
	# print('ONE_WEEK_COMPLETED:', len(ONE_WEEK_COMPLETED))
	# print('TWO_WEEKS_COMPLETED:', len(TWO_WEEKS_COMPLETED))
	# print('THREE_WEEKS_COMPLETED:', len(THREE_WEEKS_COMPLETED))
	# print('FOUR_WEEKS_COMPLETED:', len(FOUR_WEEKS_COMPLETED))

	# print('CONDITION_0_USERS:', len(CONDITION_0_USERS))
	# print('CONDITION_1_USERS:', len(CONDITION_1_USERS))
	# print('CONDITION_2_USERS:', len(CONDITION_2_USERS))

	# # Condition users week_4_plus
	# print('CONDITION_0_USERS-WEEK4_PLUS:', len(CONDITION_0_USERS.intersection(USERS_WEEK_4_PLUS)))
	# print('CONDITION_1_USERS-WEEK4_PLUS:', len(CONDITION_1_USERS.intersection(USERS_WEEK_4_PLUS)))
	# print('CONDITION_2_USERS-WEEK4_PLUS:', len(CONDITION_2_USERS.intersection(USERS_WEEK_4_PLUS)))



	# print('FOUR_WEEKS_COMPLETED:', (FOUR_WEEKS_COMPLETED))
	# print('USERS_WEEK_4_PLUS:', (USERS_WEEK_4_PLUS))

	ONE_WEEK_COMPLETED = ONE_WEEK_COMPLETED.intersection(USERS_WEEK_4_PLUS)
	TWO_WEEKS_COMPLETED = TWO_WEEKS_COMPLETED.intersection(USERS_WEEK_4_PLUS)
	THREE_WEEKS_COMPLETED = THREE_WEEKS_COMPLETED.intersection(USERS_WEEK_4_PLUS)
	FOUR_WEEKS_COMPLETED = FOUR_WEEKS_COMPLETED.intersection(USERS_WEEK_4_PLUS)

	CONDITION_0_USERS = CONDITION_0_USERS.intersection(USERS_WEEK_4_PLUS)
	CONDITION_1_USERS = CONDITION_1_USERS.intersection(USERS_WEEK_4_PLUS)
	CONDITION_2_USERS = CONDITION_2_USERS.intersection(USERS_WEEK_4_PLUS)


	ONE_SURVEY_COMPLETED = ONE_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)
	TWO_SURVEY_COMPLETED = TWO_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)
	THREE_SURVEY_COMPLETED = THREE_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)
	FOUR_SURVEY_COMPLETED = FOUR_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)


	return TOTAL_USERS, USERS_WEEK_4_PLUS, ONE_WEEK_COMPLETED, TWO_WEEKS_COMPLETED, THREE_WEEKS_COMPLETED, FOUR_WEEKS_COMPLETED, CONDITION_0_USERS, CONDITION_1_USERS, CONDITION_2_USERS, ONE_SURVEY_COMPLETED, TWO_SURVEY_COMPLETED, THREE_SURVEY_COMPLETED, FOUR_SURVEY_COMPLETED, TOOL_USAGE


def admin_dashboard(request):	
	if request.method == 'POST':

		code = request.POST.get('code', None)

		print('code:', code)

		if code == '3895':
			# sync redcap
			redcap_sync(last_sync=True, login_sync=False)

			# get all users
			userdetails = UserDetails.objects.all()

			TOTAL_USERS = set()
			USERS_WEEK_4_PLUS = set()
			ONE_WEEK_COMPLETED = set()
			TWO_WEEKS_COMPLETED = set()
			THREE_WEEKS_COMPLETED = set()
			FOUR_WEEKS_COMPLETED = set()

			ONE_SURVEY_COMPLETED = set()
			TWO_SURVEY_COMPLETED = set()
			THREE_SURVEY_COMPLETED = set()
			FOUR_SURVEY_COMPLETED = set()


			CONDITION_0_USERS = set()
			CONDITION_1_USERS = set()
			CONDITION_2_USERS = set()

			TOOL_USAGE = {}


			userdetails_df = pd.DataFrame(list(userdetails.values()), columns=['created_at', 'updated_at', 'username', 'study_id', 'n8m95', 'earnings', 'condition', 'date_started', 'week_1_start', 'week_1_expire', 'week_2_start', 'week_2_expire', 'week_3_start', 'week_3_expire', 'week_4_start', 'week_4_expire', 'week_1_use', 'week_2_use', 'week_3_use', 'week_4_use', 'survey_1_status', 'survey_2_status', 'survey_3_status', 'survey_4_status', 'survey_5_status', 'survey_8_status'])

			# get all consent
			redcap_consent = Redcap_Consent.objects.all()

			redcap_consent_df = pd.DataFrame(list(redcap_consent.values()), columns=['created_at', 'updated_at', 'study_id', 'n8m95', 'redcap_event_name', 'consent_yn', 'consent_complete'])

			# merge
			all_users = pd.merge(userdetails_df, redcap_consent_df, on = 'study_id', how = 'inner')

			# all_users['study_id'] = all_users['study_id'].astype('int')

			# # max srtudy_id
			# print('max study_id:', all_users['study_id'].max())

			redcap_week_no = Redcap_Week_No.objects.all()
			redcap_payments = Redcap_Payments.objects.all()

			redcap_week_no_df = pd.DataFrame(list(redcap_week_no.values()), columns=['created_at', 'updated_at', 'study_id', 'w1', 'w2', 'w3', 'w4', 'w5', 'w8'])
			redcap_payments_df = pd.DataFrame(list(redcap_payments.values()), columns=['created_at', 'updated_at', 'study_id', 'w1_paid', 'w1_amt', 'pay_date_w1', 'w2_paid', 'w2_amt', 'pay_date_w2', 'w3_paid', 'w3_amt', 'pay_date_w3', 'w4_paid', 'w4_amt', 'pay_date_w4', 'w5_paid', 'w5_amt', 'pay_date_w5', 'w8_paid', 'w8_amt', 'pay_date_w8'])

			# sort by updated_at
			redcap_week_no_df = redcap_week_no_df.sort_values(by = ['updated_at'], ascending = True)
			redcap_payments_df = redcap_payments_df.sort_values(by = ['updated_at'], ascending = True)

			# deduplicate by study_id, keep last
			redcap_week_no_df = redcap_week_no_df.drop_duplicates(subset=['study_id'], keep='last')
			redcap_payments_df = redcap_payments_df.drop_duplicates(subset=['study_id'], keep='last')

			# fillna with ''
			redcap_week_no_df = redcap_week_no_df.fillna('')
			redcap_payments_df = redcap_payments_df.fillna('')

			# merge
			all_users = pd.merge(all_users, redcap_week_no_df, on = 'study_id', how = 'left')
			all_users = pd.merge(all_users, redcap_payments_df, on = 'study_id', how = 'left')

			# fillna with ''
			all_users = all_users.fillna('')

			# make 'study_id' to int
			all_users = all_users.astype({'study_id': 'int64'})

			all_users = all_users.loc[all_users['study_id'] >= 70]

			all_users = all_users.loc[all_users['consent_complete'] == '2']

			# localize date_started to US/Pacific

			all_users['date_started'] = pd.to_datetime(all_users['date_started'])
			# all_users['date_started'] = all_users['date_started'].dt.tz_convert('US/Pacific')


			all_users['week_1_remaining'] = 3 - all_users['week_1_use']
			all_users['week_2_remaining'] = 3 - all_users['week_2_use']
			all_users['week_3_remaining'] = 3 - all_users['week_3_use']
			all_users['week_4_remaining'] = 3 - all_users['week_4_use']
			

			curr_datetime = datetime.datetime.now()
			curr_datetime = curr_datetime.astimezone(timezone('US/Pacific'))



			CONDITION_MAP = {'0': 'Pure control', '1': 'DIY, without AI', '2': 'DIY, with AI'}

			all_users['condition'] = all_users['condition'].map(CONDITION_MAP)

			# make 'date_started' to date only
			all_users['date_started'] = all_users['date_started'].dt.date

			# sort by study_id
			all_users = all_users.sort_values(by = ['date_started'], ascending = True)


			# for condition == 1 or 2, sum week_1_status

			print(all_users.groupby(['condition', 'survey_1_status']).size())
			
			all_users_earnings = 0

			data = []

			cnt = 1

			week_4_users_earnings = 0

			for idx, elem in all_users.iterrows():
				week_1_expire = elem['week_1_expire']
				week_2_expire = elem['week_2_expire']
				week_3_expire = elem['week_3_expire']
				week_4_expire = elem['week_4_expire']

				week_1_start = elem['week_1_start']
				week_2_start = elem['week_2_start']
				week_3_start = elem['week_3_start']
				week_4_start = elem['week_4_start']

				# week_1_start + 
				week_5_start = week_1_start + datetime.timedelta(days=28)
				week_8_start = week_1_start + datetime.timedelta(days=49)

				week_1_remaining = elem['week_1_remaining']
				week_2_remaining = elem['week_2_remaining']
				week_3_remaining = elem['week_3_remaining']
				week_4_remaining = elem['week_4_remaining']

				survey_1_status = elem['survey_1_status']
				survey_2_status = elem['survey_2_status']
				survey_3_status = elem['survey_3_status']
				survey_4_status = elem['survey_4_status']
				survey_5_status = elem['survey_5_status']
				survey_8_status = elem['survey_8_status']

				TOTAL_USERS.add(elem['study_id'])


				if curr_datetime > week_1_expire and week_1_remaining > 0:
					week_1_status = 'expired'
				elif curr_datetime > week_1_start and week_1_remaining <= 0:
					week_1_status = 'completed'
				elif curr_datetime > week_1_start and week_1_remaining > 0:
					week_1_status = 'active'
				else:
					week_1_status = 'TBA'

				if curr_datetime > week_2_expire and week_2_remaining > 0:
					week_2_status = 'expired'
				elif curr_datetime > week_2_start and week_2_remaining <= 0:
					week_2_status = 'completed'
				elif curr_datetime > week_2_start and week_2_remaining > 0:
					week_2_status = 'active'
				else:
					week_2_status = 'TBA'

				if curr_datetime > week_3_expire and week_3_remaining > 0:
					week_3_status = 'expired'
				elif curr_datetime > week_3_start and week_3_remaining <= 0:
					week_3_status = 'completed'
				elif curr_datetime > week_3_start and week_3_remaining > 0:
					week_3_status = 'active'
				else:
					week_3_status = 'TBA'
				
				if curr_datetime > week_4_expire and week_4_remaining > 0:
					week_4_status = 'expired'
				elif curr_datetime > week_4_start and week_4_remaining <= 0:
					week_4_status = 'completed'
				elif curr_datetime > week_4_start and week_4_remaining > 0:
					week_4_status = 'active'
				else:
					week_4_status = 'TBA'


				total_earnings = 0
				total_remaining_earnings = 0
				total_possible_earnings = 0

				week_1_earnings = 0
				week_2_earnings = 0
				week_3_earnings = 0
				week_4_earnings = 0
				week_5_earnings = 0
				week_8_earnings = 0

				if week_1_status == 'TBA' or week_1_status == 'active':
					total_possible_earnings += 5
				elif week_1_status == 'completed':
					total_earnings += 5
					week_1_earnings += 5
					total_possible_earnings += 5

				if week_2_status == 'TBA' or week_2_status == 'active':
					total_possible_earnings += 5
				elif week_2_status == 'completed':
					total_earnings += 5
					week_2_earnings += 5
					total_possible_earnings += 5

				
				if week_3_status == 'TBA' or week_3_status == 'active':
					total_possible_earnings += 5
				elif week_3_status == 'completed':
					total_earnings += 5
					week_3_earnings += 5
					total_possible_earnings += 5

				if week_4_status == 'TBA' or week_4_status == 'active':
					total_possible_earnings += 5
				elif week_4_status == 'completed':
					total_earnings += 5
					week_4_earnings += 5
					total_possible_earnings += 5

				
				if survey_1_status == 1:
					total_earnings += 5
					week_1_earnings += 5
					total_possible_earnings += 5
				else:
					total_possible_earnings += 5
				
				if survey_2_status == 1:
					total_earnings += 5
					week_2_earnings += 5
					total_possible_earnings += 5
				else:
					total_possible_earnings += 5
				
				if survey_3_status == 1:
					total_earnings += 5
					week_3_earnings += 5
					total_possible_earnings += 5
				else:
					total_possible_earnings += 5
				
				if survey_4_status == 1:
					total_earnings += 5
					week_4_earnings += 5
					total_possible_earnings += 5
				else:
					total_possible_earnings += 5
				
				if survey_5_status == 1:
					total_earnings += 10
					week_5_earnings += 10
					total_possible_earnings += 10
				else:
					total_possible_earnings += 10

				if survey_8_status == 1:
					total_earnings += 10
					week_8_earnings += 10
					total_possible_earnings += 10
				else:
					total_possible_earnings += 10

				all_users_earnings += total_earnings
				curr_week = ''
				if week_4_status == 'active' or week_4_status == 'completed':
					curr_week = 'Week 4'
				elif week_3_status == 'active' or week_3_status == 'completed':
					curr_week = 'Week 3'
				elif week_2_status == 'active' or week_2_status == 'completed':
					curr_week = 'Week 2'
				elif week_1_status == 'active' or week_1_status == 'completed':
					curr_week = 'Week 1'
				elif curr_datetime > week_5_start and curr_datetime < week_8_start:
					curr_week = 'Week 5'
				elif curr_datetime > week_8_start:
					curr_week = 'Week 8'

				if week_4_status == 'completed' or curr_week == 'Week 5' or curr_week == 'Week 8':
					USERS_WEEK_4_PLUS.add(elem['study_id'])
					week_4_users_earnings += total_earnings
					

				if week_1_status == 'completed' and week_2_status == 'completed' and week_3_status == 'completed' and week_4_status == 'completed':
					FOUR_WEEKS_COMPLETED.add(elem['study_id'])
					
					

				if (week_1_status == 'completed' and week_2_status == 'completed' and week_3_status == 'completed') or (week_2_status == 'completed' and week_3_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_3_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_2_status == 'completed' and week_4_status == 'completed'):
					THREE_WEEKS_COMPLETED.add(elem['study_id'])
				
				if (week_1_status == 'completed' and week_2_status == 'completed') or (week_2_status == 'completed' and week_3_status == 'completed') or (week_3_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_4_status == 'completed') or (week_1_status == 'completed' and week_3_status == 'completed') or (week_2_status == 'completed' and week_4_status == 'completed'):
					TWO_WEEKS_COMPLETED.add(elem['study_id'])
				
				if week_1_status == 'completed' or week_2_status == 'completed' or week_3_status == 'completed' or week_4_status == 'completed':
					ONE_WEEK_COMPLETED.add(elem['study_id'])


				if survey_1_status == 1 and survey_2_status == 1 and survey_3_status == 1 and survey_4_status == 1:
					FOUR_SURVEY_COMPLETED.add(elem['study_id'])
				
				if (survey_1_status == 1 and survey_2_status == 1 and survey_3_status == 1) or (survey_2_status == 1 and survey_3_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_3_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_2_status == 1 and survey_4_status == 1):
					THREE_SURVEY_COMPLETED.add(elem['study_id'])
				
				if (survey_1_status == 1 and survey_2_status == 1) or (survey_2_status == 1 and survey_3_status == 1) or (survey_3_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_4_status == 1) or (survey_1_status == 1 and survey_3_status == 1) or (survey_2_status == 1 and survey_4_status == 1):
					TWO_SURVEY_COMPLETED.add(elem['study_id'])
				
				if survey_1_status == 1 or survey_2_status == 1 or survey_3_status == 1 or survey_4_status == 1:
					ONE_SURVEY_COMPLETED.add(elem['study_id'])
				

				# fill 0 with ''

				if elem['week_1_use'] == 0:
					elem['week_1_use'] = ''
				if elem['week_2_use'] == 0:
					elem['week_2_use'] = ''
				if elem['week_3_use'] == 0:
					elem['week_3_use'] = ''
				if elem['week_4_use'] == 0:
					elem['week_4_use'] = ''
				if elem['survey_1_status'] == 0:
					elem['survey_1_status'] = ''
				if elem['survey_2_status'] == 0:
					elem['survey_2_status'] = ''
				if elem['survey_3_status'] == 0:
					elem['survey_3_status'] = ''
				if elem['survey_4_status'] == 0:
					elem['survey_4_status'] = ''
				if elem['survey_5_status'] == 0:
					elem['survey_5_status'] = ''
				if elem['survey_8_status'] == 0:
					elem['survey_8_status'] = ''

				if elem['condition'] == 'Pure control':
					CONDITION_0_USERS.add(elem['study_id'])
				elif elem['condition'] == 'DIY, without AI':
					CONDITION_1_USERS.add(elem['study_id'])
				elif elem['condition'] == 'DIY, with AI':
					CONDITION_2_USERS.add(elem['study_id'])

				try:
					week_1_use = int(elem['week_1_use'])
				except:
					week_1_use = 0
				
				try:
					week_2_use = int(elem['week_2_use'])
				except:
					week_2_use = 0
				
				try:
					week_3_use = int(elem['week_3_use'])
				except:
					week_3_use = 0
				
				try:
					week_4_use = int(elem['week_4_use'])
				except:
					week_4_use = 0

				TOOL_USAGE[elem['study_id']] = week_1_use + week_2_use + week_3_use + week_4_use
				
				# 'w1', 'w2', 'w3', 'w4', 'w5', 'w8'

				# 'w1_paid', 'w1_amt', 'pay_date_w1', 'w2_paid', 'w2_amt', 'pay_date_w2', 'w3_paid', 'w3_amt', 'pay_date_w3', 'w4_paid', 'w4_amt', 'pay_date_w4', 'w5_paid', 'w5_amt', 'pay_date_w5', 'w8_paid', 'w8_amt', 'pay_date_w8'

				if int(elem['study_id']) == 1393:
					# set all earnings to 0

					total_earnings = 0
					week_1_earnings = 0
					week_2_earnings = 0
					week_3_earnings = 0
					week_4_earnings = 0
					week_5_earnings = 0
					week_8_earnings = 0
					
					 

				curr_data = [cnt, elem['study_id'], elem['date_started'], elem['condition'], total_earnings, curr_week, elem['week_1_use'], elem['survey_1_status'], elem['week_2_use'], elem['survey_2_status'], elem['week_3_use'], elem['survey_3_status'], elem['week_4_use'], elem['survey_4_status'], elem['survey_5_status'], elem['survey_8_status'], elem['w1'], elem['w1_paid'], elem['w1_amt'], elem['pay_date_w1'], elem['w2'], elem['w2_paid'], elem['w2_amt'], elem['pay_date_w2'], elem['w3'], elem['w3_paid'], elem['w3_amt'], elem['pay_date_w3'], elem['w4'], elem['w4_paid'], elem['w4_amt'], elem['pay_date_w4'], elem['w5'], elem['w5_paid'], elem['w5_amt'], elem['pay_date_w5'], elem['w8'], elem['w8_paid'], elem['w8_amt'], elem['pay_date_w8'], week_1_earnings, week_2_earnings, week_3_earnings, week_4_earnings, week_5_earnings, week_8_earnings, total_possible_earnings, elem['week_1_remaining'], elem['week_2_remaining'], elem['week_3_remaining'], elem['week_4_remaining'], week_1_status, week_2_status, week_3_status, week_4_status, elem['survey_1_status'], elem['survey_2_status'], elem['survey_3_status'], elem['survey_4_status'], elem['survey_5_status'], elem['survey_8_status']]

				data.append(curr_data)

				cnt += 1

			print('TOTAL_USERS:', len(TOTAL_USERS))
			print('USERS_WEEK_4_PLUS:', len(USERS_WEEK_4_PLUS))
			print('ONE_WEEK_COMPLETED:', len(ONE_WEEK_COMPLETED))
			print('TWO_WEEKS_COMPLETED:', len(TWO_WEEKS_COMPLETED))
			print('THREE_WEEKS_COMPLETED:', len(THREE_WEEKS_COMPLETED))
			print('FOUR_WEEKS_COMPLETED:', len(FOUR_WEEKS_COMPLETED))

			print('week_4_users_earnings:', week_4_users_earnings)

			print('all_users_earnings:', all_users_earnings)

			# 1290

			print('CONDITION_0_USERS:', len(CONDITION_0_USERS))
			print('CONDITION_1_USERS:', len(CONDITION_1_USERS))
			print('CONDITION_2_USERS:', len(CONDITION_2_USERS))

			# Condition users week_4_plus
			print('CONDITION_0_USERS-WEEK4_PLUS:', len(CONDITION_0_USERS.intersection(USERS_WEEK_4_PLUS)))
			print('CONDITION_1_USERS-WEEK4_PLUS:', len(CONDITION_1_USERS.intersection(USERS_WEEK_4_PLUS)))
			print('CONDITION_2_USERS-WEEK4_PLUS:', len(CONDITION_2_USERS.intersection(USERS_WEEK_4_PLUS)))



			print('FOUR_WEEKS_COMPLETED:', (FOUR_WEEKS_COMPLETED))
			print('USERS_WEEK_4_PLUS:', (USERS_WEEK_4_PLUS))

			ONE_WEEK_COMPLETED = ONE_WEEK_COMPLETED.intersection(USERS_WEEK_4_PLUS)
			TWO_WEEKS_COMPLETED = TWO_WEEKS_COMPLETED.intersection(USERS_WEEK_4_PLUS)
			THREE_WEEKS_COMPLETED = THREE_WEEKS_COMPLETED.intersection(USERS_WEEK_4_PLUS)
			FOUR_WEEKS_COMPLETED = FOUR_WEEKS_COMPLETED.intersection(USERS_WEEK_4_PLUS)

			CONDITION_0_USERS = CONDITION_0_USERS.intersection(USERS_WEEK_4_PLUS)
			CONDITION_1_USERS = CONDITION_1_USERS.intersection(USERS_WEEK_4_PLUS)
			CONDITION_2_USERS = CONDITION_2_USERS.intersection(USERS_WEEK_4_PLUS)


			ONE_SURVEY_COMPLETED = ONE_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)
			TWO_SURVEY_COMPLETED = TWO_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)
			THREE_SURVEY_COMPLETED = THREE_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)
			FOUR_SURVEY_COMPLETED = FOUR_SURVEY_COMPLETED.intersection(USERS_WEEK_4_PLUS)


			# condition-wise completed
			# print('Pure Control -- ONE_WEEK_COMPLETED:', len(CONDITION_0_USERS.intersection(ONE_WEEK_COMPLETED)))
			print('DIY, Without AI -- ONE_WEEK_COMPLETED:', len(CONDITION_1_USERS.intersection(ONE_WEEK_COMPLETED)), len(CONDITION_1_USERS.intersection(ONE_WEEK_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- ONE_WEEK_COMPLETED:', len(CONDITION_2_USERS.intersection(ONE_WEEK_COMPLETED)), len(CONDITION_2_USERS.intersection(ONE_WEEK_COMPLETED)) * 100 / len(CONDITION_2_USERS))

			# print('Pure Control -- TWO_WEEKS_COMPLETED:', len(CONDITION_0_USERS.intersection(TWO_WEEKS_COMPLETED)))
			print('DIY, Without AI -- TWO_WEEKS_COMPLETED:', len(CONDITION_1_USERS.intersection(TWO_WEEKS_COMPLETED)), len(CONDITION_1_USERS.intersection(TWO_WEEKS_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- TWO_WEEKS_COMPLETED:', len(CONDITION_2_USERS.intersection(TWO_WEEKS_COMPLETED)), len(CONDITION_2_USERS.intersection(TWO_WEEKS_COMPLETED)) * 100 / len(CONDITION_2_USERS))

			# print('Pure Control -- THREE_WEEKS_COMPLETED:', len(CONDITION_0_USERS.intersection(THREE_WEEKS_COMPLETED)))
			print('DIY, Without AI -- THREE_WEEKS_COMPLETED:', len(CONDITION_1_USERS.intersection(THREE_WEEKS_COMPLETED)), len(CONDITION_1_USERS.intersection(THREE_WEEKS_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- THREE_WEEKS_COMPLETED:', len(CONDITION_2_USERS.intersection(THREE_WEEKS_COMPLETED)), len(CONDITION_2_USERS.intersection(THREE_WEEKS_COMPLETED)) * 100 / len(CONDITION_2_USERS))

			# print('Pure Control -- FOUR_WEEKS_COMPLETED:', len(CONDITION_0_USERS.intersection(FOUR_WEEKS_COMPLETED)))
			print('DIY, Without AI -- FOUR_WEEKS_COMPLETED:', len(CONDITION_1_USERS.intersection(FOUR_WEEKS_COMPLETED)), len(CONDITION_1_USERS.intersection(FOUR_WEEKS_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- FOUR_WEEKS_COMPLETED:', len(CONDITION_2_USERS.intersection(FOUR_WEEKS_COMPLETED)), len(CONDITION_2_USERS.intersection(FOUR_WEEKS_COMPLETED)) * 100 / len(CONDITION_2_USERS))


			# condition-wise completed
			# print('Pure Control -- ONE_SURVEY_COMPLETED:', len(CONDITION_0_USERS.intersection(ONE_SURVEY_COMPLETED)))
			print('DIY, Without AI -- ONE_SURVEY_COMPLETED:', len(CONDITION_1_USERS.intersection(ONE_SURVEY_COMPLETED)), len(CONDITION_1_USERS.intersection(ONE_SURVEY_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- ONE_SURVEY_COMPLETED:', len(CONDITION_2_USERS.intersection(ONE_SURVEY_COMPLETED)), len(CONDITION_2_USERS.intersection(ONE_SURVEY_COMPLETED)) * 100 / len(CONDITION_2_USERS))

			# print('Pure Control -- TWO_SURVEY_COMPLETED:', len(CONDITION_0_USERS.intersection(TWO_SURVEY_COMPLETED)))
			print('DIY, Without AI -- TWO_SURVEY_COMPLETED:', len(CONDITION_1_USERS.intersection(TWO_SURVEY_COMPLETED)), len(CONDITION_1_USERS.intersection(TWO_SURVEY_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- TWO_SURVEY_COMPLETED:', len(CONDITION_2_USERS.intersection(TWO_SURVEY_COMPLETED)), len(CONDITION_2_USERS.intersection(TWO_SURVEY_COMPLETED)) * 100 / len(CONDITION_2_USERS))

			# print('Pure Control -- THREE_SURVEY_COMPLETED:', len(CONDITION_0_USERS.intersection(THREE_SURVEY_COMPLETED))
			print('DIY, Without AI -- THREE_SURVEY_COMPLETED:', len(CONDITION_1_USERS.intersection(THREE_SURVEY_COMPLETED)), len(CONDITION_1_USERS.intersection(THREE_SURVEY_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- THREE_SURVEY_COMPLETED:', len(CONDITION_2_USERS.intersection(THREE_SURVEY_COMPLETED)), len(CONDITION_2_USERS.intersection(THREE_SURVEY_COMPLETED)) * 100 / len(CONDITION_2_USERS))

			# print('Pure Control -- FOUR_SURVEY_COMPLETED:', len(CONDITION_0_USERS.intersection(FOUR_SURVEY_COMPLETED)))
			print('DIY, Without AI -- FOUR_SURVEY_COMPLETED:', len(CONDITION_1_USERS.intersection(FOUR_SURVEY_COMPLETED)), len(CONDITION_1_USERS.intersection(FOUR_SURVEY_COMPLETED)) * 100 / len(CONDITION_1_USERS))
			print('DIY, With AI -- FOUR_SURVEY_COMPLETED:', len(CONDITION_2_USERS.intersection(FOUR_SURVEY_COMPLETED)), len(CONDITION_2_USERS.intersection(FOUR_SURVEY_COMPLETED)) * 100 / len(CONDITION_2_USERS))


			CONDITION_1_USAGE = []
			for elem in CONDITION_1_USERS:
				CONDITION_1_USAGE.append(TOOL_USAGE[elem])
			
			CONDITION_2_USAGE = []
			for elem in CONDITION_2_USERS:
				CONDITION_2_USAGE.append(TOOL_USAGE[elem])

			print('CONDITION_1_USAGE:', np.mean(CONDITION_1_USAGE))
			print('CONDITION_2_USAGE:', np.mean(CONDITION_2_USAGE))


			# condition wise

			return render(request, "study/admin_dashboard.html", {'data': data, 'code': code})
		else:
			return redirect('/study/error.html', {'error_msg': 'Error'})
	else:
		return redirect('/study/admin.html')

# compute cohen's d

def cohen_d(y,x):
	nx = len(x)
	ny = len(y)
	dof = nx + ny - 2
	cd = (x.mean() - y.mean()) / np.sqrt(((nx-1)*x.var() + (ny-1)*y.var()) / dof)

	# abs diff b/w means
	abs_diff = x.mean() - y.mean()

	# relative diff b/w means
	rel_diff = abs_diff*100.0 / y.mean()

	return [round(cd, 4), round(abs_diff, 4), round(rel_diff, 4)]



def compute_current_week_no(username):
	# compute current week num for the user
	curr_date = datetime.datetime.now().astimezone(timezone('US/Pacific'))

	# get date_started from UserDetails
	date_started = UserDetails.objects.filter(username = username)[0].week_1_start

	# compute week_no
	week_no = (curr_date - date_started).days // 7 + 1

	return week_no


def user_baseline_survey_outcomes():
	fields = {
		'token': RECAP_API_TOKEN,
		'content': 'record',
		'format': 'json',
		'type': 'flat'
	}
	

	r = requests.post('https://redcap.iths.org/api/',data=fields)
	records = eval(r.text)

	for record in records:
		# get col values
		study_id = record['study_id']
		redcap_event_name = record['redcap_event_name']
		n8m95 = record['n8m95']
		# welcome_landing_page_complete = record['welcome_landing_page_complete']
		# trigger_consent = '' # record['trigger_consent']
		condition = record['usage']
		date_consent = record['date_consent']


def statistics(request):
	if request.method == 'POST':

		code = request.POST.get('code', None)

		if code == '3895':
			TOTAL_USERS, USERS_WEEK_4_PLUS, ONE_WEEK_COMPLETED, TWO_WEEKS_COMPLETED, THREE_WEEKS_COMPLETED, FOUR_WEEKS_COMPLETED, CONDITION_0_USERS, CONDITION_1_USERS, CONDITION_2_USERS, ONE_SURVEY_COMPLETED, TWO_SURVEY_COMPLETED, THREE_SURVEY_COMPLETED, FOUR_SURVEY_COMPLETED, TOOL_USAGE = get_users()


			PHQ9_BASELINE = {}
			PHQ9_WEEK_1 = {}
			PHQ9_WEEK_2 = {}
			PHQ9_WEEK_3 = {}
			PHQ9_WEEK_4 = {}
			PHQ9_WEEK_5 = {}
			PHQ9_WEEK_8 = {}

			PHQ9_Q1_BASELINE = {}
			PHQ9_Q1_WEEK_1 = {}
			PHQ9_Q1_WEEK_2 = {}
			PHQ9_Q1_WEEK_3 = {}
			PHQ9_Q1_WEEK_4 = {}
			PHQ9_Q1_WEEK_5 = {}
			PHQ9_Q1_WEEK_8 = {}

			PHQ9_Q2_BASELINE = {}
			PHQ9_Q2_WEEK_1 = {}
			PHQ9_Q2_WEEK_2 = {}
			PHQ9_Q2_WEEK_3 = {}
			PHQ9_Q2_WEEK_4 = {}
			PHQ9_Q2_WEEK_5 = {}
			PHQ9_Q2_WEEK_8 = {}

			PHQ9_Q3_BASELINE = {}
			PHQ9_Q3_WEEK_1 = {}
			PHQ9_Q3_WEEK_2 = {}
			PHQ9_Q3_WEEK_3 = {}
			PHQ9_Q3_WEEK_4 = {}
			PHQ9_Q3_WEEK_5 = {}
			PHQ9_Q3_WEEK_8 = {}

			PHQ9_Q4_BASELINE = {}
			PHQ9_Q4_WEEK_1 = {}
			PHQ9_Q4_WEEK_2 = {}
			PHQ9_Q4_WEEK_3 = {}
			PHQ9_Q4_WEEK_4 = {}
			PHQ9_Q4_WEEK_5 = {}
			PHQ9_Q4_WEEK_8 = {}

			PHQ9_Q5_BASELINE = {}
			PHQ9_Q5_WEEK_1 = {}
			PHQ9_Q5_WEEK_2 = {}
			PHQ9_Q5_WEEK_3 = {}
			PHQ9_Q5_WEEK_4 = {}
			PHQ9_Q5_WEEK_5 = {}
			PHQ9_Q5_WEEK_8 = {}

			PHQ9_Q6_BASELINE = {}
			PHQ9_Q6_WEEK_1 = {}
			PHQ9_Q6_WEEK_2 = {}
			PHQ9_Q6_WEEK_3 = {}
			PHQ9_Q6_WEEK_4 = {}
			PHQ9_Q6_WEEK_5 = {}
			PHQ9_Q6_WEEK_8 = {}

			PHQ9_Q7_BASELINE = {}
			PHQ9_Q7_WEEK_1 = {}
			PHQ9_Q7_WEEK_2 = {}
			PHQ9_Q7_WEEK_3 = {}
			PHQ9_Q7_WEEK_4 = {}
			PHQ9_Q7_WEEK_5 = {}
			PHQ9_Q7_WEEK_8 = {}

			PHQ9_Q8_BASELINE = {}
			PHQ9_Q8_WEEK_1 = {}
			PHQ9_Q8_WEEK_2 = {}
			PHQ9_Q8_WEEK_3 = {}
			PHQ9_Q8_WEEK_4 = {}
			PHQ9_Q8_WEEK_5 = {}
			PHQ9_Q8_WEEK_8 = {}

			PHQ9_Q9_BASELINE = {}
			PHQ9_Q9_WEEK_1 = {}
			PHQ9_Q9_WEEK_2 = {}
			PHQ9_Q9_WEEK_3 = {}
			PHQ9_Q9_WEEK_4 = {}
			PHQ9_Q9_WEEK_5 = {}
			PHQ9_Q9_WEEK_8 = {}

			GAD7_BASELINE = {}
			GAD7_WEEK_1 = {}
			GAD7_WEEK_2 = {}
			GAD7_WEEK_3 = {}
			GAD7_WEEK_4 = {}
			GAD7_WEEK_5 = {}
			GAD7_WEEK_8 = {}

			GAD7_Q1_BASELINE = {}
			GAD7_Q1_WEEK_1 = {}
			GAD7_Q1_WEEK_2 = {}
			GAD7_Q1_WEEK_3 = {}
			GAD7_Q1_WEEK_4 = {}
			GAD7_Q1_WEEK_5 = {}
			GAD7_Q1_WEEK_8 = {}

			GAD7_Q2_BASELINE = {}
			GAD7_Q2_WEEK_1 = {}
			GAD7_Q2_WEEK_2 = {}
			GAD7_Q2_WEEK_3 = {}
			GAD7_Q2_WEEK_4 = {}
			GAD7_Q2_WEEK_5 = {}
			GAD7_Q2_WEEK_8 = {}

			GAD7_Q3_BASELINE = {}
			GAD7_Q3_WEEK_1 = {}
			GAD7_Q3_WEEK_2 = {}
			GAD7_Q3_WEEK_3 = {}
			GAD7_Q3_WEEK_4 = {}
			GAD7_Q3_WEEK_5 = {}
			GAD7_Q3_WEEK_8 = {}

			GAD7_Q4_BASELINE = {}
			GAD7_Q4_WEEK_1 = {}
			GAD7_Q4_WEEK_2 = {}
			GAD7_Q4_WEEK_3 = {}
			GAD7_Q4_WEEK_4 = {}
			GAD7_Q4_WEEK_5 = {}
			GAD7_Q4_WEEK_8 = {}

			GAD7_Q5_BASELINE = {}
			GAD7_Q5_WEEK_1 = {}
			GAD7_Q5_WEEK_2 = {}
			GAD7_Q5_WEEK_3 = {}
			GAD7_Q5_WEEK_4 = {}
			GAD7_Q5_WEEK_5 = {}
			GAD7_Q5_WEEK_8 = {}

			GAD7_Q6_BASELINE = {}
			GAD7_Q6_WEEK_1 = {}
			GAD7_Q6_WEEK_2 = {}
			GAD7_Q6_WEEK_3 = {}
			GAD7_Q6_WEEK_4 = {}
			GAD7_Q6_WEEK_5 = {}
			GAD7_Q6_WEEK_8 = {}

			GAD7_Q7_BASELINE = {}
			GAD7_Q7_WEEK_1 = {}
			GAD7_Q7_WEEK_2 = {}
			GAD7_Q7_WEEK_3 = {}
			GAD7_Q7_WEEK_4 = {}
			GAD7_Q7_WEEK_5 = {}
			GAD7_Q7_WEEK_8 = {}



			HOPE_BASELINE = {}
			HOPE_WEEK_1 = {}
			HOPE_WEEK_2 = {}
			HOPE_WEEK_3 = {}
			HOPE_WEEK_4 = {}
			HOPE_WEEK_5 = {}
			HOPE_WEEK_8 = {}

			EM_1_BASELINE = {}
			EM_1_WEEK_1 = {}
			EM_1_WEEK_2 = {}
			EM_1_WEEK_3 = {}
			EM_1_WEEK_4 = {}
			EM_1_WEEK_5 = {}
			EM_1_WEEK_8 = {}

			EM_2_BASELINE = {}
			EM_2_WEEK_1 = {}
			EM_2_WEEK_2 = {}
			EM_2_WEEK_3 = {}
			EM_2_WEEK_4 = {}
			EM_2_WEEK_5 = {}

			EM_3_BASELINE = {}
			EM_3_WEEK_1 = {}
			EM_3_WEEK_2 = {}
			EM_3_WEEK_3 = {}
			EM_3_WEEK_4 = {}
			EM_3_WEEK_5 = {}

			EM_4_BASELINE = {}
			EM_4_WEEK_1 = {}
			EM_4_WEEK_2 = {}
			EM_4_WEEK_3 = {}
			EM_4_WEEK_4 = {}
			EM_4_WEEK_5 = {}

			EM_5_BASELINE = {}
			EM_5_WEEK_1 = {}
			EM_5_WEEK_2 = {}
			EM_5_WEEK_3 = {}
			EM_5_WEEK_4 = {}
			EM_5_WEEK_5 = {}

			EM_6_BASELINE = {}
			EM_6_WEEK_1 = {}
			EM_6_WEEK_2 = {}
			EM_6_WEEK_3 = {}
			EM_6_WEEK_4 = {}
			EM_6_WEEK_5 = {}

			CCTS_20_BASELINE = {}
			CCTS_20_WEEK_1 = {}
			CCTS_20_WEEK_2 = {}
			CCTS_20_WEEK_3 = {}
			CCTS_20_WEEK_4 = {}
			CCTS_20_WEEK_5 = {}
			CCTS_20_WEEK_8 = {}

			CCTS_28_BASELINE = {}
			CCTS_28_WEEK_1 = {}
			CCTS_28_WEEK_2 = {}
			CCTS_28_WEEK_3 = {}
			CCTS_28_WEEK_4 = {}
			CCTS_28_WEEK_5 = {}
			CCTS_28_WEEK_8 = {}

			CCTS_21_BASELINE = {}
			CCTS_21_WEEK_1 = {}
			CCTS_21_WEEK_2 = {}
			CCTS_21_WEEK_3 = {}
			CCTS_21_WEEK_4 = {}
			CCTS_21_WEEK_5 = {}
			CCTS_21_WEEK_8 = {}

			CCTS_06_BASELINE = {}
			CCTS_06_WEEK_1 = {}
			CCTS_06_WEEK_2 = {}
			CCTS_06_WEEK_3 = {}
			CCTS_06_WEEK_4 = {}
			CCTS_06_WEEK_5 = {}
			CCTS_06_WEEK_8 = {}

			CCTS_24_BASELINE = {}
			CCTS_24_WEEK_1 = {}
			CCTS_24_WEEK_2 = {}
			CCTS_24_WEEK_3 = {}
			CCTS_24_WEEK_4 = {}
			CCTS_24_WEEK_5 = {}
			CCTS_24_WEEK_8 = {}

			CCTS_11_BASELINE = {}
			CCTS_11_WEEK_1 = {}
			CCTS_11_WEEK_2 = {}
			CCTS_11_WEEK_3 = {}
			CCTS_11_WEEK_4 = {}
			CCTS_11_WEEK_5 = {}
			CCTS_11_WEEK_8 = {}

			CCTS_ELAB_BASELINE = {}
			CCTS_ELAB_WEEK_1 = {}
			CCTS_ELAB_WEEK_2 = {}
			CCTS_ELAB_WEEK_3 = {}
			CCTS_ELAB_WEEK_4 = {}
			CCTS_ELAB_WEEK_5 = {}
			CCTS_ELAB_WEEK_8 = {}	

			CCTS_WELLBEING_BASELINE = {}
			CCTS_WELLBEING_WEEK_1 = {}
			CCTS_WELLBEING_WEEK_2 = {}
			CCTS_WELLBEING_WEEK_3 = {}
			CCTS_WELLBEING_WEEK_4 = {}
			CCTS_WELLBEING_WEEK_5 = {}
			CCTS_WELLBEING_WEEK_8 = {}

			CCTS_OTHER_BASELINE = {}
			CCTS_OTHER_WEEK_1 = {}
			CCTS_OTHER_WEEK_2 = {}
			CCTS_OTHER_WEEK_3 = {}
			CCTS_OTHER_WEEK_4 = {}
			CCTS_OTHER_WEEK_5 = {}
			CCTS_OTHER_WEEK_8 = {}


			# therapy":"2","talk":"3","seekmh":"3","practice_cr":"4","excite_mhskill":"6","life_impact

			THERAPY_BASELINE = {}
			TALK_BASELINE = {}
			SEEK_MH_BASELINE = {}
			PRACTICE_CR_BASELINE = {}
			EXCITE_MHSKILL_BASELINE = {}
			LIFE_IMPACT_BASELINE = {}

			RECAP_API_TOKEN = os.environ.get('RECAP_API_TOKEN')

			fields = {
				'token': RECAP_API_TOKEN,
				'content': 'record',
				'format': 'json',
				'type': 'flat'
			}

			r = requests.post('https://redcap.iths.org/api/',data=fields)
			records = eval(r.text)

			for record in records:
				# get col values
				study_id = record['study_id']
				redcap_event_name = record['redcap_event_name']
				n8m95 = record['n8m95']
				# welcome_landing_page_complete = record['welcome_landing_page_complete']
				# trigger_consent = '' # record['trigger_consent']
				condition = record['usage']
				date_consent = record['date_consent']
				# start_date = record['start_date']
				# stop_1 = record['stop___1']
				# test = record['test']
				# admin_complete = record['admin_complete']
				# comms_log = record['comms_log']
				# withdraw = record['withdraw']
				# date_withdraw = record['date_withdraw']
				# notes_withdraw = record['notes_withdraw']
				# events_log_complete = record['events_log_complete']
				consent_yn = record['consent_yn']
				consent_complete = record['consent_complete']
				# psychoed_complete = '' # record['psychoed_complete']
				# age = record['age']
				# us_res = record['us_res']
				# first_name = record['first_name']
				# last_name = record['last_name']
				email = record['email']
				# contact_pref = record['contact_pref']
				# phone = record['phone']
				# entry_survey_complete = record['entry_survey_complete']
				phq_1 = record['phq_1']
				phq_2 = record['phq_2']
				phq_3 = record['phq_3']
				phq_4 = record['phq_4']
				phq_5 = record['phq_5']
				phq_6 = record['phq_6']
				phq_7 = record['phq_7']
				phq_8 = record['phq_8']
				phq_9 = record['phq_9']
				# phq_calc_1 = record['phq_calc_1']
				# phq_calc_2 = record['phq_calc_2']
				# phq_calc_3 = record['phq_calc_3']
				# phq_calc_4 = record['phq_calc_4']
				# phq_calc_5 = record['phq_calc_5']
				# phq_calc_6 = record['phq_calc_6']
				# phq_calc_7 = record['phq_calc_7']
				# phq_calc_8 = record['phq_calc_8']
				# phq_calc_9 = record['phq_calc_9']
				# phq_answered = record['phq_answered']
				phq_total = record['phq_total']
				# phq_difficult = record['phq_difficult']
				phq9_complete = record['phq9_complete']
				gad7_q1 = record['gad7_q1']
				gad7_q2 = record['gad7_q2']
				gad7_q3 = record['gad7_q3']
				gad7_q4 = record['gad7_q4']
				gad7_q5 = record['gad7_q5']
				gad7_q6 = record['gad7_q6']
				gad7_q7 = record['gad7_q7']
				gad7_total = record['gad7_total']
				# gad7_q8 = record['gad7_q8']
				gad7_complete = record['gad7_complete']
				# cr_use_q = record['cr_use_q']
				# cr_use_complete = record['cr_use_complete']
				hope_q = record['hope_q']
				hope_complete = record['hope_complete']


				# week_1_arm_1
				# phq9_complete
				# gad7_complete
				# hope_complete
				# em_complete
				# ccts_complete
				em_1 = record['em_1']
				em_2 = record['em_2']
				em_3 = record['em_3']
				em_4 = record['em_4']
				em_5 = record['em_5']
				em_6 = record['em_6']
				em_complete = record['em_complete']
				ccts_20 = record['ccts_20']
				ccts_28 = record['ccts_28']
				ccts_21 = record['ccts_21']
				ccts_06 = record['ccts_06']
				ccts_24 = record['ccts_24']
				ccts_11 = record['ccts_11']
				ccts_elab = record['ccts_elab']
				ccts_wellbeing = record['ccts_wellbeing']
				ccts_other = record['ccts_other']
				ccts_complete = record['ccts_complete']
				# impact_diy = record['impact_diy']
				# use_diy = record['use_diy']
				# impact_y_diy = record['impact_y_diy']
				# impact_n_diy = record['impact_n_diy']
				# apply_diy = record['apply_diy']
				# apply_y_diy = record['apply_y_diy']
				# benefit_diy = record['benefit_diy']
				# benefit_y_diy = record['benefit_y_diy']
				# takeaways_diy = record['takeaways_diy']
				# future_diy = record['future_diy']
				# change_diy = record['change_diy']
				# like_diy = record['like_diy']
				# dislike_diy = record['dislike_diy']
				exit_complete = record['exit_complete']
				# ther_yn = record['ther_yn']
				# mhmeds_yn = record['mhmeds_yn']
				# therapy_post_diy = record['therapy_post_diy']
				
				miscq_complete = record['miscq_complete']
				# post_1 = record['post_1']
				# post_2 = record['post_2']
				# post_3 = record['post_3']
				# post_4 = record['post_4']
				# post_5 = record['post_5']
				# post_6 = record['post_6']
				# post_7 = record['post_7']
				# post_diy_complete = record['post_diy_complete']
				# tool_1 = record['tool_1']
				# tool_2 = record['tool_2']
				# tool_3 = record['tool_3']
				# tool_4 = record['tool_4']
				# tool_5 = record['tool_5']
				# tool_use_complete = record['tool_use_complete']

				if study_id != '' and int(study_id) < 70:
					continue

				study_id = int(study_id)

				if redcap_event_name == 'baseline_arm_1' and miscq_complete == '2' and email != '':
					# {"study_id":"25","redcap_event_name":"baseline_arm_1","n8m95":"","welcome_landing_page_complete":"2","status":"1","condition":"2","start_date":"2023-11-03","stop___1":"0","test":"","admin_complete":"2","comms_log":"","withdraw":"","date_withdraw":"","notes_withdraw":"","events_log_complete":"","consent_yn":"","consent_complete":"","psychoed_reminder_complete":"","tool_use_reminder_complete":"","age":"27","us_res":"1","first_name":"Ashish","last_name":"Sharma","email":"ashshar+4@uw.edu","contact_pref":"SMS_INVITE_WEB","phone":"(206) 596-6812","entry_survey_complete":"2","phq_1":"3","phq_2":"3","phq_3":"2","phq_4":"2","phq_5":"2","phq_6":"2","phq_7":"2","phq_8":"3","phq_9":"2","phq_calc_1":"1","phq_calc_2":"1","phq_calc_3":"1","phq_calc_4":"1","phq_calc_5":"1","phq_calc_6":"1","phq_calc_7":"1","phq_calc_8":"1","phq_calc_9":"1","phq_answered":"9","phq_total":"21","phq_difficult":"1","phq9_complete":"2","gad7_q1":"1","gad7_q2":"0","gad7_q3":"0","gad7_q4":"0","gad7_q5":"0","gad7_q6":"0","gad7_q7":"1","gad7_total":"2","gad7_q8":"2","gad7_complete":"2","cr_use_q":"1","cr_use_complete":"2","hope_q":"3","hope_complete":"2","em_1":"","em_2":"","em_3":"","em_4":"","em_5":"","em_6":"","em_complete":"","ccts_20":"","ccts_28":"","ccts_21":"","ccts_06":"","ccts_24":"","ccts_11":"","ccts_elab":"","ccts_wellbeing":"","ccts_other":"","ccts_complete":"","impact_diy":"","use_diy":"","impact_y_diy":"","impact_n_diy":"","apply_diy":"","apply_y_diy":"","benefit_diy":"","benefit_y_diy":"","takeaways_diy":"","future_diy":"","change_diy":"","like_diy":"","dislike_diy":"","exit_complete":"","ther_yn":"0","mhmeds_yn":"1","therapy_post_diy":"","therapy":"2","talk":"3","seekmh":"3","practice_cr":"4","excite_mhskill":"6","life_impact":"3","miscq_complete":"2","post_1":"","post_2":"","post_3":"","post_4":"","post_5":"","post_6":"","post_7":"","post_diy_complete":"","tool_1":"","tool_2":"","tool_3":"","tool_4":"","tool_5":"","tool_use_complete":""},

					therapy = record['therapy_post_diy']
					talk = record['talk']
					seekmh = record['seekmh']
					# practice_cr = record['practice_cr']
					# excite_mhskill = record['excite_mhskill']
					# life_impact = record['life_impact']

					try:
						PHQ9_BASELINE[study_id] = int(phq_total)
					except:
						PHQ9_BASELINE[study_id] = None
						
					try:
						PHQ9_Q1_BASELINE[study_id] = int(phq_1)
					except:
						PHQ9_Q1_BASELINE[study_id] = None

						
					try:
						PHQ9_Q2_BASELINE[study_id] = int(phq_2)
					except:
						PHQ9_Q2_BASELINE[study_id] = None

					try:
						PHQ9_Q3_BASELINE[study_id] = int(phq_3)
					except:
						PHQ9_Q3_BASELINE[study_id] = None


					try:
						PHQ9_Q4_BASELINE[study_id] = int(phq_4)
					except:
						PHQ9_Q4_BASELINE[study_id] = None

					try:
						PHQ9_Q5_BASELINE[study_id] = int(phq_5)
					except:
						PHQ9_Q5_BASELINE[study_id] = None

					try:
						PHQ9_Q6_BASELINE[study_id] = int(phq_6)
					except:
						PHQ9_Q6_BASELINE[study_id] = None
					
					try:
						PHQ9_Q7_BASELINE[study_id] = int(phq_7)	
					except:
						PHQ9_Q7_BASELINE[study_id] = None

					try:
						PHQ9_Q8_BASELINE[study_id] = int(phq_8)
					except:
						PHQ9_Q8_BASELINE[study_id] = None
					
					try:
						PHQ9_Q9_BASELINE[study_id] = int(phq_9)
					except:
						PHQ9_Q9_BASELINE[study_id] = None


					try:
						GAD7_BASELINE[study_id] = int(gad7_total)
					except:
						GAD7_BASELINE[study_id] = None

					try:
						GAD7_Q1_BASELINE[study_id] = int(gad7_q1)
					except:
						GAD7_Q1_BASELINE[study_id] = None

					try:
						GAD7_Q2_BASELINE[study_id] = int(gad7_q2)
					except:
						GAD7_Q2_BASELINE[study_id] = None

					try:
						GAD7_Q3_BASELINE[study_id] = int(gad7_q3)
					except:
						GAD7_Q3_BASELINE[study_id] = None

					try:
						GAD7_Q4_BASELINE[study_id] = int(gad7_q4)
					except:
						GAD7_Q4_BASELINE[study_id] = None

					try:
						GAD7_Q5_BASELINE[study_id] = int(gad7_q5)
					except:
						GAD7_Q5_BASELINE[study_id] = None

					try:
						GAD7_Q6_BASELINE[study_id] = int(gad7_q6)
					except:
						GAD7_Q6_BASELINE[study_id] = None
					
					try:
						GAD7_Q7_BASELINE[study_id] = int(gad7_q7)
					except:
						GAD7_Q7_BASELINE[study_id] = None

					try:
						HOPE_BASELINE[study_id] = int(hope_q)
					except:
						HOPE_BASELINE[study_id] = None

					# therapy":"2","talk":"3","seekmh":"3","practice_cr":"4","excite_mhskill":"6","life_impact
						
					try:
						
						THERAPY_BASELINE[study_id] = int(therapy)
					except:
						THERAPY_BASELINE[study_id] = None

					try:
						TALK_BASELINE[study_id] = int(talk)
					except:
						TALK_BASELINE[study_id] = None
					
					try:
						SEEK_MH_BASELINE[study_id] = int(seekmh)
					except:
						SEEK_MH_BASELINE[study_id] = None
					
					# try:
					# 	PRACTICE_CR_BASELINE[study_id] = int(practice_cr)
					# except:
					# 	PRACTICE_CR_BASELINE[study_id] = None
					
					# try:
					# 	EXCITE_MHSKILL_BASELINE[study_id] = int(excite_mhskill)
					# except:
					# 	EXCITE_MHSKILL_BASELINE[study_id] = None
					
					# try:
					# 	LIFE_IMPACT_BASELINE[study_id] = int(life_impact)
					# except:
					# 	LIFE_IMPACT_BASELINE[study_id] = None


				if redcap_event_name == 'week_1_arm_1' and phq9_complete == '2' and gad7_complete == '2' and hope_complete == '2' and em_complete == '2' and ccts_complete == '2' and study_id != '':
					# print(study_id)

					try:
						PHQ9_WEEK_1[study_id] = int(phq_total)
					except:
						PHQ9_WEEK_1[study_id] = None
						
					try:
						PHQ9_Q1_WEEK_1[study_id] = int(phq_1)
					except:
						PHQ9_Q1_WEEK_1[study_id] = None

						
					try:
						PHQ9_Q2_WEEK_1[study_id] = int(phq_2)
					except:
						PHQ9_Q2_WEEK_1[study_id] = None

					try:
						PHQ9_Q3_WEEK_1[study_id] = int(phq_3)
					except:
						PHQ9_Q3_WEEK_1[study_id] = None


					try:
						PHQ9_Q4_WEEK_1[study_id] = int(phq_4)
					except:
						PHQ9_Q4_WEEK_1[study_id] = None

					try:
						PHQ9_Q5_WEEK_1[study_id] = int(phq_5)
					except:
						PHQ9_Q5_WEEK_1[study_id] = None

					try:
						PHQ9_Q6_WEEK_1[study_id] = int(phq_6)
					except:
						PHQ9_Q6_WEEK_1[study_id] = None
					
					try:
						PHQ9_Q7_WEEK_1[study_id] = int(phq_7)	
					except:
						PHQ9_Q7_WEEK_1[study_id] = None

					try:
						PHQ9_Q8_WEEK_1[study_id] = int(phq_8)
					except:
						PHQ9_Q8_WEEK_1[study_id] = None
					
					try:
						PHQ9_Q9_WEEK_1[study_id] = int(phq_9)
					except:
						PHQ9_Q9_WEEK_1[study_id] = None


					try:
						GAD7_WEEK_1[study_id] = int(gad7_total)
					except:
						GAD7_WEEK_1[study_id] = None

					try:
						GAD7_Q1_WEEK_1[study_id] = int(gad7_q1)
					except:
						GAD7_Q1_WEEK_1[study_id] = None

					try:
						GAD7_Q2_WEEK_1[study_id] = int(gad7_q2)
					except:
						GAD7_Q2_WEEK_1[study_id] = None

					try:
						GAD7_Q3_WEEK_1[study_id] = int(gad7_q3)
					except:
						GAD7_Q3_WEEK_1[study_id] = None

					try:
						GAD7_Q4_WEEK_1[study_id] = int(gad7_q4)
					except:
						GAD7_Q4_WEEK_1[study_id] = None

					try:
						GAD7_Q5_WEEK_1[study_id] = int(gad7_q5)
					except:
						GAD7_Q5_WEEK_1[study_id] = None

					try:
						GAD7_Q6_WEEK_1[study_id] = int(gad7_q6)
					except:
						GAD7_Q6_WEEK_1[study_id] = None
					
					try:
						GAD7_Q7_WEEK_1[study_id] = int(gad7_q7)
					except:
						GAD7_Q7_WEEK_1[study_id] = None

					try:
						HOPE_WEEK_1[study_id] = int(hope_q)
					except:
						HOPE_WEEK_1[study_id] = None


					try:
						EM_1_WEEK_1[study_id] = int(em_1)
					except:
						EM_1_WEEK_1[study_id] = None
					
					try:
						EM_2_WEEK_1[study_id] = int(em_2)
					except:
						EM_2_WEEK_1[study_id] = None

					try:
						EM_3_WEEK_1[study_id] = int(em_3)
					except:
						EM_3_WEEK_1[study_id] = None

					try:
						EM_4_WEEK_1[study_id] = int(em_4)
					except:
						EM_4_WEEK_1[study_id] = None

					try:
						EM_5_WEEK_1[study_id] = int(em_5)
					except:
						EM_5_WEEK_1[study_id] = None

					try:
						EM_6_WEEK_1[study_id] = int(em_6)
					except:
						EM_6_WEEK_1[study_id] = None

					try:
						CCTS_20_WEEK_1[study_id] = int(ccts_20)
					except:
						CCTS_20_WEEK_1[study_id] = None

					try:
						CCTS_28_WEEK_1[study_id] = int(ccts_28)
					except:
						CCTS_28_WEEK_1[study_id] = None

					try:
						CCTS_21_WEEK_1[study_id] = int(ccts_21)
					except:
						CCTS_21_WEEK_1[study_id] = None

					try:
						CCTS_06_WEEK_1[study_id] = int(ccts_06)
					except:
						CCTS_06_WEEK_1[study_id] = None

					try:
						CCTS_24_WEEK_1[study_id] = int(ccts_24)
					except:
						CCTS_24_WEEK_1[study_id] = None

					try:
						CCTS_11_WEEK_1[study_id] = int(ccts_11)
					except:
						CCTS_11_WEEK_1[study_id] = None





			import psycopg2

			# conn = psycopg2.connect(database=os.environ['OTT_DBNAME'], user = os.environ['OTT_DBUSER'], password = os.environ['OTT_DBPASS'], host = os.environ['OTT_DBHOST'] + ".postgres.database.azure.com", port = "5432")
			conn = psycopg2.connect(database=os.environ['OTT_DBNAME'], user = os.environ['OTT_DBUSER'], password = os.environ['OTT_DBPASS'], host = os.environ['OTT_DBHOST'], port = "5432")

			cur = conn.cursor()

			Q = """SELECT username,study_id,condition,week_1_start,survey_1_status FROM study_userdetails ORDER BY study_userdetails.id ASC"""

			cur.execute(Q)
			records = cur.fetchall()

			userdetails_df = pd.DataFrame(records, columns = ['username','study_id', 'condition', 'week_1_start', 'survey_1_status'])
			
			userdetails_df['study_id'] = userdetails_df['study_id'].astype('int')

			discard_usernames = userdetails_df.loc[userdetails_df['study_id'] < 70]['username'].tolist() #+ userdetails_df.loc[userdetails_df['survey_1_status'] != 1]['username'].tolist()

			# create a dict of study_id to condition from userdetails_df
			study_id_to_condition = dict(zip(userdetails_df['study_id'], userdetails_df['condition']))

			username_to_week_1_start = dict(zip(userdetails_df['username'], userdetails_df['week_1_start']))


			DEFAULT_THOUGHTS = ["no one cares about me", "i'm a failure", "i'll never be able to do anything", "i am scared something bad will happen to people i love", "i will go crazy if i don't control my racing thoughts", "i'm worthless"]

			Q = 'SELECT study_thoughtrecord.created_at, study_outcome.updated_at, study_thoughtrecord.thought_record_id, study_thoughtrecord.username, study_thoughtrecord.remove_negative_feeling, study_thoughtrecord.skip_step, study_thoughtrecord.prompt_to_use, study_thoughtrecord.more_suggestions_btn, study_thoughtrecord.multiple_cognitive_distortions, study_thoughtrecord.ai, study_thoughtrecord.emotion_questions , study_thoughtrecord.personalize , study_thoughtrecord.readable, study_thoughtrecord.psychoeducation, believable, stickiness, helpfulness, learnability, belief_1, emotion_strength_1, belief_2, emotion_strength_2 FROM study_thoughtrecord, study_outcome WHERE study_thoughtrecord.thought_record_id = study_outcome.thought_record_id ORDER BY study_thoughtrecord.thought_record_id ASC;'

			cur.execute(Q)
			records = cur.fetchall()

			thought_records_with_outcomes_df = pd.DataFrame(records, columns=['start_time',
											'end_time',
											'thought_record_id', \
											'username', \
											'remove_negative_feeling', \
											'skip_step', \
											'prompt_to_use', \
											'more_suggestions_btn', \
											'multiple_cognitive_distortions', \
											'Human\n+AI', \
											'emotion_questions', \
											'personalize', \
											'readable', \
											'psychoeducation', \
											'believable', 'stickiness', 'helpfulness', 'learnability','belief_1', 'emotion_strength_1', 'belief_2', 'emotion_strength_2'])

			
			# Deduplicate by thought_record_id, keep last
			thought_records_with_outcomes_df = thought_records_with_outcomes_df.drop_duplicates(subset=['thought_record_id'], keep='last')


			thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[~thought_records_with_outcomes_df['username'].isin(discard_usernames)]


			# sort by time
			thought_records_with_outcomes_df = thought_records_with_outcomes_df.sort_values(by = ['start_time'], ascending = True)

			# drop duplicates based on user name
			thought_records_with_outcomes_df = thought_records_with_outcomes_df.drop_duplicates(subset=['username'], keep='first')

			# week_1_start
			thought_records_with_outcomes_df['date_started'] = thought_records_with_outcomes_df['username'].map(username_to_week_1_start)

			# compute week_no
			# week_no = (curr_date - date_started).days // 7 + 1
			thought_records_with_outcomes_df['date_started'] = pd.to_datetime(thought_records_with_outcomes_df['date_started'])

			thought_records_with_outcomes_df['start_time'] = pd.to_datetime(thought_records_with_outcomes_df['start_time'])

			thought_records_with_outcomes_df['week_no'] = thought_records_with_outcomes_df.apply(lambda row: (row['start_time'] - row['date_started']).days // 7 + 1, axis=1)

			# week_no = 1

			# compute_current_week_no(
			thought_records_with_outcomes_df['curr_week_no'] = thought_records_with_outcomes_df.apply(lambda row: compute_current_week_no(row['username']), axis=1)

			# only users with curr_week_no > 4
			# thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['curr_week_no'] > 4]


			# thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['week_no'] == 4]


			thought_records_with_outcomes_df['believable'] = pd.to_numeric(thought_records_with_outcomes_df['believable']) #.mean()
			thought_records_with_outcomes_df['stickiness'] = pd.to_numeric(thought_records_with_outcomes_df['stickiness'])
			thought_records_with_outcomes_df['helpfulness'] = pd.to_numeric(thought_records_with_outcomes_df['helpfulness'])
			thought_records_with_outcomes_df['learnability'] = pd.to_numeric(thought_records_with_outcomes_df['learnability'])

			thought_records_with_outcomes_df['believable'] = thought_records_with_outcomes_df['believable'] + 3.0
			thought_records_with_outcomes_df['stickiness'] = thought_records_with_outcomes_df['stickiness'] + 3.0
			thought_records_with_outcomes_df['helpfulness'] = thought_records_with_outcomes_df['helpfulness'] + 3.0
			thought_records_with_outcomes_df['learnability'] = thought_records_with_outcomes_df['learnability'] + 3.0


			CONDITION_MAP = {'0': 'Pure\ncontrol', '1': 'Without\nAI', '2': 'With\nAI'}

			thought_records_with_outcomes_df['condition'] = thought_records_with_outcomes_df['username'].map(userdetails_df.set_index('username')['condition'])

			thought_records_with_outcomes_df['condition_map'] = thought_records_with_outcomes_df['condition'].map(CONDITION_MAP)

			# average number of records per user for each condition
			print(thought_records_with_outcomes_df.groupby(['condition_map', 'username']).size().groupby('condition_map').mean())

			thought_records_with_outcomes_df['study_id'] = thought_records_with_outcomes_df['username'].map(userdetails_df.set_index('username')['study_id'])

			# astype int
			thought_records_with_outcomes_df['study_id'] = thought_records_with_outcomes_df['study_id'].astype('int')

			print(PRACTICE_CR_BASELINE)

			# map # therapy":"2","talk":"3","seekmh":"3","practice_cr":"4","excite_mhskill":"6","life_impact

			thought_records_with_outcomes_df['therapy'] = thought_records_with_outcomes_df['study_id'].map(THERAPY_BASELINE)
			thought_records_with_outcomes_df['talk'] = thought_records_with_outcomes_df['study_id'].map(TALK_BASELINE)
			thought_records_with_outcomes_df['seekmh'] = thought_records_with_outcomes_df['study_id'].map(SEEK_MH_BASELINE)
			# thought_records_with_outcomes_df['practice_cr'] = thought_records_with_outcomes_df['study_id'].map(PRACTICE_CR_BASELINE)
			# thought_records_with_outcomes_df['excite_mhskill'] = thought_records_with_outcomes_df['study_id'].map(EXCITE_MHSKILL_BASELINE)
			# thought_records_with_outcomes_df['life_impact'] = thought_records_with_outcomes_df['study_id'].map(LIFE_IMPACT_BASELINE)

			# thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['talk'] >= 5]

			thought_records_with_outcomes_df['phq9_baseline'] = thought_records_with_outcomes_df['study_id'].map(PHQ9_BASELINE)

			# phq9 >= 15
			# thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['phq9_baseline'] >= 15]

			# study_id in THREE_WEEKS_COMPLETED
			# thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['study_id'].isin(THREE_WEEKS_COMPLETED)]


			# get thoughts
			Q = """SELECT study_thoughtrecord.created_at, study_outcome.updated_at, study_thoughtrecord.thought_record_id, username, thought, situation, study_emotion.emotion, thinking_trap_selected, reframe_selected, reframe_final, believable, stickiness, helpfulness, learnability
			FROM study_thoughtrecord, study_thought, study_situation, study_thinking_trap_selected, study_reframe_selected, study_reframe_final, study_outcome, study_emotion
			WHERE study_thoughtrecord.thought_record_id = study_thought.thought_record_id AND study_thoughtrecord.thought_record_id = study_situation.thought_record_id AND study_thoughtrecord.thought_record_id = study_thinking_trap_selected.thought_record_id AND study_thoughtrecord.thought_record_id = study_reframe_selected.thought_record_id AND study_thoughtrecord.thought_record_id = study_reframe_selected.thought_record_id AND study_thoughtrecord.thought_record_id = study_emotion.thought_record_id AND study_thought.thought_id = study_situation.thought_id AND study_reframe_selected.reframe_selected_id = study_reframe_final.reframe_selected_id AND study_reframe_final.reframe_final_id = study_outcome.reframe_final_id
			ORDER BY study_thoughtrecord.thought_record_id ASC"""

			cur.execute(Q)
			records = cur.fetchall()

			thought_situations_df = pd.DataFrame(records, columns=['start_time',
											'end_time',
											'thought_record_id', \
											'username', \
											'thought', \
											'situation', \
											'emotion', \
											'thinking_trap_selected', \
											'reframe_selected_or_added', \
											'reframe_final', \
											'believable', 'stickiness', 'helpfulness', 'learnability'])

			print(len(thought_situations_df))

			# sort by start_time
			thought_situations_df = thought_situations_df.sort_values(by=['start_time'])

			# deduplicate
			thought_situations_df = thought_situations_df.drop_duplicates(subset=['thought_record_id'], keep='last')

			# merge with thought_records_with_outcomes_df
			thought_records_with_outcomes_df = pd.merge(thought_records_with_outcomes_df, thought_situations_df[['thought_record_id', 'thought', 'situation']], on='thought_record_id', how='left')

			# lowercase thought
			thought_records_with_outcomes_df['thought'] = thought_records_with_outcomes_df['thought'].str.lower()

			# check if thought in default thoughts
			thought_records_with_outcomes_df['default_thought'] = thought_records_with_outcomes_df['thought'].isin(DEFAULT_THOUGHTS)

			# only keep non-default thoughts
			# thought_records_with_outcomes_df = thought_records_with_outcomes_df.loc[~thought_records_with_outcomes_df['default_thought']]



			# print(thought_records_with_outcomes_df)


			# create a reframe_relatability dictionary, one for each condition ('1' and '2'), with keys as 'mean', 'std'
			
			reframe_relatability_1 = {}

			reframe_relatability_1['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['believable'].mean()
			reframe_relatability_1['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['believable'].std()

			reframe_relatability_2 = {}

			reframe_relatability_2['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['believable'].mean()
			reframe_relatability_2['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['believable'].std()


			# create a reframe_helpfulness dictionary, one for each condition ('1' and '2'), with keys as 'mean', 'std'

			reframe_helpfulness_1 = {}

			reframe_helpfulness_1['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['helpfulness'].mean()
			reframe_helpfulness_1['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['helpfulness'].std()

			reframe_helpfulness_2 = {}

			reframe_helpfulness_2['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['helpfulness'].mean()
			reframe_helpfulness_2['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['helpfulness'].std()


			# create a reframe_memorability dictionary, one for each condition ('1' and '2'), with keys as 'mean', 'std'

			reframe_memorability_1 = {}

			reframe_memorability_1['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['stickiness'].mean()
			reframe_memorability_1['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['stickiness'].std()

			reframe_memorability_2 = {}

			reframe_memorability_2['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['stickiness'].mean()
			reframe_memorability_2['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['stickiness'].std()


			# create a reframe_learnability dictionary, one for each condition ('1' and '2'), with keys as 'mean', 'std'

			reframe_learnability_1 = {}

			reframe_learnability_1['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['learnability'].mean()
			reframe_learnability_1['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['learnability'].std()

			reframe_learnability_2 = {}

			reframe_learnability_2['mean'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['learnability'].mean()
			reframe_learnability_2['std'] = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['learnability'].std()


			# compute p_value between the two condition

			from scipy import stats

			# believable

			believable_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['believable'].tolist()
			believable_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['believable'].tolist()

			N_1 = len(believable_1)
			N_2 = len(believable_2)

			reframe_relatibility_p_value = stats.ttest_ind(believable_1, believable_2)[1]

			# helpfulness

			helpfulness_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['helpfulness'].tolist()
			helpfulness_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['helpfulness'].tolist()

			reframe_helpfulness_p_value = stats.ttest_ind(helpfulness_1, helpfulness_2)[1]

			# memorability

			memorability_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['stickiness'].tolist()
			memorability_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['stickiness'].tolist()

			reframe_memorability_p_value = stats.ttest_ind(memorability_1, memorability_2)[1]

			# learnability

			learnability_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['learnability'].tolist()
			learnability_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['learnability'].tolist()

			reframe_learnability_p_value = stats.ttest_ind(learnability_1, learnability_2)[1]


			# compute cohen's d

			# believable

			believable_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['believable']
			believable_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['believable']

			reframe_relatibility_cohen_d = cohen_d(believable_1, believable_2)

			# helpfulness

			helpfulness_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['helpfulness']
			helpfulness_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['helpfulness']

			reframe_helpfulness_cohen_d = cohen_d(helpfulness_1, helpfulness_2)

			# memorability

			memorability_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['stickiness']
			memorability_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['stickiness']

			reframe_memorability_cohen_d = cohen_d(memorability_1, memorability_2)

			# learnability

			learnability_1 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '1']['learnability']
			learnability_2 = thought_records_with_outcomes_df.loc[thought_records_with_outcomes_df['condition'] == '2']['learnability']

			reframe_learnability_cohen_d = cohen_d(learnability_1, learnability_2)


			thought_records_with_emotion_outcomes_df = thought_records_with_outcomes_df[['start_time', 'end_time', 'thought_record_id', 'username', 'condition', 'believable', 'helpfulness', 'stickiness', 'learnability', 'belief_1', 'emotion_strength_1', 'belief_2', 'emotion_strength_2']] 

			Q = """SELECT * FROM study_emotion
			ORDER BY thought_record_id DESC"""

			cur.execute(Q)
			emotion = cur.fetchall()

			emotion_df = pd.DataFrame(emotion, columns = ['emotion_id', \
														'created_at', \
														'updated_at', \
														'thought_record_id', \
														'thought_id', \
														'belief', \
														'emotion', \
														'emotion_strength'])

			
			thought_records_with_emotion_outcomes_df = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['thought_record_id'] >= emotion_df['thought_record_id'].min()]


			thought_records_with_emotion_outcomes_df['belief_1'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['belief_1'], errors='coerce')
			thought_records_with_emotion_outcomes_df['belief_2'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['belief_2'], errors='coerce')
			thought_records_with_emotion_outcomes_df['emotion_strength_1'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['emotion_strength_1'], errors='coerce')
			thought_records_with_emotion_outcomes_df['emotion_strength_2'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['emotion_strength_2'], errors='coerce')


			thought_records_with_emotion_outcomes_df = thought_records_with_emotion_outcomes_df.fillna('')

			thought_records_with_emotion_outcomes_df['all_belief'] = thought_records_with_emotion_outcomes_df.apply(lambda row: row['belief_1'] if row['belief_1'] != '' else row['belief_2'], axis=1)

			thought_records_with_emotion_outcomes_df['all_emotion_strength'] = thought_records_with_emotion_outcomes_df.apply(lambda row: row['emotion_strength_1'] if row['emotion_strength_1'] != '' else row['emotion_strength_2'], axis=1)
			
			# Remove discarded usernames
			thought_records_with_emotion_outcomes_df = thought_records_with_emotion_outcomes_df[~thought_records_with_emotion_outcomes_df['username'].isin(discard_usernames)]

			thought_records_with_emotion_outcomes_df = pd.merge(thought_records_with_emotion_outcomes_df, emotion_df[['thought_record_id', 'emotion_strength', 'belief']], on='thought_record_id', how='left')

			thought_records_with_emotion_outcomes_df = thought_records_with_emotion_outcomes_df.loc[~thought_records_with_emotion_outcomes_df['emotion_strength'].isna()]

			thought_records_with_emotion_outcomes_df['emotion_strength'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['emotion_strength'])
			thought_records_with_emotion_outcomes_df['belief'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['belief'])

			thought_records_with_emotion_outcomes_df['all_emotion_strength'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['all_emotion_strength'])
			thought_records_with_emotion_outcomes_df['all_belief'] = pd.to_numeric(thought_records_with_emotion_outcomes_df['all_belief'])


			# change in belief
			thought_records_with_emotion_outcomes_df['belief_change'] = thought_records_with_emotion_outcomes_df.apply(lambda row: row['belief'] - row['all_belief'], axis=1)

			# belief change
			thought_records_with_emotion_outcomes_df['emotion_change'] = thought_records_with_emotion_outcomes_df.apply(lambda row: row['emotion_strength'] - row['all_emotion_strength'], axis=1)


			# create a belief_change dictionary, one for each condition ('1' and '2'), with keys as 'mean', 'std'

			belief_change_1 = {}
			
			belief_change_1['mean'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['belief_change'].mean()
			belief_change_1['std'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['belief_change'].std()

			belief_change_2 = {}

			belief_change_2['mean'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['belief_change'].mean()
			belief_change_2['std'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['belief_change'].std()


			# create a emotion_change dictionary, one for each condition ('1' and '2'), with keys as 'mean', 'std'

			emotion_change_1 = {}

			emotion_change_1['mean'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['emotion_change'].mean()
			emotion_change_1['std'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['emotion_change'].std()

			emotion_change_2 = {}

			emotion_change_2['mean'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['emotion_change'].mean()
			emotion_change_2['std'] = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['emotion_change'].std()


			# compute p_value between the two condition

			# belief change

			tmp_belief_change_1 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['belief_change']
			tmp_belief_change_2 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['belief_change']

			# remove nan
			tmp_belief_change_1 = tmp_belief_change_1[~np.isnan(tmp_belief_change_1)]
			tmp_belief_change_2 = tmp_belief_change_2[~np.isnan(tmp_belief_change_2)]

			tmp_belief_change_1 = tmp_belief_change_1.tolist()
			tmp_belief_change_2 = tmp_belief_change_2.tolist()


			print(stats.ttest_ind(tmp_belief_change_1, tmp_belief_change_2))

			belief_change_p_value = stats.ttest_ind(tmp_belief_change_1, tmp_belief_change_2)[1]

			# emotion change, remove nan

			tmp_emotion_change_1 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['emotion_change']
			tmp_emotion_change_1 = tmp_emotion_change_1[~np.isnan(tmp_emotion_change_1)].tolist()

			tmp_emotion_change_2 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['emotion_change']
			tmp_emotion_change_2 = tmp_emotion_change_2[~np.isnan(tmp_emotion_change_2)].tolist()

			# 
			# tmp_emotion_change_1 = tmp_emotion_change_1[~np.isnan(tmp_emotion_change_1)]
			# tmp_emotion_change_2 = tmp_emotion_change_2[~np.isnan(tmp_emotion_change_2)]

			emotion_change_p_value = stats.ttest_ind(tmp_emotion_change_1, tmp_emotion_change_2)[1]


			# compute cohen's d

			# belief change

			tmp_belief_change_1 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['belief_change']
			tmp_belief_change_2 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['belief_change']

			belief_change_cohen_d = cohen_d(tmp_belief_change_1, tmp_belief_change_2)

			# emotion change

			tmp_emotion_change_1 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '1']['emotion_change']
			tmp_emotion_change_2 = thought_records_with_emotion_outcomes_df.loc[thought_records_with_emotion_outcomes_df['condition'] == '2']['emotion_change']

			emotion_change_cohen_d = cohen_d(tmp_emotion_change_1, tmp_emotion_change_2)


			# return the computed values with upto 4 decimal places

			reframe_relatability_1['mean'] = round(reframe_relatability_1['mean'], 4)
			reframe_relatability_1['std'] = round(reframe_relatability_1['std'], 4)
			reframe_relatability_2['mean'] = round(reframe_relatability_2['mean'], 4)
			reframe_relatability_2['std'] = round(reframe_relatability_2['std'], 4)

			reframe_helpfulness_1['mean'] = round(reframe_helpfulness_1['mean'], 4)
			reframe_helpfulness_1['std'] = round(reframe_helpfulness_1['std'], 4)
			reframe_helpfulness_2['mean'] = round(reframe_helpfulness_2['mean'], 4)
			reframe_helpfulness_2['std'] = round(reframe_helpfulness_2['std'], 4)

			reframe_memorability_1['mean'] = round(reframe_memorability_1['mean'], 4)
			reframe_memorability_1['std'] = round(reframe_memorability_1['std'], 4)
			reframe_memorability_2['mean'] = round(reframe_memorability_2['mean'], 4)
			reframe_memorability_2['std'] = round(reframe_memorability_2['std'], 4)

			reframe_learnability_1['mean'] = round(reframe_learnability_1['mean'], 4)
			reframe_learnability_1['std'] = round(reframe_learnability_1['std'], 4)
			reframe_learnability_2['mean'] = round(reframe_learnability_2['mean'], 4)
			reframe_learnability_2['std'] = round(reframe_learnability_2['std'], 4)

			reframe_relatibility_p_value = round(reframe_relatibility_p_value, 4)
			reframe_helpfulness_p_value = round(reframe_helpfulness_p_value, 4)
			reframe_memorability_p_value = round(reframe_memorability_p_value, 4)
			reframe_learnability_p_value = round(reframe_learnability_p_value, 4)

			# reframe_relatibility_cohen_d = (reframe_relatibility_cohen_d, 4)
			# reframe_helpfulness_cohen_d = round(reframe_helpfulness_cohen_d, 4)
			# reframe_memorability_cohen_d = round(reframe_memorability_cohen_d, 4)
			# reframe_learnability_cohen_d = round(reframe_learnability_cohen_d, 4)

			belief_change_1['mean'] = round(belief_change_1['mean'], 4)
			belief_change_1['std'] = round(belief_change_1['std'], 4)
			belief_change_2['mean'] = round(belief_change_2['mean'], 4)
			belief_change_2['std'] = round(belief_change_2['std'], 4)

			emotion_change_1['mean'] = round(emotion_change_1['mean'], 4)
			emotion_change_1['std'] = round(emotion_change_1['std'], 4)
			emotion_change_2['mean'] = round(emotion_change_2['mean'], 4)
			emotion_change_2['std'] = round(emotion_change_2['std'], 4)

			belief_change_p_value = round(belief_change_p_value, 4)
			emotion_change_p_value = round(emotion_change_p_value, 4)

			# belief_change_cohen_d = round(belief_change_cohen_d, 4)
			# emotion_change_cohen_d = round(emotion_change_cohen_d, 4)

			cur.close()

			# close the connection
			conn.close()


			

			# change in phq and gad
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1 = []
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1 = []

			
			GAD7_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1 = []
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1 = []

			HOPE_CHANGE_BASELINE_TO_WEEK_1_1 = []

			EM_1_WEEK_1_1 = []
			EM_2_WEEK_1_1 = []
			EM_3_WEEK_1_1 = []
			EM_4_WEEK_1_1 = []
			EM_5_WEEK_1_1 = []
			EM_6_WEEK_1_1 = []

			CCTS_20_WEEK_1_1 = []
			CCTS_28_WEEK_1_1 = []
			CCTS_21_WEEK_1_1 = []
			CCTS_06_WEEK_1_1 = []
			CCTS_24_WEEK_1_1 = []
			CCTS_11_WEEK_1_1 = []
			CCTS_ELAB_WEEK_1_1 = []
			CCTS_WELLBEING_WEEK_1_1 = []
			CCTS_OTHER_WEEK_1_1 = []


			PHQ9_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2 = []
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2 = []

			
			GAD7_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2 = []
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2 = []

			HOPE_CHANGE_BASELINE_TO_WEEK_1_2 = []

			EM_1_WEEK_1_2 = []
			EM_2_WEEK_1_2 = []
			EM_3_WEEK_1_2 = []
			EM_4_WEEK_1_2 = []
			EM_5_WEEK_1_2 = []
			EM_6_WEEK_1_2 = []

			CCTS_20_WEEK_1_2 = []
			CCTS_28_WEEK_1_2 = []
			CCTS_21_WEEK_1_2 = []
			CCTS_06_WEEK_1_2 = []
			CCTS_24_WEEK_1_2 = []
			CCTS_11_WEEK_1_2 = []
			CCTS_ELAB_WEEK_1_2 = []
			CCTS_WELLBEING_WEEK_1_2 = []
			CCTS_OTHER_WEEK_1_2 = []

			N_1_SURVEY = 0
			N_2_SURVEY = 0

			N_1_PHQ9_SURVEY = 0
			N_2_PHQ9_SURVEY = 0


			for study_id in PHQ9_WEEK_1.keys():

				try:
					condition = int(study_id_to_condition[study_id])
				except:
					try:
						condition = int(study_id_to_condition[int(study_id)])
					except:
						print('Error condition', study_id)

				if condition == 1:
					N_1_SURVEY += 1

					if PHQ9_BASELINE[study_id] != None and PHQ9_WEEK_1[study_id] != None:
						PHQ9_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_WEEK_1[study_id] + PHQ9_BASELINE[study_id])

						# print(PHQ9_BASELINE[study_id], '-->', PHQ9_WEEK_1[study_id])
						N_1_PHQ9_SURVEY += 1

					if PHQ9_Q1_BASELINE[study_id] != None and PHQ9_Q1_WEEK_1[study_id] != None:
						PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q1_WEEK_1[study_id] + PHQ9_Q1_BASELINE[study_id])

					if PHQ9_Q2_BASELINE[study_id] != None and PHQ9_Q2_WEEK_1[study_id] != None:
						PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q2_WEEK_1[study_id] + PHQ9_Q2_BASELINE[study_id])

					if PHQ9_Q3_BASELINE[study_id] != None and PHQ9_Q3_WEEK_1[study_id] != None:
						PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q3_WEEK_1[study_id] + PHQ9_Q3_BASELINE[study_id])

					if PHQ9_Q4_BASELINE[study_id] != None and PHQ9_Q4_WEEK_1[study_id] != None:
						PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q4_WEEK_1[study_id] + PHQ9_Q4_BASELINE[study_id])

					if PHQ9_Q5_BASELINE[study_id] != None and PHQ9_Q5_WEEK_1[study_id] != None:
						PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q5_WEEK_1[study_id] + PHQ9_Q5_BASELINE[study_id])
					
					if PHQ9_Q6_BASELINE[study_id] != None and PHQ9_Q6_WEEK_1[study_id] != None:
						PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q6_WEEK_1[study_id] + PHQ9_Q6_BASELINE[study_id])

					if PHQ9_Q7_BASELINE[study_id] != None and PHQ9_Q7_WEEK_1[study_id] != None:
						PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q7_WEEK_1[study_id] + PHQ9_Q7_BASELINE[study_id])

					if PHQ9_Q8_BASELINE[study_id] != None and PHQ9_Q8_WEEK_1[study_id] != None:
						PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q8_WEEK_1[study_id] + PHQ9_Q8_BASELINE[study_id])

					if PHQ9_Q9_BASELINE[study_id] != None and PHQ9_Q9_WEEK_1[study_id] != None:
						PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1.append(-PHQ9_Q9_WEEK_1[study_id] + PHQ9_Q9_BASELINE[study_id])


					if GAD7_BASELINE[study_id] != None and GAD7_WEEK_1[study_id] != None:
						GAD7_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_WEEK_1[study_id] + GAD7_BASELINE[study_id])

						# print(GAD7_BASELINE[study_id], '-->', GAD7_WEEK_1[study_id])

					if GAD7_Q1_BASELINE[study_id] != None and GAD7_Q1_WEEK_1[study_id] != None:
						GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q1_WEEK_1[study_id] + GAD7_Q1_BASELINE[study_id])

					if GAD7_Q2_BASELINE[study_id] != None and GAD7_Q2_WEEK_1[study_id] != None:
						GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q2_WEEK_1[study_id] + GAD7_Q2_BASELINE[study_id])

					
					if GAD7_Q3_BASELINE[study_id] != None and GAD7_Q3_WEEK_1[study_id] != None:
						GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q3_WEEK_1[study_id] + GAD7_Q3_BASELINE[study_id])

					if GAD7_Q4_BASELINE[study_id] != None and GAD7_Q4_WEEK_1[study_id] != None:
						GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q4_WEEK_1[study_id] + GAD7_Q4_BASELINE[study_id])

					if GAD7_Q5_BASELINE[study_id] != None and GAD7_Q5_WEEK_1[study_id] != None:
						GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q5_WEEK_1[study_id] + GAD7_Q5_BASELINE[study_id])

					if GAD7_Q6_BASELINE[study_id] != None and GAD7_Q6_WEEK_1[study_id] != None:
						GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q6_WEEK_1[study_id] + GAD7_Q6_BASELINE[study_id])

					if GAD7_Q7_BASELINE[study_id] != None and GAD7_Q7_WEEK_1[study_id] != None:
						GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1.append(-GAD7_Q7_WEEK_1[study_id] + GAD7_Q7_BASELINE[study_id])

					if HOPE_BASELINE[study_id] != None and HOPE_WEEK_1[study_id] != None:
						HOPE_CHANGE_BASELINE_TO_WEEK_1_1.append(-HOPE_WEEK_1[study_id] + HOPE_BASELINE[study_id])


					
					if EM_1_WEEK_1[study_id] != None:
						EM_1_WEEK_1_1.append(EM_1_WEEK_1[study_id])

					if EM_2_WEEK_1[study_id] != None:
						EM_2_WEEK_1_1.append(EM_2_WEEK_1[study_id])

					if EM_3_WEEK_1[study_id] != None:
						EM_3_WEEK_1_1.append(EM_3_WEEK_1[study_id])

					if EM_4_WEEK_1[study_id] != None:
						EM_4_WEEK_1_1.append(EM_4_WEEK_1[study_id])

					if EM_5_WEEK_1[study_id] != None:
						EM_5_WEEK_1_1.append(EM_5_WEEK_1[study_id])

					if EM_6_WEEK_1[study_id] != None:
						EM_6_WEEK_1_1.append(EM_6_WEEK_1[study_id])


					if CCTS_20_WEEK_1[study_id] != None:
						CCTS_20_WEEK_1_1.append(CCTS_20_WEEK_1[study_id])

					if CCTS_28_WEEK_1[study_id] != None:
						CCTS_28_WEEK_1_1.append(CCTS_28_WEEK_1[study_id])

					if CCTS_21_WEEK_1[study_id] != None:
						CCTS_21_WEEK_1_1.append(CCTS_21_WEEK_1[study_id])

					if CCTS_06_WEEK_1[study_id] != None:
						CCTS_06_WEEK_1_1.append(CCTS_06_WEEK_1[study_id])

					if CCTS_24_WEEK_1[study_id] != None:
						CCTS_24_WEEK_1_1.append(CCTS_24_WEEK_1[study_id])

					if CCTS_11_WEEK_1[study_id] != None:
						CCTS_11_WEEK_1_1.append(CCTS_11_WEEK_1[study_id])

					# CCTS_ELAB_WEEK_1_1.append(CCTS_ELAB_WEEK_1[study_id])
					# CCTS_WELLBEING_WEEK_1_1.append(CCTS_WELLBEING_WEEK_1[study_id])
					# CCTS_OTHER_WEEK_1_1.append(CCTS_OTHER_WEEK_1[study_id])


				elif condition == 2:
					N_2_SURVEY += 1

					if PHQ9_BASELINE[study_id] != None and PHQ9_WEEK_1[study_id] != None:
						PHQ9_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_WEEK_1[study_id] + PHQ9_BASELINE[study_id])
						N_2_PHQ9_SURVEY += 1

						# print(PHQ9_BASELINE[study_id], '-->', PHQ9_WEEK_1[study_id])

					if PHQ9_Q1_BASELINE[study_id] != None and PHQ9_Q1_WEEK_1[study_id] != None:
						PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q1_WEEK_1[study_id] + PHQ9_Q1_BASELINE[study_id])

					if PHQ9_Q2_BASELINE[study_id] != None and PHQ9_Q2_WEEK_1[study_id] != None:
						PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q2_WEEK_1[study_id] + PHQ9_Q2_BASELINE[study_id])

					if PHQ9_Q3_BASELINE[study_id] != None and PHQ9_Q3_WEEK_1[study_id] != None:
						PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q3_WEEK_1[study_id] + PHQ9_Q3_BASELINE[study_id])

					if PHQ9_Q4_BASELINE[study_id] != None and PHQ9_Q4_WEEK_1[study_id] != None:
						PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q4_WEEK_1[study_id] + PHQ9_Q4_BASELINE[study_id])

					if PHQ9_Q5_BASELINE[study_id] != None and PHQ9_Q5_WEEK_1[study_id] != None:
						PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q5_WEEK_1[study_id] + PHQ9_Q5_BASELINE[study_id])
					
					if PHQ9_Q6_BASELINE[study_id] != None and PHQ9_Q6_WEEK_1[study_id] != None:
						PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q6_WEEK_1[study_id] + PHQ9_Q6_BASELINE[study_id])

					if PHQ9_Q7_BASELINE[study_id] != None and PHQ9_Q7_WEEK_1[study_id] != None:
						PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q7_WEEK_1[study_id] + PHQ9_Q7_BASELINE[study_id])

					if PHQ9_Q8_BASELINE[study_id] != None and PHQ9_Q8_WEEK_1[study_id] != None:
						PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q8_WEEK_1[study_id] + PHQ9_Q8_BASELINE[study_id])

					if PHQ9_Q9_BASELINE[study_id] != None and PHQ9_Q9_WEEK_1[study_id] != None:
						PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2.append(-PHQ9_Q9_WEEK_1[study_id] + PHQ9_Q9_BASELINE[study_id])


					if GAD7_BASELINE[study_id] != None and GAD7_WEEK_1[study_id] != None:
						GAD7_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_WEEK_1[study_id] + GAD7_BASELINE[study_id])

						# print(GAD7_BASELINE[study_id], '-->', GAD7_WEEK_1[study_id])

					if GAD7_Q1_BASELINE[study_id] != None and GAD7_Q1_WEEK_1[study_id] != None:
						GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q1_WEEK_1[study_id] + GAD7_Q1_BASELINE[study_id])

					if GAD7_Q2_BASELINE[study_id] != None and GAD7_Q2_WEEK_1[study_id] != None:
						GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q2_WEEK_1[study_id] + GAD7_Q2_BASELINE[study_id])

					
					if GAD7_Q3_BASELINE[study_id] != None and GAD7_Q3_WEEK_1[study_id] != None:
						GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q3_WEEK_1[study_id] + GAD7_Q3_BASELINE[study_id])

					if GAD7_Q4_BASELINE[study_id] != None and GAD7_Q4_WEEK_1[study_id] != None:
						GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q4_WEEK_1[study_id] + GAD7_Q4_BASELINE[study_id])

					if GAD7_Q5_BASELINE[study_id] != None and GAD7_Q5_WEEK_1[study_id] != None:
						GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q5_WEEK_1[study_id] + GAD7_Q5_BASELINE[study_id])

					if GAD7_Q6_BASELINE[study_id] != None and GAD7_Q6_WEEK_1[study_id] != None:
						GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q6_WEEK_1[study_id] + GAD7_Q6_BASELINE[study_id])

					if GAD7_Q7_BASELINE[study_id] != None and GAD7_Q7_WEEK_1[study_id] != None:
						GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2.append(-GAD7_Q7_WEEK_1[study_id] + GAD7_Q7_BASELINE[study_id])

					if HOPE_BASELINE[study_id] != None and HOPE_WEEK_1[study_id] != None:
						HOPE_CHANGE_BASELINE_TO_WEEK_1_2.append(-HOPE_WEEK_1[study_id] + HOPE_BASELINE[study_id])


					
					if EM_1_WEEK_1[study_id] != None:
						EM_1_WEEK_1_2.append(EM_1_WEEK_1[study_id])

					if EM_2_WEEK_1[study_id] != None:
						EM_2_WEEK_1_2.append(EM_2_WEEK_1[study_id])

					if EM_3_WEEK_1[study_id] != None:
						EM_3_WEEK_1_2.append(EM_3_WEEK_1[study_id])

					if EM_4_WEEK_1[study_id] != None:
						EM_4_WEEK_1_2.append(EM_4_WEEK_1[study_id])

					if EM_5_WEEK_1[study_id] != None:
						EM_5_WEEK_1_2.append(EM_5_WEEK_1[study_id])

					if EM_6_WEEK_1[study_id] != None:
						EM_6_WEEK_1_2.append(EM_6_WEEK_1[study_id])


					if CCTS_20_WEEK_1[study_id] != None:
						CCTS_20_WEEK_1_2.append(CCTS_20_WEEK_1[study_id])

					if CCTS_28_WEEK_1[study_id] != None:
						CCTS_28_WEEK_1_2.append(CCTS_28_WEEK_1[study_id])

					if CCTS_21_WEEK_1[study_id] != None:
						CCTS_21_WEEK_1_2.append(CCTS_21_WEEK_1[study_id])

					if CCTS_06_WEEK_1[study_id] != None:
						CCTS_06_WEEK_1_2.append(CCTS_06_WEEK_1[study_id])

					if CCTS_24_WEEK_1[study_id] != None:
						CCTS_24_WEEK_1_2.append(CCTS_24_WEEK_1[study_id])

					if CCTS_11_WEEK_1[study_id] != None:
						CCTS_11_WEEK_1_2.append(CCTS_11_WEEK_1[study_id])


			print('PHQ9_CHANGE_BASELINE_TO_WEEK_1_1:', PHQ9_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_CHANGE_BASELINE_TO_WEEK_1_2))


			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2))

			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2))

			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2))

			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2))

			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2))


			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2))

			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2))


			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2))

			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1)
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1)

			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2)
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2)

			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1, PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2))



			GAD7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_CHANGE_BASELINE_TO_WEEK_1_2))


			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2))

			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2))

			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2))

			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2))

			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2))


			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2))

			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1)
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1)

			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2)
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2)

			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1, GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2))


			HOPE_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = np.mean(HOPE_CHANGE_BASELINE_TO_WEEK_1_1)
			HOPE_CHANGE_BASELINE_TO_WEEK_1_1_STD = np.std(HOPE_CHANGE_BASELINE_TO_WEEK_1_1)

			HOPE_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = np.mean(HOPE_CHANGE_BASELINE_TO_WEEK_1_2)
			HOPE_CHANGE_BASELINE_TO_WEEK_1_2_STD = np.std(HOPE_CHANGE_BASELINE_TO_WEEK_1_2)

			HOPE_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = stats.ttest_ind(HOPE_CHANGE_BASELINE_TO_WEEK_1_1, HOPE_CHANGE_BASELINE_TO_WEEK_1_2)[1]
			HOPE_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = cohen_d(np.asarray(HOPE_CHANGE_BASELINE_TO_WEEK_1_1), np.asarray(HOPE_CHANGE_BASELINE_TO_WEEK_1_2))


			EM_1_WEEK_1_1_MEAN = np.mean(EM_1_WEEK_1_1)
			EM_1_WEEK_1_1_STD = np.std(EM_1_WEEK_1_1)

			EM_1_WEEK_1_2_MEAN = np.mean(EM_1_WEEK_1_2)
			EM_1_WEEK_1_2_STD = np.std(EM_1_WEEK_1_2)

			EM_1_WEEK_1_P_VALUE = stats.ttest_ind(EM_1_WEEK_1_1, EM_1_WEEK_1_2)[1]
			EM_1_WEEK_1_COHEN_D = cohen_d(np.asarray(EM_1_WEEK_1_1), np.asarray(EM_1_WEEK_1_2))


			EM_2_WEEK_1_1_MEAN = np.mean(EM_2_WEEK_1_1)
			EM_2_WEEK_1_1_STD = np.std(EM_2_WEEK_1_1)

			EM_2_WEEK_1_2_MEAN = np.mean(EM_2_WEEK_1_2)
			EM_2_WEEK_1_2_STD = np.std(EM_2_WEEK_1_2)

			EM_2_WEEK_1_P_VALUE = stats.ttest_ind(EM_2_WEEK_1_1, EM_2_WEEK_1_2)[1]
			EM_2_WEEK_1_COHEN_D = cohen_d(np.asarray(EM_2_WEEK_1_1), np.asarray(EM_2_WEEK_1_2))


			EM_3_WEEK_1_1_MEAN = np.mean(EM_3_WEEK_1_1)
			EM_3_WEEK_1_1_STD = np.std(EM_3_WEEK_1_1)

			EM_3_WEEK_1_2_MEAN = np.mean(EM_3_WEEK_1_2)
			EM_3_WEEK_1_2_STD = np.std(EM_3_WEEK_1_2)

			EM_3_WEEK_1_P_VALUE = stats.ttest_ind(EM_3_WEEK_1_1, EM_3_WEEK_1_2)[1]
			EM_3_WEEK_1_COHEN_D = cohen_d(np.asarray(EM_3_WEEK_1_1), np.asarray(EM_3_WEEK_1_2))


			EM_4_WEEK_1_1_MEAN = np.mean(EM_4_WEEK_1_1)
			EM_4_WEEK_1_1_STD = np.std(EM_4_WEEK_1_1)

			EM_4_WEEK_1_2_MEAN = np.mean(EM_4_WEEK_1_2)
			EM_4_WEEK_1_2_STD = np.std(EM_4_WEEK_1_2)

			EM_4_WEEK_1_P_VALUE = stats.ttest_ind(EM_4_WEEK_1_1, EM_4_WEEK_1_2)[1]
			EM_4_WEEK_1_COHEN_D = cohen_d(np.asarray(EM_4_WEEK_1_1), np.asarray(EM_4_WEEK_1_2))


			EM_5_WEEK_1_1_MEAN = np.mean(EM_5_WEEK_1_1)
			EM_5_WEEK_1_1_STD = np.std(EM_5_WEEK_1_1)

			EM_5_WEEK_1_2_MEAN = np.mean(EM_5_WEEK_1_2)
			EM_5_WEEK_1_2_STD = np.std(EM_5_WEEK_1_2)

			EM_5_WEEK_1_P_VALUE = stats.ttest_ind(EM_5_WEEK_1_1, EM_5_WEEK_1_2)[1]
			EM_5_WEEK_1_COHEN_D = cohen_d(np.asarray(EM_5_WEEK_1_1), np.asarray(EM_5_WEEK_1_2))


			EM_6_WEEK_1_1_MEAN = np.mean(EM_6_WEEK_1_1)
			EM_6_WEEK_1_1_STD = np.std(EM_6_WEEK_1_1)

			EM_6_WEEK_1_2_MEAN = np.mean(EM_6_WEEK_1_2)
			EM_6_WEEK_1_2_STD = np.std(EM_6_WEEK_1_2)

			EM_6_WEEK_1_P_VALUE = stats.ttest_ind(EM_6_WEEK_1_1, EM_6_WEEK_1_2)[1]
			EM_6_WEEK_1_COHEN_D = cohen_d(np.asarray(EM_6_WEEK_1_1), np.asarray(EM_6_WEEK_1_2))


			CCTS_20_WEEK_1_1_MEAN = np.mean(CCTS_20_WEEK_1_1)
			CCTS_20_WEEK_1_1_STD = np.std(CCTS_20_WEEK_1_1)

			CCTS_20_WEEK_1_2_MEAN = np.mean(CCTS_20_WEEK_1_2)
			CCTS_20_WEEK_1_2_STD = np.std(CCTS_20_WEEK_1_2)

			CCTS_20_WEEK_1_P_VALUE = stats.ttest_ind(CCTS_20_WEEK_1_1, CCTS_20_WEEK_1_2)[1]
			CCTS_20_WEEK_1_COHEN_D = cohen_d(np.asarray(CCTS_20_WEEK_1_1), np.asarray(CCTS_20_WEEK_1_2))


			CCTS_28_WEEK_1_1_MEAN = np.mean(CCTS_28_WEEK_1_1)
			CCTS_28_WEEK_1_1_STD = np.std(CCTS_28_WEEK_1_1)

			CCTS_28_WEEK_1_2_MEAN = np.mean(CCTS_28_WEEK_1_2)
			CCTS_28_WEEK_1_2_STD = np.std(CCTS_28_WEEK_1_2)

			CCTS_28_WEEK_1_P_VALUE = stats.ttest_ind(CCTS_28_WEEK_1_1, CCTS_28_WEEK_1_2)[1]
			CCTS_28_WEEK_1_COHEN_D = cohen_d(np.asarray(CCTS_28_WEEK_1_1), np.asarray(CCTS_28_WEEK_1_2))


			CCTS_21_WEEK_1_1_MEAN = np.mean(CCTS_21_WEEK_1_1)
			CCTS_21_WEEK_1_1_STD = np.std(CCTS_21_WEEK_1_1)

			CCTS_21_WEEK_1_2_MEAN = np.mean(CCTS_21_WEEK_1_2)
			CCTS_21_WEEK_1_2_STD = np.std(CCTS_21_WEEK_1_2)

			CCTS_21_WEEK_1_P_VALUE = stats.ttest_ind(CCTS_21_WEEK_1_1, CCTS_21_WEEK_1_2)[1]
			CCTS_21_WEEK_1_COHEN_D = cohen_d(np.asarray(CCTS_21_WEEK_1_1), np.asarray(CCTS_21_WEEK_1_2))


			CCTS_06_WEEK_1_1_MEAN = np.mean(CCTS_06_WEEK_1_1)
			CCTS_06_WEEK_1_1_STD = np.std(CCTS_06_WEEK_1_1)

			CCTS_06_WEEK_1_2_MEAN = np.mean(CCTS_06_WEEK_1_2)
			CCTS_06_WEEK_1_2_STD = np.std(CCTS_06_WEEK_1_2)

			CCTS_06_WEEK_1_P_VALUE = stats.ttest_ind(CCTS_06_WEEK_1_1, CCTS_06_WEEK_1_2)[1]
			CCTS_06_WEEK_1_COHEN_D = cohen_d(np.asarray(CCTS_06_WEEK_1_1), np.asarray(CCTS_06_WEEK_1_2))


			CCTS_24_WEEK_1_1_MEAN = np.mean(CCTS_24_WEEK_1_1)
			CCTS_24_WEEK_1_1_STD = np.std(CCTS_24_WEEK_1_1)

			CCTS_24_WEEK_1_2_MEAN = np.mean(CCTS_24_WEEK_1_2)
			CCTS_24_WEEK_1_2_STD = np.std(CCTS_24_WEEK_1_2)

			CCTS_24_WEEK_1_P_VALUE = stats.ttest_ind(CCTS_24_WEEK_1_1, CCTS_24_WEEK_1_2)[1]
			CCTS_24_WEEK_1_COHEN_D = cohen_d(np.asarray(CCTS_24_WEEK_1_1), np.asarray(CCTS_24_WEEK_1_2))


			CCTS_11_WEEK_1_1_MEAN = np.mean(CCTS_11_WEEK_1_1)
			CCTS_11_WEEK_1_1_STD = np.std(CCTS_11_WEEK_1_1)
			
			CCTS_11_WEEK_1_2_MEAN = np.mean(CCTS_11_WEEK_1_2)
			CCTS_11_WEEK_1_2_STD = np.std(CCTS_11_WEEK_1_2)

			CCTS_11_WEEK_1_P_VALUE = stats.ttest_ind(CCTS_11_WEEK_1_1, CCTS_11_WEEK_1_2)[1]
			CCTS_11_WEEK_1_COHEN_D = cohen_d(np.asarray(CCTS_11_WEEK_1_1), np.asarray(CCTS_11_WEEK_1_2))


			# round off values to 4

			PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)
			
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)

			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			GAD7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)
			
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)

			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)


			HOPE_CHANGE_BASELINE_TO_WEEK_1_1_MEAN = round(HOPE_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 4)
			HOPE_CHANGE_BASELINE_TO_WEEK_1_1_STD = round(HOPE_CHANGE_BASELINE_TO_WEEK_1_1_STD, 4)
			HOPE_CHANGE_BASELINE_TO_WEEK_1_2_MEAN = round(HOPE_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 4)
			HOPE_CHANGE_BASELINE_TO_WEEK_1_2_STD = round(HOPE_CHANGE_BASELINE_TO_WEEK_1_2_STD, 4)
			HOPE_CHANGE_BASELINE_TO_WEEK_1_P_VALUE = round(HOPE_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 4)
			# HOPE_CHANGE_BASELINE_TO_WEEK_1_COHEN_D = round(HOPE_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 4)

			EM_1_WEEK_1_1_MEAN = round(EM_1_WEEK_1_1_MEAN, 4)
			EM_1_WEEK_1_1_STD = round(EM_1_WEEK_1_1_STD, 4)
			EM_1_WEEK_1_2_MEAN = round(EM_1_WEEK_1_2_MEAN, 4)
			EM_1_WEEK_1_2_STD = round(EM_1_WEEK_1_2_STD, 4)
			EM_1_WEEK_1_P_VALUE = round(EM_1_WEEK_1_P_VALUE, 4)
			# EM_1_WEEK_1_COHEN_D = round(EM_1_WEEK_1_COHEN_D, 4)


			EM_2_WEEK_1_1_MEAN = round(EM_2_WEEK_1_1_MEAN, 4)
			EM_2_WEEK_1_1_STD = round(EM_2_WEEK_1_1_STD, 4)
			EM_2_WEEK_1_2_MEAN = round(EM_2_WEEK_1_2_MEAN, 4)
			EM_2_WEEK_1_2_STD = round(EM_2_WEEK_1_2_STD, 4)
			EM_2_WEEK_1_P_VALUE = round(EM_2_WEEK_1_P_VALUE, 4)
			# EM_2_WEEK_1_COHEN_D = round(EM_2_WEEK_1_COHEN_D, 4)


			EM_3_WEEK_1_1_MEAN = round(EM_3_WEEK_1_1_MEAN, 4)
			EM_3_WEEK_1_1_STD = round(EM_3_WEEK_1_1_STD, 4)
			EM_3_WEEK_1_2_MEAN = round(EM_3_WEEK_1_2_MEAN, 4)
			EM_3_WEEK_1_2_STD = round(EM_3_WEEK_1_2_STD, 4)
			EM_3_WEEK_1_P_VALUE = round(EM_3_WEEK_1_P_VALUE, 4)
			# EM_3_WEEK_1_COHEN_D = round(EM_3_WEEK_1_COHEN_D, 4)


			EM_4_WEEK_1_1_MEAN = round(EM_4_WEEK_1_1_MEAN, 4)
			EM_4_WEEK_1_1_STD = round(EM_4_WEEK_1_1_STD, 4)
			EM_4_WEEK_1_2_MEAN = round(EM_4_WEEK_1_2_MEAN, 4)
			EM_4_WEEK_1_2_STD = round(EM_4_WEEK_1_2_STD, 4)
			EM_4_WEEK_1_P_VALUE = round(EM_4_WEEK_1_P_VALUE, 4)
			# EM_4_WEEK_1_COHEN_D = round(EM_4_WEEK_1_COHEN_D, 4)


			EM_5_WEEK_1_1_MEAN = round(EM_5_WEEK_1_1_MEAN, 4)
			EM_5_WEEK_1_1_STD = round(EM_5_WEEK_1_1_STD, 4)
			EM_5_WEEK_1_2_MEAN = round(EM_5_WEEK_1_2_MEAN, 4)
			EM_5_WEEK_1_2_STD = round(EM_5_WEEK_1_2_STD, 4)
			EM_5_WEEK_1_P_VALUE = round(EM_5_WEEK_1_P_VALUE, 4)
			# EM_5_WEEK_1_COHEN_D = round(EM_5_WEEK_1_COHEN_D, 4)


			EM_6_WEEK_1_1_MEAN = round(EM_6_WEEK_1_1_MEAN, 4)
			EM_6_WEEK_1_1_STD = round(EM_6_WEEK_1_1_STD, 4)
			EM_6_WEEK_1_2_MEAN = round(EM_6_WEEK_1_2_MEAN, 4)
			EM_6_WEEK_1_2_STD = round(EM_6_WEEK_1_2_STD, 4)
			EM_6_WEEK_1_P_VALUE = round(EM_6_WEEK_1_P_VALUE, 4)
			# EM_6_WEEK_1_COHEN_D = round(EM_6_WEEK_1_COHEN_D, 4)


			CCTS_20_WEEK_1_1_MEAN = round(CCTS_20_WEEK_1_1_MEAN, 4)
			CCTS_20_WEEK_1_1_STD = round(CCTS_20_WEEK_1_1_STD, 4)
			CCTS_20_WEEK_1_2_MEAN = round(CCTS_20_WEEK_1_2_MEAN, 4)
			CCTS_20_WEEK_1_2_STD = round(CCTS_20_WEEK_1_2_STD, 4)
			CCTS_20_WEEK_1_P_VALUE = round(CCTS_20_WEEK_1_P_VALUE, 4)
			# CCTS_20_WEEK_1_COHEN_D = round(CCTS_20_WEEK_1_COHEN_D, 4)


			CCTS_28_WEEK_1_1_MEAN = round(CCTS_28_WEEK_1_1_MEAN, 4)
			CCTS_28_WEEK_1_1_STD = round(CCTS_28_WEEK_1_1_STD, 4)
			CCTS_28_WEEK_1_2_MEAN = round(CCTS_28_WEEK_1_2_MEAN, 4)
			CCTS_28_WEEK_1_2_STD = round(CCTS_28_WEEK_1_2_STD, 4)
			CCTS_28_WEEK_1_P_VALUE = round(CCTS_28_WEEK_1_P_VALUE, 4)
			# CCTS_28_WEEK_1_COHEN_D = round(CCTS_28_WEEK_1_COHEN_D, 4)


			CCTS_21_WEEK_1_1_MEAN = round(CCTS_21_WEEK_1_1_MEAN, 4)
			CCTS_21_WEEK_1_1_STD = round(CCTS_21_WEEK_1_1_STD, 4)
			CCTS_21_WEEK_1_2_MEAN = round(CCTS_21_WEEK_1_2_MEAN, 4)
			CCTS_21_WEEK_1_2_STD = round(CCTS_21_WEEK_1_2_STD, 4)
			CCTS_21_WEEK_1_P_VALUE = round(CCTS_21_WEEK_1_P_VALUE, 4)
			# CCTS_21_WEEK_1_COHEN_D = round(CCTS_21_WEEK_1_COHEN_D, 4)


			CCTS_06_WEEK_1_1_MEAN = round(CCTS_06_WEEK_1_1_MEAN, 4)
			CCTS_06_WEEK_1_1_STD = round(CCTS_06_WEEK_1_1_STD, 4)
			CCTS_06_WEEK_1_2_MEAN = round(CCTS_06_WEEK_1_2_MEAN, 4)
			CCTS_06_WEEK_1_2_STD = round(CCTS_06_WEEK_1_2_STD, 4)
			CCTS_06_WEEK_1_P_VALUE = round(CCTS_06_WEEK_1_P_VALUE, 4)
			# CCTS_06_WEEK_1_COHEN_D = round(CCTS_06_WEEK_1_COHEN_D, 4)


			CCTS_24_WEEK_1_1_MEAN = round(CCTS_24_WEEK_1_1_MEAN, 4)
			CCTS_24_WEEK_1_1_STD = round(CCTS_24_WEEK_1_1_STD, 4)
			CCTS_24_WEEK_1_2_MEAN = round(CCTS_24_WEEK_1_2_MEAN, 4)
			CCTS_24_WEEK_1_2_STD = round(CCTS_24_WEEK_1_2_STD, 4)
			CCTS_24_WEEK_1_P_VALUE = round(CCTS_24_WEEK_1_P_VALUE, 4)
			# CCTS_24_WEEK_1_COHEN_D = round(CCTS_24_WEEK_1_COHEN_D, 4)


			CCTS_11_WEEK_1_1_MEAN = round(CCTS_11_WEEK_1_1_MEAN, 4)
			CCTS_11_WEEK_1_1_STD = round(CCTS_11_WEEK_1_1_STD, 4)
			CCTS_11_WEEK_1_2_MEAN = round(CCTS_11_WEEK_1_2_MEAN, 4)
			CCTS_11_WEEK_1_2_STD = round(CCTS_11_WEEK_1_2_STD, 4)
			CCTS_11_WEEK_1_P_VALUE = round(CCTS_11_WEEK_1_P_VALUE, 4)
			# CCTS_11_WEEK_1_COHEN_D = round(CCTS_11_WEEK_1_COHEN_D, 4)










			# return baseline and week 1 values
			# return render(request, 'admin_dashboard.html', {})

			# return mean, std, pvalue, and cohen's d

			return render(request, "study/statistics.html", {'reframe_relatability_1': reframe_relatability_1, 'reframe_relatability_2': reframe_relatability_2, 'reframe_helpfulness_1': reframe_helpfulness_1, 'reframe_helpfulness_2': reframe_helpfulness_2, 'reframe_memorability_1': reframe_memorability_1, 'reframe_memorability_2': reframe_memorability_2, 'reframe_learnability_1': reframe_learnability_1, 'reframe_learnability_2': reframe_learnability_2, 'reframe_relatibility_p_value': reframe_relatibility_p_value, 'reframe_helpfulness_p_value': reframe_helpfulness_p_value, 'reframe_memorability_p_value': reframe_memorability_p_value, 'reframe_learnability_p_value': reframe_learnability_p_value, 'reframe_relatibility_cohen_d': reframe_relatibility_cohen_d, 'reframe_helpfulness_cohen_d': reframe_helpfulness_cohen_d, 'reframe_memorability_cohen_d': reframe_memorability_cohen_d, 'reframe_learnability_cohen_d': reframe_learnability_cohen_d, 'belief_change_1': belief_change_1, 'belief_change_2': belief_change_2, 'emotion_change_1': emotion_change_1, 'emotion_change_2': emotion_change_2, 'belief_change_p_value': belief_change_p_value, 'emotion_change_p_value': emotion_change_p_value, 'belief_change_cohen_d': belief_change_cohen_d, 'emotion_change_cohen_d': emotion_change_cohen_d, 'N_1': N_1, 'N_2': N_2, 'PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q8_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_STD': PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_STD': PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': PHQ9_Q9_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q1_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q2_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q3_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q4_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q5_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q6_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD': GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD': GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': GAD7_Q7_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'HOPE_CHANGE_BASELINE_TO_WEEK_1_1_MEAN': HOPE_CHANGE_BASELINE_TO_WEEK_1_1_MEAN, 'HOPE_CHANGE_BASELINE_TO_WEEK_1_1_STD': HOPE_CHANGE_BASELINE_TO_WEEK_1_1_STD, 'HOPE_CHANGE_BASELINE_TO_WEEK_1_2_MEAN': HOPE_CHANGE_BASELINE_TO_WEEK_1_2_MEAN, 'HOPE_CHANGE_BASELINE_TO_WEEK_1_2_STD': HOPE_CHANGE_BASELINE_TO_WEEK_1_2_STD, 'HOPE_CHANGE_BASELINE_TO_WEEK_1_P_VALUE': HOPE_CHANGE_BASELINE_TO_WEEK_1_P_VALUE, 'HOPE_CHANGE_BASELINE_TO_WEEK_1_COHEN_D': HOPE_CHANGE_BASELINE_TO_WEEK_1_COHEN_D, 'EM_1_WEEK_1_1_MEAN': EM_1_WEEK_1_1_MEAN, 'EM_1_WEEK_1_1_STD': EM_1_WEEK_1_1_STD, 'EM_1_WEEK_1_2_MEAN': EM_1_WEEK_1_2_MEAN, 'EM_1_WEEK_1_2_STD': EM_1_WEEK_1_2_STD, 'EM_1_WEEK_1_P_VALUE': EM_1_WEEK_1_P_VALUE, 'EM_1_WEEK_1_COHEN_D': EM_1_WEEK_1_COHEN_D, 'EM_2_WEEK_1_1_MEAN': EM_2_WEEK_1_1_MEAN, 'EM_2_WEEK_1_1_STD': EM_2_WEEK_1_1_STD, 'EM_2_WEEK_1_2_MEAN': EM_2_WEEK_1_2_MEAN, 'EM_2_WEEK_1_2_STD': EM_2_WEEK_1_2_STD, 'EM_2_WEEK_1_P_VALUE': EM_2_WEEK_1_P_VALUE, 'EM_2_WEEK_1_COHEN_D': EM_2_WEEK_1_COHEN_D, 'EM_3_WEEK_1_1_MEAN': EM_3_WEEK_1_1_MEAN, 'EM_3_WEEK_1_1_STD': EM_3_WEEK_1_1_STD, 'EM_3_WEEK_1_2_MEAN': EM_3_WEEK_1_2_MEAN, 'EM_3_WEEK_1_2_STD': EM_3_WEEK_1_2_STD, 'EM_3_WEEK_1_P_VALUE': EM_3_WEEK_1_P_VALUE, 'EM_3_WEEK_1_COHEN_D': EM_3_WEEK_1_COHEN_D, 'EM_4_WEEK_1_1_MEAN': EM_4_WEEK_1_1_MEAN, 'EM_4_WEEK_1_1_STD': EM_4_WEEK_1_1_STD, 'EM_4_WEEK_1_2_MEAN': EM_4_WEEK_1_2_MEAN, 'EM_4_WEEK_1_2_STD': EM_4_WEEK_1_2_STD, 'EM_4_WEEK_1_P_VALUE': EM_4_WEEK_1_P_VALUE, 'EM_4_WEEK_1_COHEN_D': EM_4_WEEK_1_COHEN_D, 'EM_5_WEEK_1_1_MEAN': EM_5_WEEK_1_1_MEAN, 'EM_5_WEEK_1_1_STD': EM_5_WEEK_1_1_STD, 'EM_5_WEEK_1_2_MEAN': EM_5_WEEK_1_2_MEAN, 'EM_5_WEEK_1_2_STD': EM_5_WEEK_1_2_STD, 'EM_5_WEEK_1_P_VALUE': EM_5_WEEK_1_P_VALUE, 'EM_5_WEEK_1_COHEN_D': EM_5_WEEK_1_COHEN_D, 'EM_6_WEEK_1_1_MEAN': EM_6_WEEK_1_1_MEAN, 'EM_6_WEEK_1_1_STD': EM_6_WEEK_1_1_STD, 'EM_6_WEEK_1_2_MEAN': EM_6_WEEK_1_2_MEAN, 'EM_6_WEEK_1_2_STD': EM_6_WEEK_1_2_STD, 'EM_6_WEEK_1_P_VALUE': EM_6_WEEK_1_P_VALUE, 'EM_6_WEEK_1_COHEN_D': EM_6_WEEK_1_COHEN_D, 'CCTS_20_WEEK_1_1_MEAN': CCTS_20_WEEK_1_1_MEAN, 'CCTS_20_WEEK_1_1_STD': CCTS_20_WEEK_1_1_STD, 'CCTS_20_WEEK_1_2_MEAN': CCTS_20_WEEK_1_2_MEAN, 'CCTS_20_WEEK_1_2_STD': CCTS_20_WEEK_1_2_STD, 'CCTS_20_WEEK_1_P_VALUE': CCTS_20_WEEK_1_P_VALUE, 'CCTS_20_WEEK_1_COHEN_D': CCTS_20_WEEK_1_COHEN_D, 'CCTS_28_WEEK_1_1_MEAN': CCTS_28_WEEK_1_1_MEAN, 'CCTS_28_WEEK_1_1_STD': CCTS_28_WEEK_1_1_STD, 'CCTS_28_WEEK_1_2_MEAN': CCTS_28_WEEK_1_2_MEAN, 'CCTS_28_WEEK_1_2_STD': CCTS_28_WEEK_1_2_STD, 'CCTS_28_WEEK_1_P_VALUE': CCTS_28_WEEK_1_P_VALUE, 'CCTS_28_WEEK_1_COHEN_D': CCTS_28_WEEK_1_COHEN_D, 'CCTS_21_WEEK_1_1_MEAN': CCTS_21_WEEK_1_1_MEAN, 'CCTS_21_WEEK_1_1_STD': CCTS_21_WEEK_1_1_STD, 'CCTS_21_WEEK_1_2_MEAN': CCTS_21_WEEK_1_2_MEAN, 'CCTS_21_WEEK_1_2_STD': CCTS_21_WEEK_1_2_STD, 'CCTS_21_WEEK_1_P_VALUE': CCTS_21_WEEK_1_P_VALUE, 'CCTS_21_WEEK_1_COHEN_D': CCTS_21_WEEK_1_COHEN_D, 'CCTS_06_WEEK_1_1_MEAN': CCTS_06_WEEK_1_1_MEAN, 'CCTS_06_WEEK_1_1_STD': CCTS_06_WEEK_1_1_STD, 'CCTS_06_WEEK_1_2_MEAN': CCTS_06_WEEK_1_2_MEAN, 'CCTS_06_WEEK_1_2_STD': CCTS_06_WEEK_1_2_STD, 'CCTS_06_WEEK_1_P_VALUE': CCTS_06_WEEK_1_P_VALUE, 'CCTS_06_WEEK_1_COHEN_D': CCTS_06_WEEK_1_COHEN_D, 'CCTS_24_WEEK_1_1_MEAN': CCTS_24_WEEK_1_1_MEAN, 'CCTS_24_WEEK_1_1_STD': CCTS_24_WEEK_1_1_STD, 'CCTS_24_WEEK_1_2_MEAN': CCTS_24_WEEK_1_2_MEAN, 'CCTS_24_WEEK_1_2_STD': CCTS_24_WEEK_1_2_STD, 'CCTS_24_WEEK_1_P_VALUE': CCTS_24_WEEK_1_P_VALUE, 'CCTS_24_WEEK_1_COHEN_D': CCTS_24_WEEK_1_COHEN_D, 'CCTS_11_WEEK_1_1_MEAN': CCTS_11_WEEK_1_1_MEAN, 'CCTS_11_WEEK_1_1_STD': CCTS_11_WEEK_1_1_STD, 'CCTS_11_WEEK_1_2_MEAN': CCTS_11_WEEK_1_2_MEAN, 'CCTS_11_WEEK_1_2_STD': CCTS_11_WEEK_1_2_STD, 'CCTS_11_WEEK_1_P_VALUE': CCTS_11_WEEK_1_P_VALUE, 'CCTS_11_WEEK_1_COHEN_D': CCTS_11_WEEK_1_COHEN_D, 'N_1_SURVEY': N_1_SURVEY, 'N_2_SURVEY': N_2_SURVEY, 'N_1_PHQ9_SURVEY': N_1_PHQ9_SURVEY, 'N_2_PHQ9_SURVEY': N_2_PHQ9_SURVEY})

		else:
			return redirect('/study/error.html', {'error_msg': 'Error'})
	else:
		return redirect('/study/admin.html')



@login_required
def home(request):
	print('user:', request.user.username)

	# get study_id from UserDetails
	study_id = UserDetails.objects.filter(username = request.user.username)[0].study_id


	# sync redcap
	# redcap_sync(last_sync=True, login_sync=True)

	# check if Redcap_Consent exists
	if len(Redcap_Consent.objects.filter(study_id = study_id, consent_complete="2", consent_yn="1")) == 0:
		return redirect('/study/error.html', {'error_msg': 'Error'})

	# save homepage
	curr_homepage = Homepage(username = request.user.username)
	curr_homepage.save()

	

	# get user condiction from UserDetails
	condition = UserDetails.objects.filter(username = request.user.username)[0].condition

	# get week_1_start, week_1_expire, week_2_start, week_2_expire, week_3_start, week_3_expire, week_4_start, week_4_expire
	week_1_start = UserDetails.objects.filter(username = request.user.username)[0].week_1_start
	week_1_expire = UserDetails.objects.filter(username = request.user.username)[0].week_1_expire
	week_2_start = UserDetails.objects.filter(username = request.user.username)[0].week_2_start
	week_2_expire = UserDetails.objects.filter(username = request.user.username)[0].week_2_expire
	week_3_start = UserDetails.objects.filter(username = request.user.username)[0].week_3_start
	week_3_expire = UserDetails.objects.filter(username = request.user.username)[0].week_3_expire
	week_4_start = UserDetails.objects.filter(username = request.user.username)[0].week_4_start
	week_4_expire = UserDetails.objects.filter(username = request.user.username)[0].week_4_expire



	# get week_1_use, week_2_use, week_3_use, week_4_use
	week_1_use = UserDetails.objects.filter(username = request.user.username)[0].week_1_use
	week_2_use = UserDetails.objects.filter(username = request.user.username)[0].week_2_use
	week_3_use = UserDetails.objects.filter(username = request.user.username)[0].week_3_use
	week_4_use = UserDetails.objects.filter(username = request.user.username)[0].week_4_use

	week_1_remaining = 3 - week_1_use
	week_2_remaining = 3 - week_2_use
	week_3_remaining = 3 - week_3_use
	week_4_remaining = 3 - week_4_use

	# get survey_1_status, survey_2_status, survey_3_status, survey_4_status, survey_5_status, survey_8_status

	survey_1_status = UserDetails.objects.filter(username = request.user.username)[0].survey_1_status
	survey_2_status = UserDetails.objects.filter(username = request.user.username)[0].survey_2_status
	survey_3_status = UserDetails.objects.filter(username = request.user.username)[0].survey_3_status
	survey_4_status = UserDetails.objects.filter(username = request.user.username)[0].survey_4_status
	survey_5_status = UserDetails.objects.filter(username = request.user.username)[0].survey_5_status
	survey_8_status = UserDetails.objects.filter(username = request.user.username)[0].survey_8_status


	survey_1_start = week_1_start + datetime.timedelta(days = 6)
	survey_2_start = week_2_start + datetime.timedelta(days = 6)
	survey_3_start = week_3_start + datetime.timedelta(days = 6)
	survey_4_start = week_4_start + datetime.timedelta(days = 6)
	survey_5_start = week_1_start + datetime.timedelta(days = 28)
	survey_8_start = week_1_start + datetime.timedelta(days = 56)


	# check expired weeks

	# pacific timezone

	curr_datetime = datetime.datetime.now()
	curr_datetime = curr_datetime.astimezone(timezone('US/Pacific'))

	if curr_datetime > week_1_expire and week_1_remaining > 0:
		week_1_status = 'expired'
	elif curr_datetime > week_1_start and week_1_remaining <= 0:
		week_1_status = 'completed'
	elif curr_datetime > week_1_start and week_1_remaining > 0:
		week_1_status = 'active'
	else:
		week_1_status = 'TBA'

	if curr_datetime > week_2_expire and week_2_remaining > 0:
		week_2_status = 'expired'
	elif curr_datetime > week_2_start and week_2_remaining <= 0:
		week_2_status = 'completed'
	elif curr_datetime > week_2_start and week_2_remaining > 0:
		week_2_status = 'active'
	else:
		week_2_status = 'TBA'

	if curr_datetime > week_3_expire and week_3_remaining > 0:
		week_3_status = 'expired'
	elif curr_datetime > week_3_start and week_3_remaining <= 0:
		week_3_status = 'completed'
	elif curr_datetime > week_3_start and week_3_remaining > 0:
		week_3_status = 'active'
	else:
		week_3_status = 'TBA'
	
	if curr_datetime > week_4_expire and week_4_remaining > 0:
		week_4_status = 'expired'
	elif curr_datetime > week_4_start and week_4_remaining <= 0:
		week_4_status = 'completed'
	elif curr_datetime > week_4_start and week_4_remaining > 0:
		week_4_status = 'active'
	else:
		week_4_status = 'TBA'


	total_earnings = 0
	total_remaining_earnings = 0
	total_possible_earnings = 0

	if week_1_status == 'TBA' or week_1_status == 'active':
		total_possible_earnings += 5
	elif week_1_status == 'completed':
		total_earnings += 5
		total_possible_earnings += 5

	if week_2_status == 'TBA' or week_2_status == 'active':
		total_possible_earnings += 5
	elif week_2_status == 'completed':
		total_earnings += 5
		total_possible_earnings += 5

	
	if week_3_status == 'TBA' or week_3_status == 'active':
		total_possible_earnings += 5
	elif week_3_status == 'completed':
		total_earnings += 5
		total_possible_earnings += 5

	if week_4_status == 'TBA' or week_4_status == 'active':
		total_possible_earnings += 5
	elif week_4_status == 'completed':
		total_earnings += 5
		total_possible_earnings += 5

	
	if survey_1_status == 1:
		total_earnings += 5
		total_possible_earnings += 5
	else:
		total_possible_earnings += 5
	
	if survey_2_status == 1:
		total_earnings += 5
		total_possible_earnings += 5
	else:
		total_possible_earnings += 5
	
	if survey_3_status == 1:
		total_earnings += 5
		total_possible_earnings += 5
	else:
		total_possible_earnings += 5
	
	if survey_4_status == 1:
		total_earnings += 5
		total_possible_earnings += 5
	else:
		total_possible_earnings += 5
	
	if survey_5_status == 1:
		total_earnings += 10
		total_possible_earnings += 10
	else:
		total_possible_earnings += 10

	if survey_8_status == 1:
		total_earnings += 10
		total_possible_earnings += 10
	else:
		total_possible_earnings += 10
	
	total_remaining_earnings = total_possible_earnings - total_earnings

	week_1_start = week_1_start.astimezone(timezone('US/Pacific'))
	week_1_expire = week_1_expire.astimezone(timezone('US/Pacific'))
	week_2_start = week_2_start.astimezone(timezone('US/Pacific'))
	week_2_expire = week_2_expire.astimezone(timezone('US/Pacific'))
	week_3_start = week_3_start.astimezone(timezone('US/Pacific'))
	week_3_expire = week_3_expire.astimezone(timezone('US/Pacific'))
	week_4_start = week_4_start.astimezone(timezone('US/Pacific'))
	week_4_expire = week_4_expire.astimezone(timezone('US/Pacific'))

	survey_1_start = survey_1_start.astimezone(timezone('US/Pacific'))
	survey_2_start = survey_2_start.astimezone(timezone('US/Pacific'))
	survey_3_start = survey_3_start.astimezone(timezone('US/Pacific'))
	survey_4_start = survey_4_start.astimezone(timezone('US/Pacific'))
	survey_5_start = survey_5_start.astimezone(timezone('US/Pacific'))
	survey_8_start = survey_8_start.astimezone(timezone('US/Pacific'))

	

	# format as as Monday, Oct 2, 9:13 AM
	week_1_start = week_1_start.strftime('%A, %b %d, %I:%M %p')
	week_1_expire = week_1_expire.strftime('%A, %b %d, %I:%M %p')
	week_2_start = week_2_start.strftime('%A, %b %d, %I:%M %p')
	week_2_expire = week_2_expire.strftime('%A, %b %d, %I:%M %p')
	week_3_start = week_3_start.strftime('%A, %b %d, %I:%M %p')
	week_3_expire = week_3_expire.strftime('%A, %b %d, %I:%M %p')
	week_4_start = week_4_start.strftime('%A, %b %d, %I:%M %p')
	week_4_expire = week_4_expire.strftime('%A, %b %d, %I:%M %p')

	survey_1_start = survey_1_start.strftime('%A, %b %d, %I:%M %p')
	survey_2_start = survey_2_start.strftime('%A, %b %d, %I:%M %p')
	survey_3_start = survey_3_start.strftime('%A, %b %d, %I:%M %p')
	survey_4_start = survey_4_start.strftime('%A, %b %d, %I:%M %p')
	survey_5_start = survey_5_start.strftime('%A, %b %d, %I:%M %p')
	survey_8_start = survey_8_start.strftime('%A, %b %d, %I:%M %p')

	# convert to US/Pacific timezone


	print('week_1_expire:', week_1_expire)
	print('week_2_expire:', week_2_expire)
	print('week_3_expire:', week_3_expire)
	print('week_4_expire:', week_4_expire)

	# Get all thought records

	thought_records = ThoughtRecord.objects.filter(username = request.user.username)

	# get thought_record_ids

	thought_record_ids = []
	thought_records_li = []

	for elem in thought_records:
		thought_record_ids.append(elem.thought_record_id)
		thought_records_li.append([elem.created_at, elem.thought_record_id, elem.username])

	# get thoughts, situations, emotions, thinking_trap_selected, reframe_final with thought_record_ids

	thoughts = Thought.objects.filter(thought_record_id__in = thought_record_ids)
	situations = Situation.objects.filter(thought_record_id__in = thought_record_ids)
	emotions = Emotion.objects.filter(thought_record_id__in = thought_record_ids)
	thinking_trap_selected = Thinking_Trap_Selected.objects.filter(thought_record_id__in = thought_record_ids)
	reframe_final = Reframe_Final.objects.filter(thought_record_id__in = thought_record_ids)


	# merge thought_records, thoughts, situations, emotions, thinking_trap_selected, reframe_final on created_at, thought_record_id and get the thought_record_id, thought, situation, emotion, thinking_trap_selected, reframe_final
	
	thoughts_li = []

	for elem in thoughts:
		thoughts_li.append([elem.thought_record_id, elem.thought,])

	situations_li = []

	for elem in situations:
		situations_li.append([elem.thought_record_id, elem.situation,])
	
	emotions_li = []

	for elem in emotions:
		emotions_li.append([elem.thought_record_id, elem.belief, elem.emotion, elem.emotion_strength,])
	
	thinking_trap_selected_li = []

	for elem in thinking_trap_selected:
		thinking_trap_selected_li.append([elem.thought_record_id, elem.thinking_trap_selected,])
	
	reframe_final_li = []

	for elem in reframe_final:
		reframe_final_li.append([elem.thought_record_id, elem.reframe_final,])

	# create_df

	thought_records_df = pd.DataFrame(thought_records_li, columns = ['created_at', 'thought_record_id', 'username'])
	thoughts_df = pd.DataFrame(thoughts_li, columns = ['thought_record_id', 'thought'])
	situations_df = pd.DataFrame(situations_li, columns = ['thought_record_id', 'situation'])
	emotions_df = pd.DataFrame(emotions_li, columns = ['thought_record_id', 'belief', 'emotion', 'emotion_strength'])
	thinking_trap_selected_df = pd.DataFrame(thinking_trap_selected_li, columns = ['thought_record_id', 'thinking_trap_selected'])
	reframe_final_df = pd.DataFrame(reframe_final_li, columns = ['thought_record_id', 'reframe_final'])


	# merge

	thought_records_df = pd.merge(thought_records_df, thoughts_df, on = 'thought_record_id', how = 'inner')
	thought_records_df = pd.merge(thought_records_df, situations_df, on = 'thought_record_id', how = 'inner')
	thought_records_df = pd.merge(thought_records_df, emotions_df, on = 'thought_record_id', how = 'inner')
	thought_records_df = pd.merge(thought_records_df, thinking_trap_selected_df, on = 'thought_record_id', how = 'inner')
	thought_records_df = pd.merge(thought_records_df, reframe_final_df, on = 'thought_record_id', how = 'inner')

	# sort by created_at reverse
	thought_records_df = thought_records_df.sort_values(by = ['created_at'], ascending = False)

	# deduplicate 
	thought_records_df = thought_records_df.drop_duplicates(subset = ['thought_record_id'], keep = 'first')

	# keep created_at, thought_record_id, thought, situation, emotion, thinking_trap_selected, reframe_final

	thought_records_df = thought_records_df[['created_at', 'thought_record_id', 'thought', 'situation', 'belief', 'emotion', 'emotion_strength', 'thinking_trap_selected', 'reframe_final']]

	# format created_at as Monday, Oct 2, 9:13 AM

	thought_records_df['created_at'] = pd.to_datetime(thought_records_df['created_at'])
	# localize to PT

	if len(thought_records_df) > 0:
		thought_records_df['created_at'] = thought_records_df['created_at'].dt.tz_convert('US/Pacific')

		thought_records_df['created_at'] = thought_records_df['created_at'].dt.strftime('%A, %b %d, %I:%M %p')

	# convert df to a list of dictionaries

	thought_records_dict = thought_records_df.to_dict('records')

	print('condition:', condition)


	return render(request, 'study/home.html', {'total_earnings': total_earnings, 'total_possible_earnings': total_possible_earnings, 'total_remaining_earnings': total_remaining_earnings, 'thought_records_dict': thought_records_dict, 'username': request.user.username, 'condition': condition, 'week_1_start': week_1_start, 'week_1_expire': week_1_expire, 'week_2_start': week_2_start, 'week_2_expire': week_2_expire, 'week_3_start': week_3_start, 'week_3_expire': week_3_expire, 'week_4_start': week_4_start, 'week_4_expire': week_4_expire, 'week_1_status': week_1_status, 'week_2_status': week_2_status, 'week_3_status': week_3_status, 'week_4_status': week_4_status, 'week_1_remaining': week_1_remaining, 'week_2_remaining': week_2_remaining, 'week_3_remaining': week_3_remaining, 'week_4_remaining': week_4_remaining, 'survey_1_status': survey_1_status, 'survey_2_status': survey_2_status, 'survey_3_status': survey_3_status, 'survey_4_status': survey_4_status, 'survey_5_status': survey_5_status, 'survey_8_status': survey_8_status, 'survey_1_start': survey_1_start, 'survey_2_start': survey_2_start, 'survey_3_start': survey_3_start, 'survey_4_start': survey_4_start, 'survey_5_start': survey_5_start, 'survey_8_start': survey_8_start, 'week_1_use': week_1_use, 'week_2_use': week_2_use, 'week_3_use': week_3_use, 'week_4_use': week_4_use})



'''
OpenAI API
'''
import openai
# openai.organization = "org-o2Ssn2MTYvpMDkvzRSiehlv4"
openai.api_key = os.getenv("OPENAI_API_KEY")

from study.definitions import *
from study.prompts import *
from study.themes_prompt import *
from study.themes_prompt_new import *
from study.themes_prompt_v3 import *


COLORS = ["#fa6767"]

def get_ip_address(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	else:
		ip = request.META.get('REMOTE_ADDR')

	if ':' in ip:
		ip, _ = ip.split(':', 1)
	
	# MD5 hash
	ip = hashlib.md5(ip.encode('utf-8')).hexdigest()
	return ip

def extract_category(s):
	for idx, elem in enumerate(CATEGORIES_PREFIX):
		if s.lower().strip().startswith(elem.lower()):
			return CATEGORIES[idx]
	print('Error', s)


def extract_category_distribution(curr_dict):
	curr_choices = curr_dict['choices'][0]['logprobs']['top_logprobs'][0]
	
	distr_li = {}
	
	for choice in curr_choices:
		for idx, elem in enumerate(CATEGORIES_PREFIX):
			if elem.lower().startswith(choice.lower().strip()):
				if CATEGORIES[idx] not in distr_li:
					distr_li[CATEGORIES[idx]] = 0.0
				distr_li[CATEGORIES[idx]] = max(np.exp(curr_choices[choice]), distr_li[CATEGORIES[idx]])

	return distr_li


def extract_category_theme(s):
	for idx, elem in enumerate(THEMES_CATEGORIES_PREFIX):
		if s.lower().strip().startswith(elem.lower()):
			return THEMES_CATEGORIES[idx]
	print('Error', s)


def extract_category_distribution_theme(curr_dict):
	curr_choices = curr_dict['choices'][0]['logprobs']['top_logprobs'][0]
	
	distr_li = {}
	
	for choice in curr_choices:
		for idx, elem in enumerate(THEMES_CATEGORIES_PREFIX):
			if elem.lower().startswith(choice.lower().strip()):
				if THEMES_CATEGORIES[idx] not in distr_li:
					distr_li[THEMES_CATEGORIES[idx]] = 0.0
				distr_li[THEMES_CATEGORIES[idx]] = max(np.exp(curr_choices[choice]), distr_li[THEMES_CATEGORIES[idx]])

	return distr_li


def pretty_print(s):
	names = ['i', "i'm", "i'll", "i've", "i'd",]
	output_str = ' '.join([word.capitalize() if word in names else word for word in s.split()])
	return output_str


def safety_filter(candidate: str) -> str:
	for word in FLAG_LIST:
		# check if word is in candidate
		if candidate.strip().lower().startswith(word.strip().lower() + ' '):
			return 1
		if candidate.strip().lower().endswith(' ' + word.strip().lower()):
			return 1
		if ' ' + word.strip().lower() + ' ' in candidate.strip().lower():
			return 1
	return 0


headers = {
	'Content-type': 'application/json',
	'Cross-domain': 'true',	
}


def error_message(request):
	return render(request, "study/error.html", {'error_msg': 'Error'})

@login_required
def RCT(request):
	if request.method == 'POST':
		condition = request.POST.get('condition', None)

	elif request.method == 'GET':
		condition = request.GET.get('condition', None)

	print('condition:', condition)
	
	if condition == '2':
		return redirect('/study/index.html')
	elif condition == '1':
		return redirect('/study/tool_use.html')
	else:
		return redirect('/study/error.html')

@login_required
def index(request):

	# check user condition
	condition = UserDetails.objects.filter(username = request.user.username)[0].condition

	if condition != '2':
		return redirect('/study/error.html')

	# compute current week num for the user
	curr_date = datetime.datetime.now().astimezone(timezone('US/Pacific'))

	# get date_started from UserDetails
	date_started = UserDetails.objects.filter(username = request.user.username)[0].week_1_start

	# compute week_no
	week_no = (curr_date - date_started).days // 7 + 1

	print('week_no:', week_no)
	

	referral_code = request.GET.get('referral_code', '')
	skip_step = request.GET.get('skip_step', None)

	prompt_to_use = request.GET.get('prompt_to_use', None)
	more_suggestions_btn = request.GET.get('more_suggestions_btn', None)

	descriptive_thought_Q = request.GET.get('descriptive_thought_Q', None)

	multiple_cognitive_distortions = request.GET.get('multiple_cognitive_distortions', None)

	A_A = request.GET.get('A_A', None)

	extra_q = request.GET.get('extra_q', None)	

	emotion_questions = request.GET.get('emotion_questions', None)

	personalize = request.GET.get('personalize', None)
	readable = request.GET.get('readable', None)

	include_emotions = request.GET.get('include_emotions', None)

	psychoeducation = request.GET.get('psychoeducation', None)

	# Randomly assign remove_negative_feeling

	refresh_btn = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	remove_negative_feeling = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	ai = 1

	if prompt_to_use == None:
		prompt_to_use = 'expert_v3_gpt4' #np.random.choice(['expert_v3_gpt3', 'expert_v3_gpt4'], p=[0.5, 0.5])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = 1 # np.random.choice([0, 1], p=[0.5, 0.5])

	if extra_q == None:
		extra_q = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		extra_q = int(extra_q)

	if emotion_questions == None:
		emotion_questions = 'second' # np.random.choice(['first', 'second'], p=[0.5, 0.5])

	if personalize == None:
		personalize = 1 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		personalize = int(personalize)
	
	if readable == None:
		readable = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		readable = int(readable)

	if include_emotions == None:
		include_emotions = np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		include_emotions = int(include_emotions)

	if psychoeducation == None:
		psychoeducation = 1 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		psychoeducation = int(psychoeducation)

	if skip_step == None:
		skip_step = '9' # np.random.choice(['0', '3'], p=[0.5, 0.5])

		if skip_step == '0':
			skip_step = None

	# remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

	skip_step_li = []

	if skip_step:
		skip_step_li_str = skip_step.strip().split(',')
		skip_step_li = [int(elem) for elem in skip_step_li_str]
	else:
		skip_step = ''

	if descriptive_thought_Q == None:
		descriptive_thought_Q = 0

	# if descriptive_thought_Q == None:
	# 	if 3 in skip_step_li:
	# 		descriptive_thought_Q = np.random.choice([0, 1], p=[0.5, 0.5])
	
	# Count number of skipped steps
	num_skipped_steps = 0

	emotion_step_no = 2
	situation_step_no = 3
	thinking_trap_step_no = 4
	reframe_step_no = 5
	evaluate_step_no = 6

	for elem in skip_step_li:
		if elem in {1, 2, 3, 4}:
			num_skipped_steps += 1

		if elem == 2:
			situation_step_no -= 1
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 3:
			situation_step_no -= 1
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 4:
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1


	total_steps = 6 - num_skipped_steps


	curr_thought_record = ThoughtRecord(username = request.user.username, week_no = week_no, referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
	
	curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "study/index.html", {'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation, 'ai': ai, 'include_emotions': include_emotions})


@login_required
def tool_use(request):

	# check user condition
	condition = UserDetails.objects.filter(username = request.user.username)[0].condition

	if condition != '1':
		return redirect('/study/error.html')

	# compute current week num for the user
	curr_date = datetime.datetime.now().astimezone(timezone('US/Pacific'))


	# date_started = '2023-11-21 00:01:00+00'
	# date_started = datetime.datetime.strptime(date_started, '%Y-%m-%d %H:%M:%S+00')

	# get date_started from UserDetails
	date_started = UserDetails.objects.filter(username = request.user.username)[0].week_1_start

	# compute week_no
	week_no = (curr_date - date_started).days // 7 + 1

	print('week_no:', week_no)
	

	referral_code = request.GET.get('referral_code', '')
	skip_step = request.GET.get('skip_step', None)

	prompt_to_use = request.GET.get('prompt_to_use', None)
	more_suggestions_btn = request.GET.get('more_suggestions_btn', None)

	descriptive_thought_Q = request.GET.get('descriptive_thought_Q', None)

	multiple_cognitive_distortions = request.GET.get('multiple_cognitive_distortions', None)

	A_A = request.GET.get('A_A', None)

	extra_q = request.GET.get('extra_q', None)	

	emotion_questions = request.GET.get('emotion_questions', None)

	personalize = request.GET.get('personalize', None)
	readable = request.GET.get('readable', None)

	psychoeducation = request.GET.get('psychoeducation', None)

	# Randomly assign remove_negative_feeling

	refresh_btn = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	remove_negative_feeling = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	ai = 2

	if prompt_to_use == None:
		prompt_to_use = 'expert_new' #np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = 1 # np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = 1 # np.random.choice([0, 1], p=[0.5, 0.5])

	if extra_q == None:
		extra_q = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		extra_q = int(extra_q)

	if emotion_questions == None:
		emotion_questions = 'second' # np.random.choice(['first', 'second'], p=[0.5, 0.5])

	if personalize == None:
		personalize = 1 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		personalize = int(personalize)
	
	if readable == None:
		readable = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		readable = int(readable)

	if psychoeducation == None:
		psychoeducation = 1 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		psychoeducation = int(psychoeducation)

	if skip_step == None:
		skip_step = '9' # np.random.choice(['0', '3'], p=[0.5, 0.5])

		if skip_step == '0':
			skip_step = None

	# remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

	skip_step_li = []

	if skip_step:
		skip_step_li_str = skip_step.strip().split(',')
		skip_step_li = [int(elem) for elem in skip_step_li_str]
	else:
		skip_step = ''

	if descriptive_thought_Q == None:
		descriptive_thought_Q = 0

	# if descriptive_thought_Q == None:
	# 	if 3 in skip_step_li:
	# 		descriptive_thought_Q = np.random.choice([0, 1], p=[0.5, 0.5])
	
	# Count number of skipped steps
	num_skipped_steps = 0

	emotion_step_no = 2
	situation_step_no = 3
	thinking_trap_step_no = 4
	reframe_step_no = 5
	evaluate_step_no = 6

	for elem in skip_step_li:
		if elem in {1, 2, 3, 4}:
			num_skipped_steps += 1

		if elem == 2:
			situation_step_no -= 1
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 3:
			situation_step_no -= 1
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 4:
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1


	total_steps = 6 - num_skipped_steps
	


	curr_thought_record = ThoughtRecord(username = request.user.username, week_no = week_no, referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai)
	curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "study/tool_use.html", {'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation, 'ai': ai})




def save_consent(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', -1)
		# user_id = request.GET.get('user_id', -1)

		# curr_consent = Consent(thought_record_id=int(thought_record_id), user_id = int(user_id), consent_obtained=1)
		# curr_consent.save()

		return JsonResponse({'upload': 'successful',}, safe=False)


def save_steps_logs(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', -1)
		step_number_from = request.GET.get('step_number_from', -1)
		step_number_to = request.GET.get('step_number_to', -1)

		curr_step_logs = Step_Logs(thought_record_id=int(thought_record_id), step_number_from=int(step_number_from), step_number_to=int(step_number_to))

		curr_step_logs.save()

		return JsonResponse({'upload': 'successful',}, safe=False)

def save_next_check_error(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', -1)
		step_number_from = request.GET.get('step_number_from', -1)
		error_type = request.GET.get('error_type', None)

		curr_next_check_error = Next_Check_Error(thought_record_id = int(thought_record_id), step_number_from = int(step_number_from), error_type = error_type)

		curr_next_check_error.save()

		return JsonResponse({'upload': 'successful',}, safe=False)

def save_refresh_btn(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', -1)

		curr_refresh_btn = Refresh_Btn(thought_record_id = int(thought_record_id),)

		curr_refresh_btn.save()

		return JsonResponse({'upload': 'successful',}, safe=False)


def save_thought(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		thought = request.GET.get('thought', None)

		curr_thought_record = Thought(thought_record_id = int(thought_record_id), thought = thought)
		curr_thought_record.save()

		thought_id = curr_thought_record.thought_id

		print(thought_record_id, 'thought saved')

		return JsonResponse({'upload': 'successful', 'thought_id': thought_id}, safe=False)

def save_emotion(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		belief = request.GET.get('belief', None)
		emotion = request.GET.get('emotion', None)
		emotion_strength = request.GET.get('emotion_strength', None)

		try:
			thought_id = Thought.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].thought_id
		except:
			thought_id = 0

		curr_thought_record = Emotion(thought_record_id = int(thought_record_id), thought_id = int(thought_id), emotion = emotion, belief = belief, emotion_strength = emotion_strength)
		curr_thought_record.save()

		emotion_id = curr_thought_record.emotion_id

		print(emotion_id, 'emotion saved')

		return JsonResponse({'upload': 'successful', 'emotion_id': emotion_id}, safe=False)


def save_situation(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		situation = request.GET.get('situation', None)
		#thought_id = request.GET.get('thought_id', None)

		try:
			thought_id = Thought.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].thought_id
		except:
			thought_id = 0

		curr_thought_record = Situation(thought_record_id = int(thought_record_id), situation = situation, thought_id = int(thought_id))
		curr_thought_record.save()

		situation_id = curr_thought_record.situation_id

		print(thought_record_id, 'situation saved')

		return JsonResponse({'upload': 'successful', 'situation_id': situation_id,}, safe=False)


def save_thinking_trap_selected(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		thinking_trap_selected = request.GET.get('thinking_trap_selected', None)
		# thinking_trap_generated_id = request.GET.get('thinking_trap_generated_id', None)

		try:
			thinking_trap_generated_id = Thinking_Trap_Generated.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].thinking_trap_generated_id
		except:
			thinking_trap_generated_id = 0

		curr_thought_record = Thinking_Trap_Selected(thought_record_id = int(thought_record_id), thinking_trap_selected = thinking_trap_selected, thinking_trap_generated_id = int(thinking_trap_generated_id))
		curr_thought_record.save()

		thinking_trap_selected_id = curr_thought_record.thinking_trap_selected_id

		print(thought_record_id, 'thinking_trap_selected saved')

		return JsonResponse({'upload': 'successful', 'thinking_trap_selected_id': thinking_trap_selected_id,}, safe=False)


def save_reframe_selected(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		reframe_selected = request.GET.get('reframe_selected', None)

		try:
			reframes_generated_id = Reframes_Generated.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].reframes_generated_id
		except:
			reframes_generated_id = 0

		curr_thought_record = Reframe_Selected(thought_record_id = int(thought_record_id), reframe_selected = reframe_selected, reframes_generated_id = int(reframes_generated_id))
		curr_thought_record.save()
		print(thought_record_id, 'reframe_selected saved')

		return JsonResponse({'upload': 'successful',}, safe=False)


def save_reframe_final(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		reframe_final = request.GET.get('reframe_final', None)
		# reframe_selected_id = request.GET.get('reframe_selected_id', None)

		try:
			reframe_selected_id = Reframe_Selected.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].reframe_selected_id
		except:
			reframe_selected_id = 0

		curr_thought_record = Reframe_Final(thought_record_id = int(thought_record_id), reframe_final = reframe_final, reframe_selected_id = int(reframe_selected_id))
		curr_thought_record.save()

		reframe_final_id = curr_thought_record.reframe_final_id

		print(thought_record_id, 'reframe_final saved')

		return JsonResponse({'upload': 'successful', 'reframe_final_id': reframe_final_id}, safe=False)


def save_outcome_questions(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		# reframe_final_id = request.GET.get('reframe_final_id', None)

		try:
			reframe_final_id = Reframe_Final.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].reframe_final_id
		except:
			reframe_final_id = 0

		believable = request.GET.get('believable', None)
		stickiness = request.GET.get('stickiness', None)
		helpfulness = request.GET.get('helpfulness', None)
		learnability = request.GET.get('learnability', None)
		
		belief_1 = request.GET.get('belief_1', '')
		emotion_strength_1 = request.GET.get('emotion_strength_1', '')

		belief_2 = request.GET.get('belief_2', '')
		emotion_strength_2 = request.GET.get('emotion_strength_2', '')

		comments = request.GET.get('comments', '')

		curr_outcome = Outcome(thought_record_id = int(thought_record_id), \
								reframe_final_id = int(reframe_final_id), \
								believable = believable, \
								stickiness = stickiness, \
								helpfulness = helpfulness, \
								learnability = learnability, \
								belief_1 = belief_1, \
								emotion_strength_1 = emotion_strength_1, \
								belief_2 = belief_2, \
								emotion_strength_2 = emotion_strength_2, \
								comments = comments, \
								)

		curr_outcome.save()

		print(thought_record_id, 'outcome saved')

		# update UserDetails. Get week_no from ThoughtRecord and then update the relevant week_use
		week_no = ThoughtRecord.objects.filter(thought_record_id = int(thought_record_id))[0].week_no

		curr_user_details = UserDetails.objects.filter(username = request.user.username)[0]

		curr_week_use = 0

		if week_no == 1:
			curr_user_details.week_1_use += 1
			curr_week_use = curr_user_details.week_1_use
		elif week_no == 2:
			curr_user_details.week_2_use += 1
			curr_week_use = curr_user_details.week_2_use
		elif week_no == 3:
			curr_user_details.week_3_use += 1
			curr_week_use = curr_user_details.week_3_use
		elif week_no == 4:
			curr_user_details.week_4_use += 1
			curr_week_use = curr_user_details.week_4_use
		
		curr_user_details.save()


		# get week_1_start, week_1_expire, week_2_start, week_2_expire, week_3_start, week_3_expire, week_4_start, week_4_expire
		week_1_start = UserDetails.objects.filter(username = request.user.username)[0].week_1_start
		week_1_expire = UserDetails.objects.filter(username = request.user.username)[0].week_1_expire
		week_2_start = UserDetails.objects.filter(username = request.user.username)[0].week_2_start
		week_2_expire = UserDetails.objects.filter(username = request.user.username)[0].week_2_expire
		week_3_start = UserDetails.objects.filter(username = request.user.username)[0].week_3_start
		week_3_expire = UserDetails.objects.filter(username = request.user.username)[0].week_3_expire
		week_4_start = UserDetails.objects.filter(username = request.user.username)[0].week_4_start
		week_4_expire = UserDetails.objects.filter(username = request.user.username)[0].week_4_expire





		# get week_1_use, week_2_use, week_3_use, week_4_use
		week_1_use = UserDetails.objects.filter(username = request.user.username)[0].week_1_use
		week_2_use = UserDetails.objects.filter(username = request.user.username)[0].week_2_use
		week_3_use = UserDetails.objects.filter(username = request.user.username)[0].week_3_use
		week_4_use = UserDetails.objects.filter(username = request.user.username)[0].week_4_use

		week_1_remaining = 3 - week_1_use
		week_2_remaining = 3 - week_2_use
		week_3_remaining = 3 - week_3_use
		week_4_remaining = 3 - week_4_use

		# get survey_1_status, survey_2_status, survey_3_status, survey_4_status, survey_5_status, survey_8_status

		survey_1_status = UserDetails.objects.filter(username = request.user.username)[0].survey_1_status
		survey_2_status = UserDetails.objects.filter(username = request.user.username)[0].survey_2_status
		survey_3_status = UserDetails.objects.filter(username = request.user.username)[0].survey_3_status
		survey_4_status = UserDetails.objects.filter(username = request.user.username)[0].survey_4_status
		survey_5_status = UserDetails.objects.filter(username = request.user.username)[0].survey_5_status
		survey_8_status = UserDetails.objects.filter(username = request.user.username)[0].survey_8_status


		# check expired weeks

		# pacific timezone

		curr_datetime = datetime.datetime.now()
		curr_datetime = curr_datetime.astimezone(timezone('US/Pacific'))

		if curr_datetime > week_1_expire and week_1_remaining > 0:
			week_1_status = 'expired'
		elif curr_datetime > week_1_start and week_1_remaining <= 0:
			week_1_status = 'completed'
		elif curr_datetime > week_1_start and week_1_remaining > 0:
			week_1_status = 'active'
		else:
			week_1_status = 'TBA'

		if curr_datetime > week_2_expire and week_2_remaining > 0:
			week_2_status = 'expired'
		elif curr_datetime > week_2_start and week_2_remaining <= 0:
			week_2_status = 'completed'
		elif curr_datetime > week_2_start and week_2_remaining > 0:
			week_2_status = 'active'
		else:
			week_2_status = 'TBA'

		if curr_datetime > week_3_expire and week_3_remaining > 0:
			week_3_status = 'expired'
		elif curr_datetime > week_3_start and week_3_remaining <= 0:
			week_3_status = 'completed'
		elif curr_datetime > week_3_start and week_3_remaining > 0:
			week_3_status = 'active'
		else:
			week_3_status = 'TBA'
		
		if curr_datetime > week_4_expire and week_4_remaining > 0:
			week_4_status = 'expired'
		elif curr_datetime > week_4_start and week_4_remaining <= 0:
			week_4_status = 'completed'
		elif curr_datetime > week_4_start and week_4_remaining > 0:
			week_4_status = 'active'
		else:
			week_4_status = 'TBA'


		total_earnings = 0
		total_remaining_earnings = 0
		total_possible_earnings = 0

		if week_1_status == 'TBA' or week_1_status == 'active':
			total_possible_earnings += 5
		elif week_1_status == 'completed':
			total_earnings += 5
			total_possible_earnings += 5

		if week_2_status == 'TBA' or week_2_status == 'active':
			total_possible_earnings += 5
		elif week_2_status == 'completed':
			total_earnings += 5
			total_possible_earnings += 5

		
		if week_3_status == 'TBA' or week_3_status == 'active':
			total_possible_earnings += 5
		elif week_3_status == 'completed':
			total_earnings += 5
			total_possible_earnings += 5

		if week_4_status == 'TBA' or week_4_status == 'active':
			total_possible_earnings += 5
		elif week_4_status == 'completed':
			total_earnings += 5
			total_possible_earnings += 5

		
		if survey_1_status == 1:
			total_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_2_status == 1:
			total_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_3_status == 1:
			total_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_4_status == 1:
			total_earnings += 5
			total_possible_earnings += 5
		else:
			total_possible_earnings += 5
		
		if survey_5_status == 1:
			total_earnings += 10
			total_possible_earnings += 10
		else:
			total_possible_earnings += 10

		if survey_8_status == 1:
			total_earnings += 10
			total_possible_earnings += 10
		else:
			total_possible_earnings += 10
		
		total_remaining_earnings = total_possible_earnings - total_earnings


	
		return JsonResponse({'upload': 'successful', 'curr_week_use': str(curr_week_use), 'total_earnings': str(total_earnings), 'total_remaining_earnings': str(total_remaining_earnings)}, safe=False)


def save_demographics(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		# reframe_final_id = request.GET.get('reframe_final_id', None)
		age_range = request.GET.get('age_range', None)
		gender = request.GET.get('gender', None)
		race = request.GET.get('race', None)
		# income = request.GET.get('income', None)
		education = request.GET.get('education', None)
		population = request.GET.get('population', None)
		problems = request.GET.get('problems', None)
		treatment = request.GET.get('treatment', None)
		prior_experience = request.GET.get('prior_experience', None)

		try:
			reframe_final_id = Reframe_Final.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].reframe_final_id
		except:
			reframe_final_id = 0

		curr_demographics = Demographics(thought_record_id = int(thought_record_id), \
										reframe_final_id = int(reframe_final_id), \
										age_range = age_range, \
										gender = gender, \
										race = race, \
										education = education, \
										population = population, \
										problems = problems, \
										treatment = treatment, \
										prior_experience = prior_experience,)

		curr_demographics.save()

		print(thought_record_id, 'demographics saved')

		return JsonResponse({'upload': 'successful',}, safe=False)


def save_start_over(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		step_number_from = request.GET.get('step_number_from', None)

		skip_step = request.GET.get('skip_step', None)
		remove_negative_feeling = request.GET.get('remove_negative_feeling', None)
		prompt_to_use = request.GET.get('prompt_to_use', None)
		refresh_btn = request.GET.get('refresh_btn', None)
		more_suggestions_btn = request.GET.get('more_suggestions_btn', None)
		descriptive_thought_Q = request.GET.get('descriptive_thought_Q', None)
		A_A = request.GET.get('A_A', None)
		multiple_cognitive_distortions = request.GET.get('multiple_cognitive_distortions', None)
		extra_q = request.GET.get('extra_q', None)

		emotion_questions = request.GET.get('emotion_questions', None)

		personalize = request.GET.get('personalize', None)
		readable = request.GET.get('readable', None)

		psychoeducation = request.GET.get('psychoeducation', None)

		ai = request.GET.get('ai', None)

		include_emotions = request.GET.get('include_emotions', None)

		# compute current week num for the user
		curr_date = datetime.datetime.now().astimezone(timezone('US/Pacific'))

		# get date_started from UserDetails
		date_started = UserDetails.objects.filter(username = request.user.username)[0].week_1_start

		# compute week_no
		week_no = (curr_date - date_started).days // 7 + 1

		curr_thought_record = ThoughtRecord(username = request.user.username, week_no = week_no, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
		curr_thought_record.save()

		new_thought_record_id = curr_thought_record.thought_record_id

		curr_start_over = Start_Over(old_thought_record_id = int(thought_record_id), new_thought_record_id = int(new_thought_record_id), step_number_from = int(step_number_from))

		curr_start_over.save()

		return JsonResponse({'new_thought_record_id': new_thought_record_id,}, safe=False)  


def save_flag_inappropriate(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		reframe = request.GET.get('reframe', None)
		reason = request.GET.get('reason', '')

		curr_flag_inappropriate = Flag_Inappropriate(thought_record_id = int(thought_record_id), reframe = reframe, delete_label=0, reason=reason)
		curr_flag_inappropriate.save()

		# if Flag_Inappropriate.objects.filter(thought_record_id = int(thought_record_id), reframe = reframe).exists():
		# 	curr_flag_inappropriate = Flag_Inappropriate.objects.get(thought_record_id = int(thought_record_id), reframe = reframe)
		# 	curr_flag_inappropriate.delete_label = 0 if curr_flag_inappropriate.delete_label else 1
		# 	curr_flag_inappropriate.save()
		# else:
		# 	curr_flag_inappropriate = Flag_Inappropriate(thought_record_id = int(thought_record_id), reframe = reframe, delete_label=0)
		# 	curr_flag_inappropriate.save()
			
		return JsonResponse({'delete_label': curr_flag_inappropriate.delete_label,}, safe=False) 

def save_load_more(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		num_thinking_trap_shown = request.GET.get('num_thinking_trap_shown', None)

		curr_load_more = Show_More_Thinking_Traps(thought_record_id = int(thought_record_id), num_thinking_trap_shown = int(num_thinking_trap_shown))

		curr_load_more.save()

		return JsonResponse({'upload': 'successful',}, safe=False)


def save_url_clicks(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		url_text = request.GET.get('url_text', None)

		curr_url_click = URL_Clicks(thought_record_id = int(thought_record_id), url_text = url_text)

		curr_url_click.save()

		return JsonResponse({'upload': 'successful',}, safe=False)


def save_feedback(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		feedback = request.GET.get('feedback', None)

		curr_feedback = Feedback(thought_record_id = int(thought_record_id), feedback = feedback)

		curr_feedback.save()

		return JsonResponse({'upload': 'successful',}, safe=False)


def redcap_save(request):
	if request.method == "POST":	
		# project_id, username, instrument, record, redcap_event_name, redcap_data_access_group, redcap_repeat_instance, redcap_repeat_instrument, redcap_url, project_url
		project_id = request.POST.get('project_id', None)
		username = request.POST.get('username', None)
		instrument = request.POST.get('instrument', None)
		record = request.POST.get('record', None)
		redcap_event_name = request.POST.get('redcap_event_name', None)
		redcap_data_access_group = request.POST.get('redcap_data_access_group', None)
		redcap_repeat_instance = request.POST.get('redcap_repeat_instance', None)
		redcap_repeat_instrument = request.POST.get('redcap_repeat_instrument', None)
		redcap_url = request.POST.get('redcap_url', None)
		project_url = request.POST.get('project_url', None)


		print('project_id:', project_id)
		print('username:', username)
		print('instrument:', instrument)
		print('record:', record)
		print('redcap_event_name:', redcap_event_name)
		print('redcap_data_access_group:', redcap_data_access_group)
		print('redcap_repeat_instance:', redcap_repeat_instance)
		print('redcap_repeat_instrument:', redcap_repeat_instrument)
		print('redcap_url:', redcap_url)
		print('project_url:', project_url)

		return JsonResponse({'out': 'success'}, status=200)



def cognitive_distortion_request(request):
	if request.method == "GET":
		
		thought_record_id = request.GET.get('thought_record_id', None)
		# situation_id = request.GET.get('situation_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

		print('situation:', situation)
		print('thought:', thought)
		print('thought_record_id:', thought_record_id)

		curr_original_thought = thought

		if curr_original_thought.endswith('.'):
			curr_original_thought = curr_original_thought[:-1]

		MAX_RETRIES = 3

		current_tries = 1

		curr_original_thought = situation + ' ' + curr_original_thought


		curr_prompt = [{"role": "system", "content": COGNITIVE_DISTORTION_SYSTEM_PROMPT,}, {"role": "user", "content": COGNITIVE_DISTORTION_EXAMPLES + '\n' + curr_original_thought + ' ->',}]


		while current_tries <= MAX_RETRIES:
			try:
				openai.api_base = "https://reframing20k2.openai.azure.com"
				openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
				openai.api_version = "2024-02-15-preview"
				openai.api_type = "azure"

				curr_response_cd = openai.ChatCompletion.create(
									deployment_id='gpt-35-turbo-16k',
									messages=curr_prompt,
									temperature=0,
									max_tokens=64,
									top_p=1,
									stop=['->', '\n'],
									request_timeout=30.0,
								)

				# openai.api_base = "https://api.openai.com/v1"
				# openai.api_key = os.getenv("OPENAI_API_KEY")
				# openai.api_version = ""
				# openai.api_type = "open_ai"

				# curr_response_cd = openai.Completion.create(
				# 					engine="curie:ft-academics-uw-2022-12-07-06-04-56",#"curie:ft-academics-uw-2022-07-21-13-54-54",#"curie:ft-academics-uw-2022-04-26-19-24-38",
				# 					prompt=curr_original_thought.strip() + ' ->',
				# 					temperature=0,
				# 					max_tokens=8,
				# 					top_p=1,
				# 					frequency_penalty=0.8,
				# 					presence_penalty=0.0,
				# 					logprobs=3,
				# 					stop=['->'],
				# 					request_timeout=30.0,
				# 				)
	
				current_tries += 1
				break
			except Exception as e:
				print('cd retrying', str(e))
				time.sleep(5)
				current_tries += 1

		try:
			curr_cd = curr_response_cd['choices'][0]['message']['content'].strip()
			curr_distr = eval(curr_cd)
		except:
			curr_cd = 'Negative Feeling or Emotion'
			curr_cd_category = 'Negative Feeling or Emotion'
			curr_distr = {}

		# curr_distr = {'Catastrophizing': 0.71, 'Fortune Telling': 0.23, 'Overgeneralizing': 0.06}

		# curr_distr = {'Overgeneralizing': 0.62, 'Fortune Telling': 0.16, 'All-or-Nothing Thinking': 0.15}

		pprint.pprint(curr_distr)


		# get probabilities


		

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				openai.api_base = "https://reframing20k2.openai.azure.com"
				openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
				openai.api_version = "2024-02-15-preview"
				openai.api_type = "azure"

				curr_response_cd = openai.Completion.create(
									deployment_id='gpt-35-turbo-instruct',
									prompt = COGNITIVE_DISTORTION_PROBABILITIES + '\n\n' + 'Thought: ' + curr_original_thought + '\nCognitive Distortions: ' + curr_cd + '\nProbabilities:',
									temperature=0,
									max_tokens=64,
									top_p=1,
									stop=['->', '\n'],
									request_timeout=30.0,
								)	
				current_tries += 1
				break
			except Exception as e:
				print('cd retrying', str(e))
				time.sleep(5)
				current_tries += 1

		
		try:
			curr_cd = curr_response_cd['choices'][0]['text'].strip()
			curr_distr = eval(curr_cd)
		except:
			print('curr_cd:', curr_cd)
			curr_cd = 'Negative Feeling or Emotion'
			curr_cd_category = 'Negative Feeling or Emotion'
			curr_distr = {}

		pprint.pprint(curr_distr)


		neg_feeling_flag = 0

		if remove_negative_feeling == 0:
			if 'Negative Feeling or Emotion' not in curr_distr:
				curr_distr['Negative Feeling or Emotion'] = 0.01
				neg_feeling_flag = 1

		curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)

		curr_categories = set()
		curr_categories_li = []
		curr_perc_li = []
		cat_output_li = []

		for idx, elem in enumerate(curr_distr_sorted):
			cat = elem[0]
			prob = round(elem[1]*100.0, 2)

			try:
				subtext = CATEGORIES_SUBTEXT[cat]
			except:
				try:
					subtext = CATEGORIES_SUBTEXT_LOWERCASE_KEYS[cat.lower()]
				except:
					subtext = ''

			if neg_feeling_flag and idx == 0:
				prob = prob - 1.0
				prob = round(prob, 2)

			cat_output_li.append({'category': cat, \
									'subtext': subtext, \
									'prob': int(prob), \
									'color': COLORS[idx % len(COLORS)]})

			curr_categories_li.append(cat)
			curr_perc_li.append(str(prob))
			curr_categories.add(cat)

		curr_categories_str = ';'.join(curr_categories_li)
		curr_perc_str = ';'.join(curr_perc_li)

			
		rem_len = 4 - len(curr_categories)

		shuffle(CATEGORIES_SHUFFLED)

		other_cat_output_li = []
		other_categories_li = []
		for elem in CATEGORIES_SHUFFLED:
			if elem in curr_categories:
				continue
			
			try:
				subtext = CATEGORIES_SUBTEXT[elem]
			except:
				try:
					subtext = CATEGORIES_SUBTEXT_LOWERCASE_KEYS[elem.lower()]
				except:
					subtext = ''

			other_categories_li.append(elem)

			if rem_len <= 0:
				other_cat_output_li.append({'category': elem, \
									'subtext': subtext, \
									'prob': 0.0, \
									'color': COLORS[0]})
				curr_categories.add(elem)
			else:
				cat_output_li.append({'category': elem, \
									'subtext': subtext, \
									'prob': 0.0, \
									'color': COLORS[0]})

				curr_categories.add(elem)
				rem_len = 4 - len(curr_categories)


		other_cat_output_li.append({'category': 'None of These Thinking Traps Seem Right to Me', \
									'subtext': CATEGORIES_SUBTEXT['None of These Thinking Traps Seem Right to Me'], \
									'prob': 0.0, \
									'color': COLORS[0]})
		other_categories_li.append('None of These Thinking Traps Seem Right to Me')

		other_categories_str = ';'.join(other_categories_li)

		try:
			situation_id = Situation.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].situation_id
		except:
			situation_id = 0

		curr_thought_record = Thinking_Trap_Generated(thought_record_id = int(thought_record_id), thinking_trap_generated_cat = curr_categories_str, thinking_trap_generated_perc = curr_perc_str, thinking_trap_generated_other_cat = other_categories_str, situation_id = int(situation_id))
		
		print(thought_record_id, 'thinking trap saved')

		curr_thought_record.save()


		thinking_trap_generated_id = curr_thought_record.thinking_trap_generated_id

		pprint.pprint(cat_output_li)
		return JsonResponse({'pred_CD': cat_output_li, 'other_CD': other_cat_output_li, 'thinking_trap_generated_id': thinking_trap_generated_id}, status=200) 


def cognitive_distortion_request_finetuned(request):
	if request.method == "GET":
		

		thought_record_id = request.GET.get('thought_record_id', None)
		# situation_id = request.GET.get('situation_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

		print('situation:', situation)
		print('thought:', thought)
		print('thought_record_id:', thought_record_id)

		curr_original_thought = thought

		if curr_original_thought.endswith('.'):
			curr_original_thought = curr_original_thought[:-1]

		MAX_RETRIES = 3

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				openai.api_base = "https://reframing20k2.openai.azure.com"
				openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
				openai.api_version = "2024-02-15-preview"
				openai.api_type = "azure"

				curr_response_cd = openai.Completion.create(
									engine="Thinking-Traps",#"curie:ft-academics-uw-2022-12-07-06-04-56",#"curie:ft-academics-uw-2022-07-21-13-54-54",#"curie:ft-academics-uw-2022-04-26-19-24-38",
									prompt=curr_original_thought.strip() + ' ->',
									temperature=0,
									max_tokens=8,
									top_p=1,
									frequency_penalty=0.8,
									presence_penalty=0.0,
									logprobs=3,
									stop=['->'],
									request_timeout=30.0,
								)

				# openai.api_base = "https://api.openai.com/v1"
				# openai.api_key = os.getenv("OPENAI_API_KEY")
				# openai.api_version = ""
				# openai.api_type = "open_ai"

				# curr_response_cd = openai.Completion.create(
				# 					engine="curie:ft-academics-uw-2022-12-07-06-04-56",#"curie:ft-academics-uw-2022-07-21-13-54-54",#"curie:ft-academics-uw-2022-04-26-19-24-38",
				# 					prompt=curr_original_thought.strip() + ' ->',
				# 					temperature=0,
				# 					max_tokens=8,
				# 					top_p=1,
				# 					frequency_penalty=0.8,
				# 					presence_penalty=0.0,
				# 					logprobs=3,
				# 					stop=['->'],
				# 					request_timeout=30.0,
				# 				)
	
				current_tries += 1
				break
			except:
				print('cd retrying')
				time.sleep(5)
				current_tries += 1

		# print(curr_response_cd)
		try:
			curr_cd = curr_response_cd['choices'][0]['text'].replace('\n', ' ').strip()
			curr_cd_category = extract_category(curr_cd)
			curr_distr = extract_category_distribution(curr_response_cd)
		except:
			curr_cd = 'Negative Feeling or Emotion'
			curr_cd_category = 'Negative Feeling or Emotion'
			curr_distr = {}

		# curr_distr = {'Catastrophizing': 0.71, 'Fortune Telling': 0.23, 'Overgeneralizing': 0.06}

		# curr_distr = {'Overgeneralizing': 0.62, 'Fortune Telling': 0.16, 'All-or-Nothing Thinking': 0.15}

		pprint.pprint(curr_distr)

		neg_feeling_flag = 0

		if remove_negative_feeling == 0:
			if 'Negative Feeling or Emotion' not in curr_distr:
				curr_distr['Negative Feeling or Emotion'] = 0.01
				neg_feeling_flag = 1

		curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)

		curr_categories = set()
		curr_categories_li = []
		curr_perc_li = []
		cat_output_li = []

		for idx, elem in enumerate(curr_distr_sorted):
			cat = elem[0]
			prob = round(elem[1]*100.0, 2)
			subtext = CATEGORIES_SUBTEXT[cat]

			if neg_feeling_flag and idx == 0:
				prob = prob - 1.0
				prob = round(prob, 2)

			cat_output_li.append({'category': cat, \
									'subtext': subtext, \
									'prob': int(prob), \
									'color': COLORS[idx % len(COLORS)]})

			curr_categories_li.append(cat)
			curr_perc_li.append(str(prob))
			curr_categories.add(cat)

		curr_categories_str = ';'.join(curr_categories_li)
		curr_perc_str = ';'.join(curr_perc_li)

			
		rem_len = 4 - len(curr_categories)

		shuffle(CATEGORIES_SHUFFLED)

		other_cat_output_li = []
		other_categories_li = []
		for elem in CATEGORIES_SHUFFLED:
			if elem in curr_categories:
				continue
			
			subtext = CATEGORIES_SUBTEXT[elem]

			other_categories_li.append(elem)

			if rem_len <= 0:
				other_cat_output_li.append({'category': elem, \
									'subtext': subtext, \
									'prob': 0.0, \
									'color': COLORS[0]})
				curr_categories.add(elem)
			else:
				cat_output_li.append({'category': elem, \
									'subtext': subtext, \
									'prob': 0.0, \
									'color': COLORS[0]})

				curr_categories.add(elem)
				rem_len = 4 - len(curr_categories)


		other_cat_output_li.append({'category': 'None of These Thinking Traps Seem Right to Me', \
									'subtext': CATEGORIES_SUBTEXT['None of These Thinking Traps Seem Right to Me'], \
									'prob': 0.0, \
									'color': COLORS[0]})
		other_categories_li.append('None of These Thinking Traps Seem Right to Me')

		other_categories_str = ';'.join(other_categories_li)

		try:
			situation_id = Situation.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].situation_id
		except:
			situation_id = 0

		curr_thought_record = Thinking_Trap_Generated(thought_record_id = int(thought_record_id), thinking_trap_generated_cat = curr_categories_str, thinking_trap_generated_perc = curr_perc_str, thinking_trap_generated_other_cat = other_categories_str, situation_id = int(situation_id))
		
		print(thought_record_id, 'thinking trap saved')

		curr_thought_record.save()


		thinking_trap_generated_id = curr_thought_record.thinking_trap_generated_id

		pprint.pprint(cat_output_li)
		return JsonResponse({'pred_CD': cat_output_li, 'other_CD': other_cat_output_li, 'thinking_trap_generated_id': thinking_trap_generated_id}, status=200) 



def make_more_readable(input_text):

	input_text = input_text.strip()

	READABLE_PROMPT = 'Revise the text below to make it easy to understand for a 5th grader. Also, make it more casual: '

	MAX_RETRIES = 3

	current_tries = 1

	while current_tries <= MAX_RETRIES:
		try:
			openai.api_base = "https://reframing20k2.openai.azure.com"
			openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
			openai.api_version = "2024-02-15-preview"
			openai.api_type = "azure"
			deployment = "gpt-35-turbo"
			gpt3_model = deployment

			curr_response_reframing = openai.ChatCompletion.create(
							deployment_id=deployment,
							model="gpt-35-turbo",
							messages= [{"role": "user", "content": READABLE_PROMPT + input_text}],
							max_tokens=128,
							stop=['\n'],
							request_timeout=30.0,
						)
			current_tries += 1
			break
		except Exception as e:
			print('readable error: ', str(e))

			print('readable response retrying')
		
			current_tries += 1

			if current_tries > MAX_RETRIES:
				break
			time.sleep(5)
	try:
		return curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()
	except:
		return input_text


def rational_response_request_attributes(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		attribute_prompts_idx = [0, 1, 2, 3]
		attribute_prompts = [ACTIONABLE_PROMPTS, POSITIVITY_PROMPTS, SPECIFICITY_PROMPTS, NATURALNESS_PROMPTS]
		attribute_prompts_str = ['ACTIONABLE_PROMPTS', 'POSITIVITY_PROMPTS', 'GENERIC_PROMPTS', 'INFORMAL_PROMPTS']
		attribute_prompts_first_header = ['Non-Actionable Response', 'Less Positive Response', 'Specific Response', 'Formal Response']
		attribute_prompts_second_header = ['Actionable Response', 'More Positive Response', 'Generic Response', 'Informal Response']
		
		shuffle(attribute_prompts_idx)

		curr_attribute_prompt = attribute_prompts[attribute_prompts_idx[0]]
		curr_attribute_prompt_str = attribute_prompts_str[attribute_prompts_idx[0]]
		curr_attribute_prompt_first_header = attribute_prompts_first_header[attribute_prompts_idx[0]]
		curr_attribute_prompt_second_header = attribute_prompts_second_header[attribute_prompts_idx[0]]

		print('curr_attribute_prompt_str:', curr_attribute_prompt_str)

		time.sleep(1)


		if cognitive_distortion_category in PROMPTS_2:
			f = 1

			top_ps = [0.2, 0.6]
			gpt3_models = ['text-davinci-003', 'text-davinci-003']

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompts = [HARMFUL_PROMPTS_2, HARMFUL_PROMPTS_1]
				curr_prompt_strs = ['HARMFUL_PROMPTS_2', 'HARMFUL_PROMPTS_1']

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompts = [PROMPTS_2[cognitive_distortion_category], curr_attribute_prompt]
				curr_prompt_strs = ['PROMPTS_2', curr_attribute_prompt_str]

			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					curr_response_reframing = openai.Completion.create(
						engine=gpt3_models[0],
						prompt=curr_reframing_prompts[0] + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_ps[0],
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					break
				except Exception as e:
					print('error2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompts[0] + "\n\n" + prompt_input + '\nRational Response:', response_no="1")
					curr_openAI_error.save()
					print('response 1 retrying')
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)	

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				curr_response_reframing_final_1 = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final_1 = curr_response_reframing_str

				print('response 1:', curr_response_reframing_final_1)
			except:
				curr_response_reframing_final_1 = ''
				curr_prompt_strs[0] = 'default_empty'


			MAX_RETRIES = 3

			current_tries = 1

			if curr_prompt_strs[1].startswith('HARMFUL_PROMPTS'):
				curr_reframing_prompt_2 = curr_reframing_prompts[1] + "\n\n" + prompt_input + '\nRational Response:'
			else:
				curr_reframing_prompt_2 = curr_reframing_prompts[1] + "\n\n" + prompt_input + '\n' + curr_attribute_prompt_first_header + ': ' + curr_response_reframing_final_1 + '\n' + curr_attribute_prompt_second_header + ':'

			while current_tries <= MAX_RETRIES:
				try:
					curr_response_reframing = openai.Completion.create(
						engine=gpt3_models[1],
						prompt=curr_reframing_prompt_2,
						max_tokens=128,
						top_p=top_ps[1],
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					break
				except Exception as e:
					print('error2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompts[1] + "\n\n" + prompt_input + '\nRational Response:', response_no="2")
					curr_openAI_error.save()
					print('response 2 retrying')
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)	

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				curr_response_reframing_final_2 = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final_2 = curr_response_reframing_str

				print('response 2:', curr_response_reframing_final_2)
			except:
				curr_response_reframing_final_2 = ''
				curr_prompt_strs[1] = 'default_empty'

			curr_response_idxs = [0, 1]
			curr_response_reframing_final_li = [curr_response_reframing_final_1, curr_response_reframing_final_2]

			shuffle(curr_response_idxs)

			return JsonResponse({'reframed_thought_1': curr_response_reframing_final_li[curr_response_idxs[0]], 'prompt_type_1': curr_prompt_strs[curr_response_idxs[0]], 'reframed_thought_2': curr_response_reframing_final_li[curr_response_idxs[1]], 'prompt_type_2': curr_prompt_strs[curr_response_idxs[1]]}, status=200)
		else:
			return JsonResponse({'reframed_thought_1': '', 'prompt_type_1': '', 'reframed_thought_2': '', 'prompt_type_2': ''}, status=200)




def rational_response_request_matched(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		curr_safety_filter_thought = safety_filter(thought)

		if curr_safety_filter_thought:
			curr_reframing_prompts = [HARMFUL_PROMPTS_1, HARMFUL_PROMPTS_2]
			curr_prompt_strs = ['HARMFUL_PROMPTS_1', 'HARMFUL_PROMPTS_2']

			curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
			curr_safety_filter_obj.save()
		else:
			try:
				curr_response = requests.post('https://511e-205-175-118-188.ngrok.io/api/prompts', json={'situation': situation, 'thought': thought}, timeout=3)

				curr_reframing_prompts = [curr_response.json()['prompt_1'], curr_response.json()['prompt_2']]
				curr_prompt_strs = [curr_response.json()['thought_record_ids'], curr_response.json()['thought_record_ids']]

			except ConnectTimeout:
				print('Request has timed out')

				curr_reframing_prompts = [PROMPTS_2[cognitive_distortion_category], PROMPTS_1[cognitive_distortion_category],]
				curr_prompt_strs = ['PROMPTS_2', 'PROMPTS_2']
				
		top_ps = [0.4, 0.6]
		gpt3_models = ['text-davinci-003', 'text-davinci-003']


		MAX_RETRIES = 3

		current_tries = 1


		while current_tries <= MAX_RETRIES:
			try:
				curr_response_reframing = openai.Completion.create(
					engine=gpt3_models[0],
					prompt=curr_reframing_prompts[0] + "\n\n" + prompt_input + '\nRational Response:',
					max_tokens=128,
					top_p=top_ps[0],
					frequency_penalty=0.0,
					presence_penalty=0.0,
					logprobs=5,
					stop=['\n'],
					request_timeout=30.0,
				)
				break
			except Exception as e:
				print('error1:', str(e))
				curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompts[0] + "\n\n" + prompt_input + '\nRational Response:', response_no="1")
				curr_openAI_error.save()
				print('response 1  retrying')
				current_tries += 1

				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)

		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

			curr_response_reframing_final_1 = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
				curr_safety_filter_obj.save()

			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final_1 = curr_response_reframing_str

			print('response 1:', curr_response_reframing_final_1)
	
			# return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_strs[0]}, status=200)

		except:
			curr_response_reframing_final_1 = ''
			curr_prompt_strs[0] = 'default_empty'
			# return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)


		MAX_RETRIES = 3

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				curr_response_reframing = openai.Completion.create(
					engine=gpt3_models[1],
					prompt=curr_reframing_prompts[1] + "\n\n" + prompt_input + '\nRational Response:',
					max_tokens=128,
					top_p=top_ps[1],
					frequency_penalty=0.0,
					presence_penalty=0.0,
					logprobs=5,
					stop=['\n'],
					request_timeout=30.0,
				)
				break
			except Exception as e:
				print('error2: ', str(e))
				curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompts[1] + "\n\n" + prompt_input + '\nRational Response:', response_no="2")
				curr_openAI_error.save()
				print('response 2 retrying')
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)	

		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

			curr_response_reframing_final_2 = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
				curr_safety_filter_obj.save()

			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final_2 = curr_response_reframing_str

			print('response 2:', curr_response_reframing_final_2)
		except:
			curr_response_reframing_final_2 = ''
			curr_prompt_strs[1] = 'default_empty'


		return JsonResponse({'reframed_thought_1': curr_response_reframing_final_1, 'prompt_type_1': curr_prompt_strs[0], 'reframed_thought_2': curr_response_reframing_final_2, 'prompt_type_2': curr_prompt_strs[1]}, status=200)


def rational_response_request_single(request):
	if request.method == "GET":
		
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		if cognitive_distortion_category in PROMPTS_2:
			f = 1

			top_p = 0.2
			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompt = HARMFUL_PROMPTS_2
				curr_prompt_str = 'HARMFUL_PROMPTS_2'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompt = PROMPTS_2[cognitive_distortion_category]
				curr_prompt_str = 'PROMPTS_2'

			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					openai.api_base = "https://reframing20k2.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2024-02-15-preview"
					openai.api_type = "azure"
					deployment = "davinci-002"
					gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					break
				except Exception as e:
					print('error2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="2")
					curr_openAI_error.save()
					print('response 2 retrying')
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)	

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response 2:', curr_response_reframing_final)

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)



def get_cognitive_distortion_category(thought):
	curr_original_thought = thought

	if curr_original_thought.endswith('.'):
		curr_original_thought = curr_original_thought[:-1]

	MAX_RETRIES = 3

	current_tries = 1

	while current_tries <= MAX_RETRIES:
		try:
			openai.api_base = "https://reframing20k2.openai.azure.com"
			openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
			openai.api_version = "2024-02-15-preview"
			openai.api_type = "azure"

			curr_response_cd = openai.Completion.create(
								engine="Thinking-Traps", #"curie:ft-academics-uw-2022-12-07-06-04-56",#"curie:ft-academics-uw-2022-07-21-13-54-54",#"curie:ft-academics-uw-2022-04-26-19-24-38",
								prompt=curr_original_thought.strip() + ' ->',
								temperature=0,
								max_tokens=8,
								top_p=1,
								frequency_penalty=0.8,
								presence_penalty=0.0,
								logprobs=3,
								stop=['->'],
								request_timeout=30.0,
							)

			# openai.api_base = "https://api.openai.com/v1"
			# openai.api_key = os.getenv("OPENAI_API_KEY")
			# openai.api_version = ""
			# openai.api_type = "open_ai"

			# curr_response_cd = openai.Completion.create(
			# 			engine= "curie:ft-academics-uw-2022-12-07-06-04-56",#"curie:ft-academics-uw-2022-07-21-13-54-54",#"curie:ft-academics-uw-2022-04-26-19-24-38",
			# 			prompt=curr_original_thought.strip() + ' ->',
			# 			temperature=0,
			# 			max_tokens=8,
			# 			top_p=1,
			# 			frequency_penalty=0.8,
			# 			presence_penalty=0.0,
			# 			logprobs=3,
			# 			stop=['->'],
			# 			request_timeout=30.0,
			# 		)

			current_tries += 1
			break
		except:
			print('cd retrying')
			time.sleep(1)
			current_tries += 1

	# print(curr_response_cd)
	curr_cd = curr_response_cd['choices'][0]['text'].replace('\n', ' ').strip()
	curr_cd_category = extract_category(curr_cd)
	curr_distr = extract_category_distribution(curr_response_cd)

	pprint.pprint(curr_distr)

	curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)

	curr_categories = set()
	curr_categories_li = []
	curr_perc_li = []
	cat_output_li = []

	for idx, elem in enumerate(curr_distr_sorted):
		cat = elem[0]
		prob = round(elem[1]*100.0, 2)
		subtext = CATEGORIES_SUBTEXT[cat]

		if idx == 0:
			prob = prob - 1.0
			prob = round(prob, 2)

		cat_output_li.append({'category': cat, \
								'subtext': subtext, \
								'prob': int(prob), \
								'color': COLORS[idx % len(COLORS)]})

		curr_categories_li.append(cat)
		curr_perc_li.append(str(prob))
		curr_categories.add(cat)
	
	return curr_categories_li[0]


def rational_response_request_1(request):
	if request.method == "GET":

		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()
		
		# if cognitive_distortion_category == 'None of These Thinking Traps Seem Right to Me':
		# 	cognitive_distortion_category = get_cognitive_distortion_category(thought)
		# 	print('returned cd:', cognitive_distortion_category)

		if cognitive_distortion_category in PROMPTS_1:
			f = 1

			if random_top_p == 0:
				top_p = 0.6
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)
			
			
			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompt = HARMFUL_PROMPTS_1
				curr_prompt_str = 'HARMFUL_PROMPTS_1'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompt = PROMPTS_1[cognitive_distortion_category]
				curr_prompt_str = 'PROMPTS_1'

			MAX_RETRIES = 3

			current_tries = 1

			print('querying response 1...')


			while current_tries <= MAX_RETRIES:
				try:
					if current_tries <= 1:
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "davinci-002"
						gpt3_model = deployment
					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "text-davinci-003"
						gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error1:', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="1")
					curr_openAI_error.save()
					print('response 1  retrying')
					current_tries += 1

					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)
					

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response 1:', curr_response_reframing_final)
		
				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)


def rational_response_request_2(request):
	if request.method == "GET":

		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		time.sleep(1)	

		if cognitive_distortion_category in PROMPTS_2:
			f = 1
			
			if random_top_p == 0:
				top_p = 0.2
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)


			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompt = HARMFUL_PROMPTS_2
				curr_prompt_str = 'HARMFUL_PROMPTS_2'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompt = PROMPTS_2[cognitive_distortion_category]
				curr_prompt_str = 'PROMPTS_2'

			MAX_RETRIES = 3

			current_tries = 1

			print('querying response 2...')

			while current_tries <= MAX_RETRIES:
				try:

					if current_tries <= 1:
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "davinci-002"
						gpt3_model = deployment
					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "text-davinci-003"
						gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="2")
					curr_openAI_error.save()
					print('response 2 retrying')
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)	

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response 2:', curr_response_reframing_final)

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)


def rational_response_request_3(request):

	if request.method == "GET":
		
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()
		
		time.sleep(2)

		if cognitive_distortion_category in PROMPTS_3:
			f = 1

			if random_top_p == 0:
				top_p = 0.4
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)
			

			#'text-davinci-002'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompt = HARMFUL_PROMPTS_3
				curr_prompt_str = 'HARMFUL_PROMPTS_3'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompt = PROMPTS_3[cognitive_distortion_category]
				curr_prompt_str = 'PROMPTS_3'

			MAX_RETRIES = 3

			current_tries = 1

			print('querying response 3...')

			while current_tries <= MAX_RETRIES:
				try:
					if current_tries <= 1:
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "davinci-002"
						gpt3_model = deployment
					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "text-davinci-003"
						gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error3: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response 3 retrying')
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response 3:', curr_response_reframing_final)
		
				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)

def rational_response_request_theme_1(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)


		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		# Get Theme
		MAX_RETRIES = 3

		current_tries = 1

		theme_pred_prompt = thought.strip() + ' ' + situation.strip()

		if theme_pred_prompt == "":
			theme_pred_prompt = thought.strip()

		while current_tries <= MAX_RETRIES:
			try:
				openai.api_base = "https://reframing20k2.openai.azure.com"
				openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
				openai.api_version = "2024-02-15-preview"
				openai.api_type = "azure"

				curr_response_theme = openai.Completion.create(
									engine="Theme_Curie",#"curie:ft-academics-uw-2023-02-14-06-48-46", #"curie:ft-academics-uw-2022-04-26-19-24-38",
									prompt=theme_pred_prompt.strip() + ' ->',
									temperature=0,
									max_tokens=8,
									top_p=1,
									frequency_penalty=0.69,
									presence_penalty=0.0,
									logprobs=5,
									stop=['->'],
									request_timeout=10.0,
								)

				# openai.api_base = "https://api.openai.com/v1"
				# openai.api_key = os.getenv("OPENAI_API_KEY")
				# openai.api_version = ""
				# openai.api_type = "open_ai"

				# curr_response_theme = openai.Completion.create(
				# 					engine="curie:ft-academics-uw-2023-02-14-06-48-46", #"curie:ft-academics-uw-2022-04-26-19-24-38",
				# 					prompt=theme_pred_prompt.strip() + ' ->',
				# 					temperature=0,
				# 					max_tokens=8,
				# 					top_p=1,
				# 					frequency_penalty=0.69,
				# 					presence_penalty=0.0,
				# 					logprobs=5,
				# 					stop=['->'],
				# 					request_timeout=10.0,
				# 				)

				current_tries += 1
				break
			except Exception as e:
				print('error-theme-2-pred: ', str(e))
				print('theme retrying')
				time.sleep(1)
				current_tries += 1

		# print(curr_response_cd)
		try:
			curr_theme = curr_response_theme['choices'][0]['text'].replace('\n', ' ').strip()
			curr_theme_category = extract_category_theme(curr_theme)
			curr_distr = extract_category_distribution_theme(curr_response_theme)
			curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)
			curr_theme = curr_distr_sorted[0][0]
		except:
			curr_theme = 'Tasks & achievement'
			curr_theme_category = 'Tasks & achievement'
			curr_distr = {}

		pprint.pprint(curr_distr)

		if curr_theme in PROMPTS_THEME:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME[curr_theme]:
				curr_li = PROMPTS_THEME[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt
			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.6
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)

			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
				curr_prompt_str = 'THEME_PROMPT_1'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
				curr_prompt_str = 'THEME_PROMPT_1'

			# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "davinci-002"
						gpt3_model = deployment
					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "text-davinci-003"
						gpt3_model = deployment
					
					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error-theme: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				print('response theme 1:', curr_response_reframing_str, curr_prompt_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str



				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)



def rational_response_request_theme_2(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		time.sleep(1)

		# Get Theme
		MAX_RETRIES = 3

		current_tries = 1

		theme_pred_prompt = thought.strip() + ' ' + situation.strip()

		if theme_pred_prompt == "":
			theme_pred_prompt = thought.strip()

		# openai.organization = "org-o2Ssn2MTYvpMDkvzRSiehlv4"

		while current_tries <= MAX_RETRIES:
			try:
				openai.api_base = "https://reframing20k2.openai.azure.com"
				openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
				openai.api_version = "2024-02-15-preview"
				openai.api_type = "azure"
			
				curr_response_theme = openai.Completion.create(
									engine="Theme_Curie", #"curie:ft-academics-uw-2023-02-14-06-48-46", #"curie:ft-academics-uw-2022-04-26-19-24-38",
									prompt=situation + ' ->',
									temperature=0,
									max_tokens=8,
									top_p=1,
									frequency_penalty=0.69,
									presence_penalty=0.0,
									logprobs=5,
									stop=['->'],
									request_timeout=30.0,
								)

				# openai.api_base = "https://api.openai.com/v1"
				# openai.api_key = os.getenv("OPENAI_API_KEY")
				# openai.api_version = ""
				# openai.api_type = "open_ai"

				# curr_response_theme = openai.Completion.create(
				# 					engine="curie:ft-academics-uw-2023-02-14-06-48-46", #"curie:ft-academics-uw-2022-04-26-19-24-38",
				# 					prompt=situation + ' ->',
				# 					temperature=0,
				# 					max_tokens=8,
				# 					top_p=1,
				# 					frequency_penalty=0.69,
				# 					presence_penalty=0.0,
				# 					logprobs=5,
				# 					stop=['->'],
				# 					request_timeout=30.0,
				# 				)

				current_tries += 1
				break
			except Exception as e:
				print('error-theme-2-pred: ', str(e))
				print('theme retrying')
				time.sleep(5)
				current_tries += 1

		# print(curr_response_cd)
		try:
			curr_theme = curr_response_theme['choices'][0]['text'].replace('\n', ' ').strip()
			curr_theme_category = extract_category_theme(curr_theme)
			curr_distr = extract_category_distribution_theme(curr_response_theme)
			curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)
			curr_theme = curr_distr_sorted[0][0]
		except:
			curr_theme = 'Tasks & achievement'
			curr_theme_category = 'Tasks & achievement'
			curr_distr = {}

		pprint.pprint(curr_distr)


		openai.api_base = "https://reframing20k2.openai.azure.com"
		openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
		openai.api_version = "2024-02-15-preview"
		openai.api_type = "azure"
		deployment = "davinci-002"

		if curr_theme in PROMPTS_THEME:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME[curr_theme]:
				curr_li = PROMPTS_THEME[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt

			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.4
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)


			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
				curr_prompt_str = 'THEME_PROMPT_2'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
				curr_prompt_str = 'THEME_PROMPT_2'

			# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "davinci-002"
						gpt3_model = deployment
					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "text-davinci-003"
						gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error-theme-2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response theme 2:', curr_response_reframing_final)

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)


def get_theme(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)

		curr_prompt = [{'role': 'system', 'content': TOPIC_PROMPT}, {'role': 'user', 'content': situation.strip() + ' ' + thought.strip()}]

		MAX_RETRIES = 3

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				openai.api_base = "https://reframing20k2.openai.azure.com"
				openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
				openai.api_version = "2024-02-15-preview"
				openai.api_type = "azure"
				deployment = "gpt-35-turbo"
				gpt3_model = deployment

				curr_response_reframing = openai.ChatCompletion.create(
					deployment_id=deployment,
					model='gpt-35-turbo',
					messages=curr_prompt,
					max_tokens=32,
					top_p=1,
					temperature=0,
					request_timeout=30.0,
				)
				
				current_tries += 1
				break
			except Exception as e:
				print('error-get-theme: ', str(e))
				if 'filtered' in str(e):
					curr_response_reframing = {'choices': [{'message': {'content': 'Hopelessness/Depression'}}]}				
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)

		try:
			final_theme = 'tasks & achievement'
			curr_theme = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip().lower()

			for theme in THEMES_CATEGORIES_NEW:
				if theme in curr_theme:
					final_theme = theme
					break	
		except:
			final_theme = 'tasks & achievement'
		
		print('final_theme:', final_theme)
		return JsonResponse({'theme': final_theme}, status=200)



def rational_response_request_theme_new_1(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		include_emotions = np.random.choice([0, 1], p=[0.5, 0.5])

		emotion = request.GET.get('emotion', None)

		curr_theme = request.GET.get('theme', None)


		if include_emotions == 1:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip() + '\nEmotion: ' + emotion.strip()
		else:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		if curr_theme in PROMPTS_THEME_V3:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME_V3[curr_theme]:
				curr_li = PROMPTS_THEME_V3[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME_V3[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt
			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.6
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)

			#'text-davinci-003'

			# sample 0 or 1 with a probability of 0.33

			

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				if include_emotions == 1:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Incorporate the emotion in your output whenever available. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_1_EMOTION'
				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_1'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				if include_emotions == 1:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Incorporate the emotion in your output whenever available. Avoid overly long reframes:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_1_EMOTION'
				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_1'

			# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					openai.api_base = "https://reframing20k2.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2024-02-15-preview"
					openai.api_type = "azure"
					deployment = "davinci-002"
					gpt3_model = deployment

					# if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
					# 	openai.api_base = "https://reframing20k2.openai.azure.com"
					# 	openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					# 	openai.api_version = "2024-02-15-preview"
					# 	openai.api_type = "azure"
					# 	deployment = "davinci-002"
					# 	gpt3_model = deployment
					# else:
					# 	openai.api_base = "https://api.openai.com/v1"
					# 	openai.api_key = os.getenv("OPENAI_API_KEY")
					# 	openai.api_version = ""
					# 	openai.api_type = "open_ai"
					# 	deployment = "text-davinci-003"
					# 	gpt3_model = deployment
					
					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error-theme-new: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				print('response theme 1:', curr_response_reframing_str, curr_prompt_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)



def rational_response_request_theme_new_2(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		include_emotions = np.random.choice([0, 1], p=[0.5, 0.5])

		emotion = request.GET.get('emotion', None)

		curr_theme = request.GET.get('theme', None)

		if include_emotions == 1:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip() + '\nEmotion: ' + emotion.strip()
		else:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		time.sleep(1)

		openai.api_base = "https://reframing20k2.openai.azure.com"
		openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
		openai.api_version = "2024-02-15-preview"
		openai.api_type = "azure"
		deployment = "davinci-002"

		if curr_theme in PROMPTS_THEME_V3:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME_V3[curr_theme]:
				curr_li = PROMPTS_THEME_V3[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME_V3[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt

			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.4
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)


			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				if include_emotions == 1:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Incorporate the emotion in your output whenever available. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_2_EMOTION'
				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_2'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				if include_emotions == 1:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Incorporate the emotion in your output whenever available. Avoid overly long reframes:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_2_EMOTION'
				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_2'

			# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					openai.api_base = "https://reframing20k2.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2024-02-15-preview"
					openai.api_type = "azure"
					deployment = "davinci-002"
					gpt3_model = deployment

					# if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
					# 	openai.api_base = "https://reframing20k2.openai.azure.com"
					# 	openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					# 	openai.api_version = "2024-02-15-preview"
					# 	openai.api_type = "azure"
					# 	deployment = "davinci-002"
					# 	gpt3_model = deployment
					# else:
					# 	openai.api_base = "https://api.openai.com/v1"
					# 	openai.api_key = os.getenv("OPENAI_API_KEY")
					# 	openai.api_version = ""
					# 	openai.api_type = "open_ai"
					# 	deployment = "text-davinci-003"
					# 	gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error-theme-new-2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response theme 2:', curr_response_reframing_final)

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)




def rational_response_request_theme_new_3(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		include_emotions = np.random.choice([0, 1], p=[0.5, 0.5])

		emotion = request.GET.get('emotion', None)

		curr_theme = request.GET.get('theme', None)

		if include_emotions == 1:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip() + '\nEmotion: ' + emotion.strip()
		else:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		time.sleep(1)

		openai.api_base = "https://reframing20k2.openai.azure.com"
		openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
		openai.api_version = "2024-02-15-preview"
		openai.api_type = "azure"
		deployment = "davinci-002"

		if curr_theme in PROMPTS_THEME_V3:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME_V3[curr_theme]:
				curr_li = PROMPTS_THEME_V3[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME_V3[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt

			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.1
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)


			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				if include_emotions == 1:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Incorporate the emotion in your output whenever available. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_3_EMOTION'
				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_3'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				if include_emotions == 1:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Incorporate the emotion in your output whenever available. Avoid overly long reframes:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_3_EMOTION'
				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_3'

			# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					openai.api_base = "https://reframing20k2.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2024-02-15-preview"
					openai.api_type = "azure"
					deployment = "davinci-002"
					gpt3_model = deployment

					# if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
					# 	openai.api_base = "https://reframing20k2.openai.azure.com"
					# 	openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					# 	openai.api_version = "2024-02-15-preview"
					# 	openai.api_type = "azure"
					# 	deployment = "davinci-002"
					# 	gpt3_model = deployment
					# else:
					# 	openai.api_base = "https://api.openai.com/v1"
					# 	openai.api_key = os.getenv("OPENAI_API_KEY")
					# 	openai.api_version = ""
					# 	openai.api_type = "open_ai"
					# 	deployment = "text-davinci-003"
					# 	gpt3_model = deployment

					curr_response_reframing = openai.Completion.create(
						engine=gpt3_model,
						prompt=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:',
						max_tokens=128,
						top_p=top_p,
						frequency_penalty=0.0,
						presence_penalty=0.0,
						logprobs=5,
						stop=['\n'],
						request_timeout=30.0,
					)
					current_tries += 1
					break
				except Exception as e:
					print('error-theme-new-3: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				print('response theme 3:', curr_response_reframing_final)

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)





def rational_response_request_theme_gpt4_1(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		include_emotions = 1 # np.random.choice([0, 1], p=[0.5, 0.5])

		emotion = request.GET.get('emotion', None)

		curr_theme = request.GET.get('theme', None)

		if include_emotions == 1:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip() + '\nEmotion: ' + emotion.strip()
		else:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		if curr_theme in PROMPTS_THEME_V3:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME_V3[curr_theme]:
				curr_li = PROMPTS_THEME_V3[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME_V3[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt
			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.6
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)

			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)


			if curr_safety_filter_thought:
				if include_emotions == 1:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Incorporate the emotion in your output whenever available. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut"'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_1_EMOTION'
				else:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut"'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_1'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				if include_emotions == 1:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Incorporate the emotion in your output whenever available. Avoid overly long reframes.'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_1_EMOTION'
				else:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Avoid overly long reframes.'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_1'

			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:					
					if current_tries <= 1:
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "gpt-4"
						gpt3_model = deployment

						curr_response_reframing = openai.ChatCompletion.create(
							deployment_id=deployment,
							model='gpt-4',
							messages = curr_reframing_prompt + [{'role': 'user', 'content': prompt_input + '\nRational Response:'},],
							max_tokens=128,
							top_p=top_p,
							stop=['\n'],
							request_timeout=30.0,
						)

					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "gpt-4"
						gpt3_model = deployment

						curr_response_reframing = openai.ChatCompletion.create(
							model=gpt3_model,
							messages = curr_reframing_prompt + [{'role': 'user', 'content': prompt_input + '\nRational Response:'},],
							max_tokens=128,
							top_p=top_p,
							stop=['\n'],
							request_timeout=30.0,
						)
					
					
					current_tries += 1
					break
				except Exception as e:
					print('error-gpt4-1: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				print('response gpt4 1:', curr_response_reframing_str, curr_prompt_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)
		else:
			return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)


def rational_response_request_theme_gpt4_2(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		include_emotions = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

		emotion = request.GET.get('emotion', None)

		curr_theme = request.GET.get('theme', None)

		if include_emotions == 1:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip() + '\nEmotion: ' + emotion.strip()
		else:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		if curr_theme in PROMPTS_THEME_V3:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME_V3[curr_theme]:
				curr_li = PROMPTS_THEME_V3[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME_V3[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt
			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.4
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)

			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				if include_emotions == 1:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Incorporate the emotion in your output whenever available. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut"'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_2_EMOTION'
				else:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut"'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_2'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				if include_emotions == 1:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Incorporate the emotion in your output whenever available. Avoid overly long reframes.'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_2_EMOTION'
				else:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Avoid overly long reframes.'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_2'

			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					

					if current_tries <= 1:
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "gpt-4"
						gpt3_model = deployment

						curr_response_reframing = openai.ChatCompletion.create(
							deployment_id=deployment,
							model='gpt-4',
							messages = curr_reframing_prompt + [{'role': 'user', 'content': prompt_input + '\nRational Response:'},],
							max_tokens=128,
							top_p=top_p,
							stop=['\n'],
							request_timeout=30.0,
						)

					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "gpt-4"
						gpt3_model = deployment

						curr_response_reframing = openai.ChatCompletion.create(
							model=gpt3_model,
							messages = curr_reframing_prompt + [{'role': 'user', 'content': prompt_input + '\nRational Response:'},],
							max_tokens=128,
							top_p=top_p,
							stop=['\n'],
							request_timeout=30.0,
						)
					
					
					current_tries += 1
					break
				except Exception as e:
					print('error-gpt4-2: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				print('response gpt4 2:', curr_response_reframing_str, curr_prompt_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)

		else:
			return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)





def rational_response_request_theme_gpt4_3(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', None)
		thought = request.GET.get('thought', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		random_top_p = int(request.GET.get('random_top_p', 0))

		readable = request.GET.get('readable', 0)
		readable = int(readable)

		include_emotions = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

		emotion = request.GET.get('emotion', None)

		curr_theme = request.GET.get('theme', None)

		if include_emotions == 1:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip() + '\nEmotion: ' + emotion.strip()
		else:
			prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

		if curr_theme in PROMPTS_THEME_V3:
			curr_prompt_example_li = []
			if cognitive_distortion_category in PROMPTS_THEME_V3[curr_theme]:
				curr_li = PROMPTS_THEME_V3[curr_theme][cognitive_distortion_category]
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

				curr_prompt_example_li += curr_li_sample
			
			if len(curr_prompt_example_li) < 5:
				curr_li = list(set(PROMPTS_THEME_V3[curr_theme]['all']))
				curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
				
				# Sample max 5 examples from the list
				curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

				curr_prompt_example_li += curr_li_sample
			
			# Reverse the list
			curr_prompt_example_li = curr_prompt_example_li[::-1]

			# print('curr_prompt_example_li:', curr_prompt_example_li)

			# Create Prompt
			# Get Reframing

			f = 1

			if random_top_p == 0:
				top_p = 0.1
			else:
				top_p = round(random.uniform(0.0, 0.99), 2)

			#'text-davinci-003'

			curr_safety_filter_thought = safety_filter(thought)

			if curr_safety_filter_thought:
				if include_emotions == 1:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Incorporate the emotion in your output whenever available. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut"'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_3_EMOTION'
				else:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut"'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_3'

				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
				curr_safety_filter_obj.save()

			else:
				if include_emotions == 1:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Incorporate the emotion in your output whenever available. Avoid overly long reframes.'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_3_EMOTION'
				else:
					curr_reframing_prompt = [{'role': 'system', 'content': 'Write a rational response to the following distorted thoughts. Always respond in first person. Avoid overly long reframes.'}, {'role': 'user', 'content': '\n\n'.join(curr_prompt_example_li)}]
					curr_prompt_str = 'GPT4_PROMPT_3'


			MAX_RETRIES = 3

			current_tries = 1

			while current_tries <= MAX_RETRIES:
				try:
					if current_tries <= 1:
						openai.api_base = "https://reframing20k2.openai.azure.com"
						openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
						openai.api_version = "2024-02-15-preview"
						openai.api_type = "azure"
						deployment = "gpt-4"
						gpt3_model = deployment

						curr_response_reframing = openai.ChatCompletion.create(
							deployment_id=deployment,
							model='gpt-4',
							messages = curr_reframing_prompt + [{'role': 'user', 'content': prompt_input + '\nRational Response:'},],
							max_tokens=128,
							top_p=top_p,
							stop=['\n'],
							request_timeout=30.0,
						)

					else:
						openai.api_base = "https://api.openai.com/v1"
						openai.api_key = os.getenv("OPENAI_API_KEY")
						openai.api_version = ""
						openai.api_type = "open_ai"
						deployment = "gpt-4"
						gpt3_model = deployment

						curr_response_reframing = openai.ChatCompletion.create(
							model=gpt3_model,
							messages = curr_reframing_prompt + [{'role': 'user', 'content': prompt_input + '\nRational Response:'},],
							max_tokens=128,
							top_p=top_p,
							stop=['\n'],
							request_timeout=30.0,
						)
					
					
					current_tries += 1
					break
				except Exception as e:
					print('error-gpt4-3: ', str(e))
					curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=prompt_input + '\nRational Response:', response_no="3")
					curr_openAI_error.save()
					print('response theme retrying')
					if 'filtered' in str(e):
						break
					current_tries += 1
					if current_tries > MAX_RETRIES:
						break
					time.sleep(5)

			try:
				curr_response_reframing_str = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()

				if readable == 1:
					curr_response_reframing_str = make_more_readable(curr_response_reframing_str)

				print('response gpt4 2:', curr_response_reframing_str, curr_prompt_str)

				curr_response_reframing_final = ''

				curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

				if curr_safety_filter_reframing:
					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
					curr_safety_filter_obj.save()

				else:
					if curr_response_reframing_str != "":
						curr_response_reframing_final = curr_response_reframing_str

				return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': curr_prompt_str, 'theme': curr_theme}, status=200)
			except:
				return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)
		else:
			return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty', 'theme': curr_theme}, status=200)




def get_more_help_1(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', '')
		thought = request.GET.get('thought', '')
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', '')

		original_reframe = request.GET.get('original_reframe', '')

		prompt_type = request.GET.get('prompt_type', '')
		more_context = request.GET.get('more_context', '')

		curr_theme = request.GET.get('theme', '')

		print('curr_theme:', curr_theme)

		if prompt_type == 'actionable':
			curr_reframing_prompt = MORE_ACTIONABLE_PROMPTS
			prompt_input = curr_reframing_prompt + "\n\n" + 'Situation: ' + situation.strip() + '\nThought: ' + thought.strip() + '\nOriginal Reframe: ' + original_reframe.strip() + '\nActionable Reframe:'
		elif prompt_type == 'empathic':
			curr_reframing_prompt = MORE_EMPATHIC_PROMPTS
			prompt_input = curr_reframing_prompt + "\n\n" + 'Situation: ' + situation.strip() + '\nThought: ' + thought.strip() + '\nOriginal Reframe: ' + original_reframe.strip() + '\nEmpathetic Reframe:'
		elif prompt_type == 'personalized':
			if curr_theme in PROMPTS_THEME_NEW:
				curr_prompt_example_li = []
				if cognitive_distortion_category in PROMPTS_THEME_NEW[curr_theme]:
					curr_li = PROMPTS_THEME_NEW[curr_theme][cognitive_distortion_category]
					# Sample max 5 examples from the list
					curr_li_sample = random.sample(curr_li, min(len(curr_li), 5))

					curr_prompt_example_li += curr_li_sample
				
				if len(curr_prompt_example_li) < 5:
					curr_li = list(set(PROMPTS_THEME_NEW[curr_theme]['all']))
					curr_li = [x for x in curr_li if x not in curr_prompt_example_li]
					
					# Sample max 5 examples from the list
					curr_li_sample = random.sample(curr_li, min(len(curr_li), 5 - len(curr_prompt_example_li)))

					curr_prompt_example_li += curr_li_sample
				
				# Reverse the list
				curr_prompt_example_li = curr_prompt_example_li[::-1]

				# print('curr_prompt_example_li:', curr_prompt_example_li)

				# Create Prompt
				# Get Reframing

				f = 1
				#'text-davinci-003'

				curr_safety_filter_thought = safety_filter(thought)

				if curr_safety_filter_thought:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts. Do not use words related to suicidal ideation or self-harm such as "die", "suicide", or "cut":\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_1'

					curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = thought, type = 'thought')
					curr_safety_filter_obj.save()

				else:
					curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
					curr_prompt_str = 'THEME_PROMPT_1'
				
				prompt_input = curr_reframing_prompt + "\n\n" + 'Situation: ' + situation.strip() + ' ' + more_context.strip() + '\nThought: ' + thought.strip() + '\nRational Response:'
			else:
				curr_reframing_prompt = MORE_PERSONALIZED_PROMPTS
				prompt_input = 'Situation: ' + situation.strip() + '\nThought: ' + thought.strip() + '\nReframe: ' + original_reframe.strip() + '\n\n' + curr_reframing_prompt + '\n\n' + 'Context: ' + more_context + '\nPersonalized Reframe:'
				

		MAX_RETRIES = 3

		top_p = 0.4

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				if current_tries <= 1:
					openai.api_base = "https://reframing20k2.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2024-02-15-preview"
					openai.api_type = "azure"
					deployment = "davinci-002"
					gpt3_model = deployment
				else:
					openai.api_base = "https://api.openai.com/v1"
					openai.api_key = os.getenv("OPENAI_API_KEY")
					openai.api_version = ""
					openai.api_type = "open_ai"
					deployment = "text-davinci-003"
					gpt3_model = deployment

				curr_response_reframing = openai.Completion.create(
					engine=gpt3_model,
					prompt=prompt_input,
					max_tokens=128,
					top_p=top_p,
					frequency_penalty=0.0,
					presence_penalty=0.0,
					logprobs=5,
					stop=['\n'],
					request_timeout=30.0,
				)
				current_tries += 1
				break
			except Exception as e:
				print('error-theme-new-2: ', str(e))
				curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
				curr_openAI_error.save()
				print('response theme retrying')
				if 'filtered' in str(e):
					break
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)
		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
				curr_safety_filter_obj.save()

			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			print('response more help 1:', curr_response_reframing_final)

			return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': prompt_type}, status=200)
		
		except:
			return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)
		

def get_more_help_2(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)

		situation = request.GET.get('situation', '')
		thought = request.GET.get('thought', '')
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', '')

		original_reframe = request.GET.get('original_reframe', '')

		prompt_type = request.GET.get('prompt_type', '')
		more_context = request.GET.get('more_context', '')

		curr_theme = request.GET.get('theme', '')

		print('curr_theme:', curr_theme)

		top_p = 0.8

		if prompt_type == 'actionable':
			curr_reframing_prompt = MORE_ACTIONABLE_PROMPTS
			prompt_input = curr_reframing_prompt + "\n\n" + 'Situation: ' + situation.strip() + '\nThought: ' + thought.strip() + '\nOriginal Reframe: ' + original_reframe.strip() + '\nActionable Reframe:'
		elif prompt_type == 'empathic':
			curr_reframing_prompt = MORE_EMPATHIC_PROMPTS
			prompt_input = curr_reframing_prompt + "\n\n" + 'Situation: ' + situation.strip() + '\nThought: ' + thought.strip() + '\nOriginal Reframe: ' + original_reframe.strip() + '\nEmpathetic Reframe:'
		elif prompt_type == 'personalized':
			top_p = 0.4
			curr_reframing_prompt = MORE_PERSONALIZED_PROMPTS
			prompt_input = curr_reframing_prompt + "\n\n" + 'Situation: ' + situation.strip() + '\nThought: ' + thought.strip() + '\nOriginal Reframe: ' + original_reframe.strip() + '\nAdditional Context: ' + more_context + '\nPersonalized Reframe:'


		MAX_RETRIES = 3

		

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				if current_tries <= 1:
					openai.api_base = "https://reframing20k2.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2024-02-15-preview"
					openai.api_type = "azure"
					deployment = "davinci-002"
					gpt3_model = deployment
				else:
					openai.api_base = "https://api.openai.com/v1"
					openai.api_key = os.getenv("OPENAI_API_KEY")
					openai.api_version = ""
					openai.api_type = "open_ai"
					deployment = "text-davinci-003"
					gpt3_model = deployment

				curr_response_reframing = openai.Completion.create(
					engine=gpt3_model,
					prompt=prompt_input,
					max_tokens=128,
					top_p=top_p,
					frequency_penalty=0.0,
					presence_penalty=0.0,
					logprobs=5,
					stop=['\n'],
					request_timeout=30.0,
				)
				current_tries += 1
				break
			except Exception as e:
				print('error-theme-new-2: ', str(e))
				curr_openAI_error = OpenAI_Error(thought_record_id = int(thought_record_id), input=curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:', response_no="3")
				curr_openAI_error.save()
				print('response theme retrying')
				if 'filtered' in str(e):
					break
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)
		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()

			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				curr_safety_filter_obj = Safety_Filter(thought_record_id = int(thought_record_id), text = curr_response_reframing_str, type = 'reframe')
				curr_safety_filter_obj.save()

			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			print('response more help 2:', curr_response_reframing_final)

			return JsonResponse({'reframed_thought': curr_response_reframing_final, 'prompt_type': prompt_type}, status=200)
		
		except:
			return JsonResponse({'reframed_thought': '', 'prompt_type': 'default_empty'}, status=200)



def combine_reframe_thoughts_more_help(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		# thinking_trap_selected_id = request.GET.get('thinking_trap_selected_id', None)
		original_reframe = request.GET.get('original_reframe', None)

		reframed_thought_1 = request.GET.get('reframed_thought_1', None)
		reframed_thought_2 = request.GET.get('reframed_thought_2', None)

		prompt_type_1 = request.GET.get('prompt_type_1', None)
		prompt_type_2 = request.GET.get('prompt_type_2', None)

		more_context = request.GET.get('more_context', '')

		reframed_thoughts_li_init = [reframed_thought_1, reframed_thought_2]
		reframed_thoughts_prompt_types_init = [prompt_type_1, prompt_type_2]

		reframed_thoughts_li = []
		reframed_thoughts_set = set()
		reframed_thoughts_prompt_types = []

		for idx, elem in enumerate(reframed_thoughts_li_init):
			if elem.strip().lower() not in reframed_thoughts_set:
				if elem.strip() != "":
					reframed_thoughts_li.append(elem)
					reframed_thoughts_prompt_types.append(reframed_thoughts_prompt_types_init[idx])
					reframed_thoughts_set.add(elem.strip().lower())

		
		default_reframe_li = ["It's understandable to feel overwhelmed in this situation. It's important to remember that things can get better. I can reach out for help and find ways to cope with my feelings.", \
							"Life can be difficult and it's okay to feel overwhelmed. I'm hoping to find healthier ways to cope with these difficult emotions.", "Life can be hard, but it's important to remember that things can get better. I'm going to focus on finding ways to cope with my difficult emotions."]
		
		shuffle(default_reframe_li)

		deafult_idx = 0

		while len(reframed_thoughts_li) < 1:
			if default_reframe_li[deafult_idx].lower() not in reframed_thoughts_set:
				reframed_thoughts_li.append(default_reframe_li[deafult_idx])
				reframed_thoughts_prompt_types.append('Default')
				reframed_thoughts_set.add(default_reframe_li[deafult_idx].lower())
				deafult_idx += 1
					

		for idx, elem in enumerate(reframed_thoughts_li):
			print('reframed thought', idx, elem.strip())
			
		print('===============================================\n\n')
		
		reframed_thoughts_all_str = ';'.join(reframed_thoughts_li)
		reframed_thoughts_prompt_types_str = ';'.join(reframed_thoughts_prompt_types)

		curr_thought_record = Reframes_More_Help(thought_record_id = int(thought_record_id), original_reframe=original_reframe, reframe_generated = reframed_thoughts_all_str, reframe_generated_prompt_type = reframed_thoughts_prompt_types_str, more_context = more_context)

		curr_thought_record.save()

		reframes_generated_id = curr_thought_record.reframes_more_help_id

		return JsonResponse({'out': reframed_thoughts_li, 'reframes_generated_id': reframes_generated_id,}, status=200)



def combine_reframed_thoughts_single(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		# thinking_trap_selected_id = request.GET.get('thinking_trap_selected_id', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		try:
			thinking_trap_selected_id = Thinking_Trap_Selected.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].thinking_trap_selected_id
		except:
			thinking_trap_selected_id = 0

		reframed_thought_1 = request.GET.get('reframed_thought_1', None)

		prompt_type_1 = request.GET.get('prompt_type_1', None)


		reframed_thoughts_li_init = [reframed_thought_1, ]
		reframed_thoughts_prompt_types_init = [prompt_type_1, ]

		reframed_thoughts_li = []
		reframed_thoughts_set = set()
		reframed_thoughts_prompt_types = []

		for idx, elem in enumerate(reframed_thoughts_li_init):
			if elem.strip().lower() not in reframed_thoughts_set:
				if elem.strip() != "":
					reframed_thoughts_li.append(elem)
					reframed_thoughts_prompt_types.append(reframed_thoughts_prompt_types_init[idx])
					reframed_thoughts_set.add(elem.strip().lower())
		

		if len(reframed_thoughts_li) < 1:
			if "this is a difficult situation, but i'll get through this" not in  reframed_thoughts_set:
				reframed_thoughts_li.append("This is a difficult situation, but I'll get through this")
				reframed_thoughts_prompt_types.append('Default')
			

		for idx, elem in enumerate(reframed_thoughts_li):
			print('reframed thought', idx, elem.strip())
			
		print('===============================================\n\n')
		
		reframed_thoughts_all_str = ';'.join(reframed_thoughts_li)
		reframed_thoughts_prompt_types_str = ';'.join(reframed_thoughts_prompt_types)

		curr_thought_record = Reframes_Generated(thought_record_id = int(thought_record_id), reframe_generated = reframed_thoughts_all_str, reframe_generated_prompt_type = reframed_thoughts_prompt_types_str, thinking_trap_selected_id = int(thinking_trap_selected_id))

		curr_thought_record.save()

		reframes_generated_id = curr_thought_record.reframes_generated_id

		return JsonResponse({'out': reframed_thoughts_li, 'cognitive_distortion_definition': DISTORTION_DEFINITIONS[cognitive_distortion_category], 'reframes_generated_id': reframes_generated_id}, status=200) 


def combine_reframed_thoughts(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		# thinking_trap_selected_id = request.GET.get('thinking_trap_selected_id', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		try:
			thinking_trap_selected_id = Thinking_Trap_Selected.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].thinking_trap_selected_id
		except:
			thinking_trap_selected_id = 0

		reframed_thought_1 = request.GET.get('reframed_thought_1', None)
		reframed_thought_2 = request.GET.get('reframed_thought_2', None)
		reframed_thought_3 = request.GET.get('reframed_thought_3', None)

		prompt_type_1 = request.GET.get('prompt_type_1', None)
		prompt_type_2 = request.GET.get('prompt_type_2', None)
		prompt_type_3 = request.GET.get('prompt_type_3', None)


		reframed_thoughts_li_init = [reframed_thought_1, reframed_thought_2, reframed_thought_3]
		reframed_thoughts_prompt_types_init = [prompt_type_1, prompt_type_2, prompt_type_3]

		reframed_thoughts_li = []
		reframed_thoughts_set = set()
		reframed_thoughts_prompt_types = []

		for idx, elem in enumerate(reframed_thoughts_li_init):
			if elem.strip().lower() not in reframed_thoughts_set:
				if elem.strip() != "":
					reframed_thoughts_li.append(elem)
					reframed_thoughts_prompt_types.append(reframed_thoughts_prompt_types_init[idx])
					reframed_thoughts_set.add(elem.strip().lower())
		

		this_is_a_difficult_situation = 0
		
		default_reframe_li = ["It's understandable to feel overwhelmed in this situation. It's important to remember that things can get better. I can reach out for help and find ways to cope with my feelings.", \
							"Life can be difficult and it's okay to feel overwhelmed. I'm hoping to find healthier ways to cope with these difficult emotions.", "Life can be hard, but it's important to remember that things can get better. I'm going to focus on finding ways to cope with my difficult emotions."]
		
		shuffle(default_reframe_li)

		deafult_idx = 0

		while len(reframed_thoughts_li) < 3:
			if default_reframe_li[deafult_idx].lower() not in reframed_thoughts_set:
				reframed_thoughts_li.append(default_reframe_li[deafult_idx])
				reframed_thoughts_prompt_types.append('Default')
				reframed_thoughts_set.add(default_reframe_li[deafult_idx].lower())
				deafult_idx += 1
			

		for idx, elem in enumerate(reframed_thoughts_li):
			print('reframed thought', idx, elem.strip())
			
		print('===============================================\n\n')
		
		reframed_thoughts_all_str = ';'.join(reframed_thoughts_li)
		reframed_thoughts_prompt_types_str = ';'.join(reframed_thoughts_prompt_types)

		curr_thought_record = Reframes_Generated(thought_record_id = int(thought_record_id), reframe_generated = reframed_thoughts_all_str, reframe_generated_prompt_type = reframed_thoughts_prompt_types_str, thinking_trap_selected_id = int(thinking_trap_selected_id))

		curr_thought_record.save()

		reframes_generated_id = curr_thought_record.reframes_generated_id

		# reframed_thoughts_li = ["I may not have won the hackathon, but I can use this experience to learn and grow.", "Losing the hackathon does not indicate that I cannot become a successful programmer. It simply means I have some more learning to do.", 'I may not become the most successful programmer, but I can continue participating in hackathons and improving my skills.']

		# reframed_thoughts_li = ["Rejection is a part of the process. I will take the feedback I received and use it to improve my paper.", "It's normal to feel disappointed when something doesn't go as planned. I can use this experience to learn and grow.", "Receiving a rejection does not mean that I will never become a successful researcher. I will continue to work hard and improve my skills."]

		# reframed_thoughts_li = ["It is normal to feel disappointed when a paper gets rejected. I can take the feedback I received and use it to improve my paper", "It is normal to feel disappointed when a paper gets rejected", "It is normal to feel disappointed when a paper gets rejected. I can use this experience to learn and grow"]

		# reframed_thoughts_li = ["I'm imagining the worst-case scenario. This project did not work out, but I can use this experience for my future projects.", "This research project was a setback, but it is just one step in my PhD journey. I will take this as a learning experience and I'm sure I will do better next time.", "I am disappointed that my research project failed, but I can still complete my PhD if I keep working hard and don’t give up."]



		return JsonResponse({'out': reframed_thoughts_li, 'reframes_generated_id': reframes_generated_id, 'this_is_a_difficult_situation': this_is_a_difficult_situation}, status=200) 
	


def combine_reframed_thoughts_new(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', None)
		# thinking_trap_selected_id = request.GET.get('thinking_trap_selected_id', None)
		cognitive_distortion_category = request.GET.get('cognitive_distortion_category', None)

		try:
			thinking_trap_selected_id = Thinking_Trap_Selected.objects.filter(thought_record_id = int(thought_record_id),).order_by('-updated_at')[0].thinking_trap_selected_id
		except:
			thinking_trap_selected_id = 0

		reframed_thought_1 = request.GET.get('new_reframed_thought_1', None)
		reframed_thought_2 = request.GET.get('new_reframed_thought_2', None)
		reframed_thought_3 = request.GET.get('new_reframed_thought_3', None)

		prompt_type_1 = request.GET.get('new_prompt_type_1', None)
		prompt_type_2 = request.GET.get('new_prompt_type_2', None)
		prompt_type_3 = request.GET.get('new_prompt_type_3', None)

		old_reframed_thought_1 = request.GET.get('old_reframed_thought_1', None)
		old_reframed_thought_2 = request.GET.get('old_reframed_thought_2', None)
		old_reframed_thought_3 = request.GET.get('old_reframed_thought_3', None)

		this_is_a_difficult_situation = request.GET.get('this_is_a_difficult_situation', 0)

		print('this_is_a_difficult_situation:', this_is_a_difficult_situation)



		old_reframed_thought_li = set([old_reframed_thought_1.strip().lower(), old_reframed_thought_2.strip().lower(), old_reframed_thought_3.strip().lower()])


		reframed_thoughts_li_init = [reframed_thought_1, reframed_thought_2, reframed_thought_3]
		reframed_thoughts_prompt_types_init = [prompt_type_1, prompt_type_2, prompt_type_3]

		reframed_thoughts_li = []
		reframed_thoughts_set = set()
		reframed_thoughts_prompt_types = []

		for idx, elem in enumerate(reframed_thoughts_li_init):
			if elem.strip().lower() not in reframed_thoughts_set and elem.strip().lower() not in old_reframed_thought_li:
				if elem.strip() != "":
					reframed_thoughts_li.append(elem)
					reframed_thoughts_prompt_types.append(reframed_thoughts_prompt_types_init[idx])
					reframed_thoughts_set.add(elem.strip().lower())
		

		if this_is_a_difficult_situation == 0 and len(reframed_thoughts_li) < 3:
			if "this is a difficult situation, but i'll get through this" not in  reframed_thoughts_set and "this is a difficult situation, but i'll get through this" not in old_reframed_thought_li:
				reframed_thoughts_li.append("This is a difficult situation, but I'll get through this")
				reframed_thoughts_prompt_types.append('Default')


		for idx, elem in enumerate(reframed_thoughts_li):
			print('reframed thought', idx, elem.strip())
			
		print('===============================================\n\n')
		
		reframed_thoughts_all_str = ';'.join(reframed_thoughts_li)
		reframed_thoughts_prompt_types_str = ';'.join(reframed_thoughts_prompt_types)

		curr_thought_record = Reframes_Generated(thought_record_id = int(thought_record_id), reframe_generated = reframed_thoughts_all_str, reframe_generated_prompt_type = reframed_thoughts_prompt_types_str, thinking_trap_selected_id = int(thinking_trap_selected_id))

		curr_thought_record.save()

		reframes_generated_id = curr_thought_record.reframes_generated_id

		

		return JsonResponse({'out': reframed_thoughts_li, 'reframes_generated_id': reframes_generated_id}, status=200) 
