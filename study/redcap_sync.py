import json
import requests
import os
import datetime

from study.models import UserDetails, \
						Redcap_Last_Sync, \
						Redcap_Welcome_Landing_Page, \
						Redcap_Admin, \
						Redcap_Events_Log, \
						Redcap_Consent, \
						Redcap_Psychoed, \
						Redcap_Entry_Survey, \
						Redcap_PHQ9, \
						Redcap_GAD7, \
						Redcap_CR_Use, \
						Redcap_Hope, \
						Redcap_EM, \
						Redcap_CCTS, \
						Redcap_Exit, \
						Redcap_MiscQ, \
						Redcap_Post_Diy, \
						Redcap_Tool_Use, \
						Redcap_Week_No, \
						Redcap_Payments

from users.models import CustomUser
from study.assign_user_tasks import assign_tasks

from pytz import timezone


RECAP_API_TOKEN = os.environ.get('RECAP_API_TOKEN')

cols_1 = ['study_id', 'redcap_event_name', 'n8m95', 'welcome_landing_page_complete', 'trigger_consent', 'condition', 'start_date', 'stop___1', 'test', 'admin_complete', 'comms_log', 'withdraw', 'date_withdraw', 'notes_withdraw', 'events_log_complete', 'consent_yn', 'consent_complete', 'psychoed_complete', 'age', 'us_res', 'first_name', 'last_name', 'email', 'contact_pref', 'phone', 'entry_survey_complete', 'phq_1', 'phq_2', 'phq_3', 'phq_4', 'phq_5', 'phq_6', 'phq_7', 'phq_8', 'phq_9', 'phq_calc_1', 'phq_calc_2', 'phq_calc_3', 'phq_calc_4', 'phq_calc_5', 'phq_calc_6', 'phq_calc_7', 'phq_calc_8', 'phq_calc_9', 'phq_answered', 'phq_total', 'phq_difficult', 'phq9_complete', 'gad7_q1', 'gad7_q2', 'gad7_q3', 'gad7_q4', 'gad7_q5', 'gad7_q6', 'gad7_q7', 'gad7_total', 'gad7_q8', 'gad7_complete', 'cr_use_q', 'cr_use_complete', 'hope_q', 'hope_complete', 'em_1', 'em_2', 'em_3', 'em_4', 'em_5', 'em_6', 'em_complete', 'ccts_20', 'ccts_28', 'ccts_21', 'ccts_06', 'ccts_24', 'ccts_11', 'ccts_elab', 'ccts_wellbeing', 'ccts_other', 'ccts_complete', 'impact_diy', 'use_diy', 'impact_y_diy', 'impact_n_diy', 'apply_diy', 'apply_y_diy', 'benefit_diy', 'benefit_y_diy', 'takeaways_diy', 'future_diy', 'change_diy', 'like_diy', 'dislike_diy', 'exit_complete', 'ther_yn', 'mhmeds_yn', 'therapy_post_diy', 'therapy', 'talk', 'seekmh', 'practice_cr', 'excite_mhskill', 'life_impact', 'miscq_complete', 'post_1', 'post_2', 'post_3', 'post_4', 'post_5', 'post_6', 'post_7', 'post_diy_complete', 'tool_1', 'tool_2', 'tool_3', 'tool_4', 'tool_5', 'tool_use_complete']


cols_2 = ['study_id', 'redcap_event_name', 'n8m95', 'welcome_landing_page_complete', 'status', 'condition', 'start_date', 'stop___1', 'test', 'admin_complete', 'comms_log', 'withdraw', 'date_withdraw', 'notes_withdraw', 'events_log_complete', 'consent_yn', 'consent_complete', 'psychoed_reminder_complete', 'tool_use_reminder_complete', 'age', 'us_res', 'first_name', 'last_name', 'email', 'contact_pref', 'phone', 'entry_survey_complete', 'phq_1', 'phq_2', 'phq_3', 'phq_4', 'phq_5', 'phq_6', 'phq_7', 'phq_8', 'phq_9', 'phq_calc_1', 'phq_calc_2', 'phq_calc_3', 'phq_calc_4', 'phq_calc_5', 'phq_calc_6', 'phq_calc_7', 'phq_calc_8', 'phq_calc_9', 'phq_answered', 'phq_total', 'phq_difficult', 'phq9_complete', 'gad7_q1', 'gad7_q2', 'gad7_q3', 'gad7_q4', 'gad7_q5', 'gad7_q6', 'gad7_q7', 'gad7_total', 'gad7_q8', 'gad7_complete', 'cr_use_q', 'cr_use_complete', 'hope_q', 'hope_complete', 'em_1', 'em_2', 'em_3', 'em_4', 'em_5', 'em_6', 'em_complete', 'ccts_20', 'ccts_28', 'ccts_21', 'ccts_06', 'ccts_24', 'ccts_11', 'ccts_elab', 'ccts_wellbeing', 'ccts_other', 'ccts_complete', 'impact_diy', 'use_diy', 'impact_y_diy', 'impact_n_diy', 'apply_diy', 'apply_y_diy', 'benefit_diy', 'benefit_y_diy', 'takeaways_diy', 'future_diy', 'change_diy', 'like_diy', 'dislike_diy', 'exit_complete', 'ther_yn', 'mhmeds_yn', 'therapy_post_diy', 'therapy', 'talk', 'seekmh', 'practice_cr', 'excite_mhskill', 'life_impact', 'miscq_complete', 'post_1', 'post_2', 'post_3', 'post_4', 'post_5', 'post_6', 'post_7', 'post_diy_complete', 'tool_1', 'tool_2', 'tool_3', 'tool_4', 'tool_5', 'tool_use_complete']


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


def redcap_sync(last_sync=False, login_sync=True):

	if last_sync:
		# check when it was last synced, sort by updated at
		try:
			last_sync = Redcap_Last_Sync.objects.all().order_by('-updated_at')[0]
			last_sync = last_sync.updated_at

			# if within 1 mins, don't sync
			now = datetime.datetime.now()
			
			last_sync = last_sync.replace(tzinfo=None)

			if (now - last_sync).total_seconds() < 20:
				print('last_sync: ', last_sync, 'Skipping...')
				return
		except Exception as e:
			print('last_sync: ', e)
			pass
		
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

		w1 = record['w1']
		w2 = record['w2']
		w3 = record['w3']
		w4 = record['w4']
		w5 = record['w5']
		w8 = record['w8']

		w1_paid = record['w1_paid']
		w1_amt = record['w1_amt']
		pay_date_w1 = record['pay_date_w1']

		w2_paid = record['w2_paid']
		w2_amt = record['w2_amt']
		pay_date_w2 = record['pay_date_w2']

		w3_paid = record['w3_paid']
		w3_amt = record['w3_amt']
		pay_date_w3 = record['pay_date_w3']

		w4_paid = record['w4_paid']
		w4_amt = record['w4_amt']
		pay_date_w4 = record['pay_date_w4']

		w5_paid = record['w5_paid']
		w5_amt = record['w5_amt']
		pay_date_w5 = record['pay_date_w5']

		w8_paid = record['w8_paid']
		w8_amt = record['w8_amt']
		pay_date_w8 = record['pay_date_w8']

		# create or update record
		# redcap_welcome_landing_page, created = Redcap_Welcome_Landing_Page.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'welcome_landing_page_complete': welcome_landing_page_complete,
		# 	}
		# )

		# redcap_admin, created = Redcap_Admin.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'trigger_consent': trigger_consent,
		# 		'condition': condition,
		# 		'start_date': start_date,
		# 		'stop_1': stop_1,
		# 		'test': test,
		# 		'admin_complete': admin_complete,
		# 	}
		# )

		# redcap_events_log, created = Redcap_Events_Log.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'comms_log': comms_log,
		# 		'withdraw': withdraw,
		# 		'date_withdraw': date_withdraw,
		# 		'notes_withdraw': notes_withdraw,
		# 		'events_log_complete': events_log_complete,
		# 	}
		# )

		# redcap_consent, created = Redcap_Consent.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'consent_yn': consent_yn,
		# 		'consent_complete': consent_complete,
		# 	}
		# )

		# redcap_psychoed, created = Redcap_Psychoed.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'psychoed_complete': psychoed_complete,
		# 	}
		# )

		# redcap_entry_survey, created = Redcap_Entry_Survey.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'age': age,
		# 		'us_res': us_res,
		# 		'first_name': first_name,
		# 		'last_name': last_name,
		# 		'email': email,
		# 		'contact_pref': contact_pref,
		# 		'phone': phone,
		# 		'entry_survey_complete': entry_survey_complete,
		# 	}
		# )

		# redcap_phq9, created = Redcap_PHQ9.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'phq_1': phq_1,
		# 		'phq_2': phq_2,
		# 		'phq_3': phq_3,
		# 		'phq_4': phq_4,
		# 		'phq_5': phq_5,
		# 		'phq_6': phq_6,
		# 		'phq_7': phq_7,
		# 		'phq_8': phq_8,
		# 		'phq_9': phq_9,
		# 		'phq_calc_1': phq_calc_1,
		# 		'phq_calc_2': phq_calc_2,
		# 		'phq_calc_3': phq_calc_3,
		# 		'phq_calc_4': phq_calc_4,
		# 		'phq_calc_5': phq_calc_5,
		# 		'phq_calc_6': phq_calc_6,
		# 		'phq_calc_7': phq_calc_7,
		# 		'phq_calc_8': phq_calc_8,
		# 		'phq_calc_9': phq_calc_9,
		# 		'phq_answered': phq_answered,
		# 		'phq_total': phq_total,
		# 		'phq_difficult': phq_difficult,
		# 		'phq9_complete': phq9_complete,
		# 	}
		# )

		# redcap_gad7, created = Redcap_GAD7.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'gad7_q1': gad7_q1,
		# 		'gad7_q2': gad7_q2,
		# 		'gad7_q3': gad7_q3,
		# 		'gad7_q4': gad7_q4,
		# 		'gad7_q5': gad7_q5,
		# 		'gad7_q6': gad7_q6,
		# 		'gad7_q7': gad7_q7,
		# 		'gad7_total': gad7_total,
		# 		'gad7_q8': gad7_q8,
		# 		'gad7_complete': gad7_complete,
		# 	}
		# )

		# redcap_cr_use, created = Redcap_CR_Use.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'cr_use_q': cr_use_q,
		# 		'cr_use_complete': cr_use_complete,
		# 	}
		# )

		# redcap_hope, created = Redcap_Hope.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'hope_q': hope_q,
		# 		'hope_complete': hope_complete,
		# 	}
		# )

		# redcap_em, created = Redcap_EM.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95 = n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'em_1': em_1,
		# 		'em_2': em_2,
		# 		'em_3': em_3,
		# 		'em_4': em_4,
		# 		'em_5': em_5,
		# 		'em_6': em_6,
		# 		'em_complete': em_complete,
		# 	}
		# )

		# redcap_ccts, created = Redcap_CCTS.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95=n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'ccts_20': ccts_20,
		# 		'ccts_28': ccts_28,
		# 		'ccts_21': ccts_21,
		# 		'ccts_06': ccts_06,
		# 		'ccts_24': ccts_24,
		# 		'ccts_11': ccts_11,
		# 		'ccts_elab': ccts_elab,
		# 		'ccts_wellbeing': ccts_wellbeing,
		# 		'ccts_other': ccts_other,
		# 		'ccts_complete': ccts_complete,
		# 	}
		# )

		# redcap_exit, created = Redcap_Exit.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95=n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'impact_diy': impact_diy,
		# 		'use_diy': use_diy,
		# 		'impact_y_diy': impact_y_diy,
		# 		'impact_n_diy': impact_n_diy,
		# 		'apply_diy': apply_diy,
		# 		'apply_y_diy': apply_y_diy,
		# 		'benefit_diy': benefit_diy,
		# 		'benefit_y_diy': benefit_y_diy,
		# 		'takeaways_diy': takeaways_diy,
		# 		'future_diy': future_diy,
		# 		'change_diy': change_diy,
		# 		'like_diy': like_diy,
		# 		'dislike_diy': dislike_diy,
		# 		'exit_complete': exit_complete,
		# 	}
		# )

		# redcap_miscq, created = Redcap_MiscQ.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95=n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'ther_yn': ther_yn,
		# 		'mhmeds_yn': mhmeds_yn,
		# 		'therapy_post_diy': therapy_post_diy,
		# 		'therapy': therapy,
		# 		'talk': talk,
		# 		'seekmh': seekmh,
		# 		'practice_cr': practice_cr,
		# 		'excite_mhskill': excite_mhskill,
		# 		'life_impact': life_impact,
		# 		'miscq_complete': miscq_complete,
		# 	}
		# )

		# redcap_post_diy, created = Redcap_Post_Diy.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95=n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'post_1': post_1,
		# 		'post_2': post_2,
		# 		'post_3': post_3,
		# 		'post_4': post_4,
		# 		'post_5': post_5,
		# 		'post_6': post_6,
		# 		'post_7': post_7,
		# 		'post_diy_complete': post_diy_complete,
		# 	}
		# )

		# redcap_tool_use, created = Redcap_Tool_Use.objects.update_or_create(
		# 	study_id=study_id,
		# 	n8m95=n8m95,
		# 	redcap_event_name=redcap_event_name,
		# 	defaults={
		# 		'tool_1': tool_1,
		# 		'tool_2': tool_2,
		# 		'tool_3': tool_3,
		# 		'tool_4': tool_4,
		# 		'tool_5': tool_5,
		# 		'tool_use_complete': tool_use_complete,
		# 	}
		# )

		# print('email: ', email)
		# # print('consent_complete: ', consent_complete)
		# print('condition: ', condition)

		# print('#################')

		if study_id != '' and int(study_id) < 70:
			continue


		# create user
		if (condition == '0' or condition == '1' or condition == '2') and redcap_event_name == "baseline_arm_1" and email != '' and n8m95 != '':
			# if user doesn't exist, create user
			email = email.lower()

			user = CustomUser.objects.filter(username=email)

			if not user:
				# check if UserDetail exists with n8m95
				user_details = UserDetails.objects.filter(n8m95=n8m95)

				if not user_details:
					# create user
					user = CustomUser.objects.create_user(username=email)
					user.save()

					print('condition: ', condition)
					print('start date: ', date_consent)

					assign_tasks(email, condition, date_consent, study_id, n8m95)

			else:
				# check if date_started needs to be updated
				
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

		if redcap_event_name == 'week_1_arm_1' and phq9_complete == '2' and gad7_complete == '2' and hope_complete == '2' and em_complete == '2' and ccts_complete == '2' and study_id != '':
			# update UserDetails with survey_1_status = 1
			# print('study_id:', study_id)

			try:
				user_details = UserDetails.objects.filter(study_id=study_id)[0]
				if user_details.survey_1_status == 0:
					user_details.survey_1_status = 1
					user_details.save()
					print('updated survey_1_status', study_id)
			except Exception as e:
				print('Error: ', e)
				print('Could not update survey_1_status', study_id)
		
		if redcap_event_name == 'week_2_arm_1' and phq9_complete == '2' and gad7_complete == '2' and hope_complete == '2' and em_complete == '2' and ccts_complete == '2' and study_id != '':
			# update UserDetails with survey_2_status = 1
			
			try:
				user_details = UserDetails.objects.filter(study_id=study_id)[0]

				if user_details.survey_2_status == 0:
					user_details.survey_2_status = 1
					user_details.save()
					print('updated survey_2_status', study_id)
				
			except Exception as e:
				print('Error: ', e)
				print('Could not update survey_2_status', study_id)
		
		if redcap_event_name == 'week_3_arm_1' and phq9_complete == '2' and gad7_complete == '2' and hope_complete == '2' and em_complete == '2' and ccts_complete == '2' and study_id != '':
			# update UserDetails with survey_3_status = 1
			
			try:
				user_details = UserDetails.objects.filter(study_id=study_id)[0]

				if user_details.survey_3_status == 0:
					user_details.survey_3_status = 1
					user_details.save()
					print('updated survey_3_status', study_id)

			except Exception as e:
				print('Error: ', e)
				print('Could not update survey_3_status', study_id)
		
		if redcap_event_name == 'week_4_arm_1' and phq9_complete == '2' and gad7_complete == '2' and hope_complete == '2' and em_complete == '2' and ccts_complete == '2' and study_id != '':
			# update UserDetails with survey_4_status = 1
			
			try:
				user_details = UserDetails.objects.filter(study_id=study_id)[0]
				if user_details.survey_4_status == 0:
					user_details.survey_4_status = 1
					user_details.save()
					print('updated survey_4_status', study_id)
			except Exception as e:
				print('Error: ', e)
				print('Could not update survey_4_status', study_id)


		if redcap_event_name == 'week_5_arm_1' and miscq_complete == '2' and study_id != '':
			# update UserDetails with survey_4_status = 1
			
			try:
				user_details = UserDetails.objects.filter(study_id=study_id)[0]

				curr_condition = int(user_details.condition)

				if curr_condition == 0:
					if user_details.survey_5_status == 0:
						user_details.survey_5_status = 1
						user_details.save()
						print('updated survey_5_status', study_id)

				else:
					# [week_5_arm_1][exit_complete]='2'
					if exit_complete == '2':
						if user_details.survey_5_status == 0:
							user_details.survey_5_status = 1
							user_details.save()
							print('updated survey_5_status', study_id)
			except Exception as e:
				print('Error: ', e)
				print('Could not update survey_5_status', study_id)

		if redcap_event_name == 'week_8_arm_1' and phq9_complete == '2' and gad7_complete == '2' and hope_complete == '2' and em_complete == '2' and ccts_complete == '2' and study_id != '':
			# update UserDetails with survey_4_status = 1
			
			try:
				user_details = UserDetails.objects.filter(study_id=study_id)[0]
				if user_details.survey_8_status == 0:
					user_details.survey_8_status = 1
					user_details.save()
					print('updated survey_8_status', study_id)
			except Exception as e:
				print('Error: ', e)
				print('Could not update survey_8_status', study_id)


		if consent_complete == '2' and consent_yn == '1' and study_id != '':
			# if Redcap_Consent object doesn't exist, create it
			try:
				redcap_consent, created = Redcap_Consent.objects.update_or_create(
					study_id=study_id,
					n8m95 = n8m95,
					redcap_event_name=redcap_event_name,
					defaults={
						'consent_yn': consent_yn,
						'consent_complete': consent_complete,
					}
				)
			except Exception as e:
				print('Error: ', e)
				print('Could not update consent_complete', study_id)

		
		if redcap_event_name == 'baseline_arm_1' and study_id != '' and login_sync == False:
			# Redcap_Payments, Redcap_Week_No

			# class Redcap_Week_No(BaseModel):
			# 	study_id = models.TextField()

			# 	w1 = models.TextField(default='')
			# 	w2 = models.TextField(default='')
			# 	w3 = models.TextField(default='')
			# 	w4 = models.TextField(default='')
			# 	w5 = models.TextField(default='')
			# 	w8 = models.TextField(default='')


			# class Redcap_Payments(BaseModel):
			# 	study_id = models.TextField()
				
			# 	w1_paid = models.TextField(default='')
			# 	w1_amt = models.TextField(default='')
			# 	pay_date_w1 = models.TextField(default='')

			# 	w2_paid = models.TextField(default='')
			# 	w2_amt = models.TextField(default='')
			# 	pay_date_w2 = models.TextField(default='')

			# 	w3_paid = models.TextField(default='')
			# 	w3_amt = models.TextField(default='')
			# 	pay_date_w3 = models.TextField(default='')

			# 	w4_paid = models.TextField(default='')
			# 	w4_amt = models.TextField(default='')
			# 	pay_date_w4 = models.TextField(default='')

			# 	w5_paid = models.TextField(default='')
			# 	w5_amt = models.TextField(default='')
			# 	pay_date_w5 = models.TextField(default='')

			# 	w8_paid = models.TextField(default='')
			# 	w8_amt = models.TextField(default='')
			# 	pay_date_w8 = models.TextField(default='')


			if w1 != '':
				# check if Redcap_Week_No exists
				curr_week_no = Redcap_Week_No.objects.filter(study_id=study_id)

				if not curr_week_no:
					# create
					redcap_week_no = Redcap_Week_No.objects.create(study_id=study_id, w1=w1, w2=w2, w3=w3, w4=w4, w5=w5, w8=w8)
					redcap_week_no.save()
					print('created week_no', study_id)
					

			# update or create Redcap_Payments

			try:
				curr_redcap_payments, created = Redcap_Payments.objects.update_or_create(
					study_id=study_id,
					defaults={
						'w1_paid': w1_paid,
						'w1_amt': w1_amt,
						'pay_date_w1': pay_date_w1,

						'w2_paid': w2_paid,
						'w2_amt': w2_amt,
						'pay_date_w2': pay_date_w2,

						'w3_paid': w3_paid,
						'w3_amt': w3_amt,
						'pay_date_w3': pay_date_w3,

						'w4_paid': w4_paid,
						'w4_amt': w4_amt,
						'pay_date_w4': pay_date_w4,

						'w5_paid': w5_paid,
						'w5_amt': w5_amt,
						'pay_date_w5': pay_date_w5,

						'w8_paid': w8_paid,
						'w8_amt': w8_amt,
						'pay_date_w8': pay_date_w8,
					}
				)
			except Exception as e:
				print('Error: ', e)
				print('Could not update payments', study_id)

	# update last sync
	redcap_last_sync, created = Redcap_Last_Sync.objects.update_or_create(
		defaults={
			'updated_at': datetime.datetime.now()
		}
	)




