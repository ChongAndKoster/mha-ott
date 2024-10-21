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

import json
import requests

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','overcoming_thinking_traps.settings')

import django
django.setup()

import pandas as pd

import psycopg2


from study.models import *

from pytz import timezone


RECAP_API_TOKEN = os.environ.get('RECAP_API_TOKEN')

STUDY_ID_TO_EMAIL = {}


def update_date_started(date_started, username):
	if date_started == None or username == None:
		return

	print('date_started: ', date_started)

	week_1_start = date_started
	week_1_expire = week_1_start + datetime.timedelta(days=7) - datetime.timedelta(minutes=2)

	# print('week_1_start: ', week_1_start)
	# print('week_1_expire: ', week_1_expire)

	week_2_start = date_started + datetime.timedelta(days=7)
	week_2_expire = week_2_start + datetime.timedelta(days=7)  - datetime.timedelta(minutes=2)

	week_3_start = date_started + datetime.timedelta(days=14)
	week_3_expire = week_3_start + datetime.timedelta(days=7) - datetime.timedelta(minutes=2)

	week_4_start = date_started + datetime.timedelta(days=21)
	week_4_expire = week_4_start + datetime.timedelta(days=7) - datetime.timedelta(minutes=2)

	# update UserDetails
	# username=username, date_started=date_started, week_1_start=week_1_start, week_1_expire=week_1_expire, week_2_start=week_2_start, week_2_expire=week_2_expire, week_3_start=week_3_start, week_3_expire=week_3_expire, week_4_start=week_4_start, week_4_expire=week_4_expire, condition=condition,
	UserDetails.objects.filter(username=username).update(date_started=date_started, week_1_start=week_1_start, week_1_expire=week_1_expire, week_2_start=week_2_start, week_2_expire=week_2_expire, week_3_start=week_3_start, week_3_expire=week_3_expire, week_4_start=week_4_start, week_4_expire=week_4_expire)


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
	# phq_1 = record['phq_1']
	# phq_2 = record['phq_2']
	# phq_3 = record['phq_3']
	# phq_4 = record['phq_4']
	# phq_5 = record['phq_5']
	# phq_6 = record['phq_6']
	# phq_7 = record['phq_7']
	# phq_8 = record['phq_8']
	# phq_9 = record['phq_9']
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
	# phq_total = record['phq_total']
	# phq_difficult = record['phq_difficult']
	phq9_complete = record['phq9_complete']
	# gad7_q1 = record['gad7_q1']
	# gad7_q2 = record['gad7_q2']
	# gad7_q3 = record['gad7_q3']
	# gad7_q4 = record['gad7_q4']
	# gad7_q5 = record['gad7_q5']
	# gad7_q6 = record['gad7_q6']
	# gad7_q7 = record['gad7_q7']
	# gad7_total = record['gad7_total']
	# gad7_q8 = record['gad7_q8']
	gad7_complete = record['gad7_complete']
	# cr_use_q = record['cr_use_q']
	# cr_use_complete = record['cr_use_complete']
	# hope_q = record['hope_q']
	hope_complete = record['hope_complete']
	# week_1_arm_1
	# phq9_complete
	# gad7_complete
	# hope_complete
	# em_complete
	# ccts_complete
	# em_1 = record['em_1']
	# em_2 = record['em_2']
	# em_3 = record['em_3']
	# em_4 = record['em_4']
	# em_5 = record['em_5']
	# em_6 = record['em_6']
	em_complete = record['em_complete']
	# ccts_20 = record['ccts_20']
	# ccts_28 = record['ccts_28']
	# ccts_21 = record['ccts_21']
	# ccts_06 = record['ccts_06']
	# ccts_24 = record['ccts_24']
	# ccts_11 = record['ccts_11']
	# ccts_elab = record['ccts_elab']
	# ccts_wellbeing = record['ccts_wellbeing']
	# ccts_other = record['ccts_other']
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
	# therapy = record['therapy']
	# talk = record['talk']
	# seekmh = record['seekmh']
	# practice_cr = record['practice_cr']
	# excite_mhskill = record['excite_mhskill']
	# life_impact = record['life_impact']
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


	# print('email: ', email)
	# # print('consent_complete: ', consent_complete)
	# print('condition: ', condition)

	# print('#################')

	if study_id != '' and int(study_id) < 70:
		continue

	if email != '':
		STUDY_ID_TO_EMAIL[study_id] = email.lower()



	# create user
	if (condition == '0' or condition == '1' or condition == '2') and redcap_event_name == "baseline_arm_1" and email != '' and n8m95 != '':
		# if user doesn't exist, create user
		email = email.lower()
			
		try:
			if date_consent != '':
				prev_date_started = UserDetails.objects.filter(username=email)[0].date_started

				# check if prev_date_started is same as date_consent

				date_consent = datetime.datetime.strptime(date_consent, '%Y-%m-%d')

				# date_consent as datetime with date = date_consent and time = 00:00:01 PT
				date_consent = datetime.datetime.combine(date_consent.date(), datetime.datetime.min.time()) + datetime.timedelta(hours=8) + datetime.timedelta(minutes=1)
				date_consent = date_consent.astimezone(timezone('US/Pacific'))

				if prev_date_started != date_consent:
					update_date_started(date_consent, email)
					print('updated date_started', email, prev_date_started, date_consent)
		except Exception as e:
			print('Error: ', e)


	if consent_complete == '2' and consent_yn == '1' and study_id != '':
		# update week no counts

		# get completed thought records

		# Get all thought records

		email = STUDY_ID_TO_EMAIL[study_id]

		# print('email: ', email)

		thought_records = ThoughtRecord.objects.filter(username = email)

		if len(thought_records) == 0:
			continue

		

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

		# check week no based on created_at

		week_1_use = 0
		week_2_use = 0
		week_3_use = 0
		week_4_use = 0

		# get date_started from UserDetails
		date_started = UserDetails.objects.filter(username = email)[0].week_1_start

		true_week_1_use = UserDetails.objects.filter(username = email)[0].week_1_use
		true_week_2_use = UserDetails.objects.filter(username = email)[0].week_2_use
		true_week_3_use = UserDetails.objects.filter(username = email)[0].week_3_use
		true_week_4_use = UserDetails.objects.filter(username = email)[0].week_4_use



		for index, row in thought_records_df.iterrows():

			curr_date = row['created_at']

			

			# compute week_no
			week_no = (curr_date - date_started).days // 7 + 1

			if week_no == 1:
				week_1_use += 1
			
			if week_no == 2:
				week_2_use += 1
			
			if week_no == 3:
				week_3_use += 1
			
			if week_no == 4:
				week_4_use += 1


		if week_1_use != true_week_1_use:
			print(study_id, 'week_1_use', week_1_use, true_week_1_use)
			# print(thought_records_df)

			# update UserDetails
			UserDetails.objects.filter(username=email).update(week_1_use=week_1_use)


		
		if week_2_use != true_week_2_use:
			print(study_id, 'week_2_use', week_2_use, true_week_2_use)

			# update UserDetails
			UserDetails.objects.filter(username=email).update(week_1_use=week_1_use)

		if week_3_use != true_week_3_use:
			print(study_id, 'week_3_use', week_3_use, true_week_3_use)

			# update UserDetails
			UserDetails.objects.filter(username=email).update(week_1_use=week_1_use)
		
		if week_4_use != true_week_4_use:
			print(study_id, 'week_4_use', week_4_use, true_week_4_use)

			# update UserDetails
			UserDetails.objects.filter(username=email).update(week_1_use=week_1_use)

		# print(email, 'processed...')
