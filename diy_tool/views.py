import random
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



from .models import User, \
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
					Reframes_More_Help

# Create your views here.

# from .rational_responses import PROMPTS

'''
OpenAI API
'''
import openai
# openai.organization = "org-o2Ssn2MTYvpMDkvzRSiehlv4"
openai.api_key = os.getenv("OPENAI_API_KEY")

from diy_tool.definitions import *
from diy_tool.prompts import *
from diy_tool.themes_prompt import *
from diy_tool.themes_prompt_new import *
from diy_tool.themes_prompt_v3 import *


# COLORS = ["text-primary", 
# 		"text-success",
# 		"text-danger",
# 		"text-warning",
# 		"text-info",
# 		"text-secondary",]

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


def RCT(request):
	condition = request.GET.get('condition', None)

	referral_code = request.GET.get('referral_code', None)

	if condition == None:
		condition = np.random.choice(['AI', 'no AI'], p=[0.5, 0.5])

	if condition == 'AI':
		# redirect and pass referral_code
		if referral_code:
			return redirect('/diy_tool/RCT_AI?referral_code=' + referral_code)
		else:
			return redirect('/diy_tool/RCT_AI')
	else:
		if referral_code:
			return redirect('/diy_tool/RCT_no_AI?referral_code=' + referral_code)
		else:
			return redirect('/diy_tool/RCT_no_AI')

def RCT_AI(request):
		# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
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
		prompt_to_use = np.random.choice(['expert_v3_gpt3', 'expert_v3_gpt4'], p=[0.5, 0.5])
	
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
		skip_step = '0' # np.random.choice(['0', '3'], p=[0.5, 0.5])

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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/RCT_AI.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation, 'ai': ai, 'include_emotions': include_emotions})



def RCT_no_AI(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
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
		skip_step = '0' # np.random.choice(['0', '3'], p=[0.5, 0.5])

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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/RCT_no_AI.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation, 'ai': ai})


def old_index(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		curr_user = User(user_id = user_id, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
	skip_step = request.GET.get('skip_step', None)

	prompt_to_use = request.GET.get('prompt_to_use', None)
	more_suggestions_btn = request.GET.get('more_suggestions_btn', None)

	# Randomly assign remove_negative_feeling

	refresh_btn = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	remove_negative_feeling = 0 #np.random.choice([0, 1], p=[0.5, 0.5])


	if prompt_to_use == None:
		prompt_to_use = np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = np.random.choice([0, 1], p=[0.5, 0.5])


	# remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

	skip_step_li = []

	if skip_step:
		skip_step_li_str = skip_step.strip().split(',')
		skip_step_li = [int(elem) for elem in skip_step_li_str]
	else:
		skip_step = ''

	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn)
		curr_thought_record.save()

	

	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/old_index.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn})
	
	# else:
	# 	return redirect('/users/login/')


def index_old_outcomes(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
	skip_step = request.GET.get('skip_step', None)

	prompt_to_use = request.GET.get('prompt_to_use', None)
	more_suggestions_btn = request.GET.get('more_suggestions_btn', None)

	descriptive_thought_Q = request.GET.get('descriptive_thought_Q', None)

	multiple_cognitive_distortions = request.GET.get('multiple_cognitive_distortions', None)

	A_A = request.GET.get('A_A', None)

	extra_q = request.GET.get('extra_q', None)	

	# Randomly assign remove_negative_feeling

	refresh_btn = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	remove_negative_feeling = 0 # np.random.choice([0, 1], p=[0.5, 0.5])


	if prompt_to_use == None:
		prompt_to_use = np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = np.random.choice([0, 1], p=[0.5, 0.5])

	if extra_q == None:
		extra_q = np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		extra_q = int(extra_q)

	# if skip_step == None:
	# 	skip_step = np.random.choice(['0', '3'], p=[0.5, 0.5])

	# 	if skip_step == '0':
	# 		skip_step = None

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

	situation_step_no = 2
	thinking_trap_step_no = 3
	reframe_step_no = 4
	evaluate_step_no = 5

	for elem in skip_step_li:
		if elem in {2, 3, 4}:
			num_skipped_steps += 1

		if elem == 2:
			situation_step_no -= 1
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 3:
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 4:
			reframe_step_no -= 1
			evaluate_step_no -= 1


	total_steps = 5 - num_skipped_steps

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index_old_outcomes.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q})




def index(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	ai = -1

	referral_code = request.GET.get('referral_code', None)
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

	if prompt_to_use == None:
		prompt_to_use = np.random.choice(['expert_v3_gpt3', 'expert_v3_gpt4'], p=[0.5, 0.5])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = 1 # np.random.choice([0, 1], p=[0.5, 0.5])

	if extra_q == None:
		extra_q = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		extra_q = int(extra_q)

	if emotion_questions == None:
		emotion_questions = np.random.choice(['first', 'second'], p=[0.5, 0.5])

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
		skip_step = '0' # np.random.choice(['0', '3'], p=[0.5, 0.5])

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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation, 'ai': ai, 'include_emotions': include_emotions})




def index_no_AI(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
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

	ai = -2

	if prompt_to_use == None:
		prompt_to_use = 'expert_new' #np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
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

	if psychoeducation == None:
		psychoeducation = 1 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		psychoeducation = int(psychoeducation)

	if skip_step == None:
		skip_step = '0' # np.random.choice(['0', '3'], p=[0.5, 0.5])

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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index_no_AI.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation, 'ai': ai})



def index_save(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
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


	if prompt_to_use == None:
		prompt_to_use = np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = np.random.choice([0, 1], p=[0.5, 0.5])

	if extra_q == None:
		extra_q = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		extra_q = int(extra_q)

	if emotion_questions == None:
		emotion_questions = np.random.choice(['first', 'second'], p=[0.5, 0.5])

	if personalize == None:
		personalize = np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		personalize = int(personalize)
	
	if readable == None:
		readable = np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		readable = int(readable)

	if psychoeducation == None:
		psychoeducation = np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		psychoeducation = int(psychoeducation)

	if skip_step == None:
		skip_step = np.random.choice(['0', '3'], p=[0.5, 0.5])

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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index_save.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation})



def index_demo(request):
		# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
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


	if prompt_to_use == None:
		prompt_to_use = 'initial' # np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = 1 # np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if extra_q == None:
		extra_q = 0 # np.random.choice([0, 1], p=[0.5, 0.5])
	else:
		extra_q = int(extra_q)

	if emotion_questions == None:
		emotion_questions = 'first' # np.random.choice(['first', 'second'], p=[0.5, 0.5])

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
		skip_step = '0' # np.random.choice(['0', '3'], p=[0.5, 0.5])

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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index_demo.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'emotion_step_no': emotion_step_no, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions, 'extra_q': extra_q, 'emotion_questions': emotion_questions, 'personalize': personalize, 'readable': readable, 'psychoeducation': psychoeducation})


def index_multiple_select(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
	skip_step = request.GET.get('skip_step', None)

	prompt_to_use = request.GET.get('prompt_to_use', None)
	more_suggestions_btn = request.GET.get('more_suggestions_btn', None)

	descriptive_thought_Q = request.GET.get('descriptive_thought_Q', None)

	multiple_cognitive_distortions = request.GET.get('multiple_cognitive_distortions', None)

	A_A = request.GET.get('A_A', None)

	# Randomly assign remove_negative_feeling

	refresh_btn = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	remove_negative_feeling = 0 # np.random.choice([0, 1], p=[0.5, 0.5])


	if prompt_to_use == None:
		prompt_to_use = 'expert_new' # np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = np.random.choice([0, 1], p=[0.5, 0.5])

	if multiple_cognitive_distortions == None:
		multiple_cognitive_distortions = np.random.choice([0, 1], p=[0.5, 0.5])

	# if skip_step == None:
	# 	skip_step = np.random.choice(['0', '3'], p=[0.5, 0.5])

	# 	if skip_step == '0':
	# 		skip_step = None

	# remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

	skip_step_li = []

	if skip_step:
		skip_step_li_str = skip_step.strip().split(',')
		skip_step_li = [int(elem) for elem in skip_step_li_str]
	else:
		skip_step = ''

	# if descriptive_thought_Q == None:
	# 	if 3 in skip_step_li:
	# 		descriptive_thought_Q = np.random.choice([0, 1], p=[0.5, 0.5])
	
	# Count number of skipped steps
	num_skipped_steps = 0

	situation_step_no = 2
	thinking_trap_step_no = 3
	reframe_step_no = 4
	evaluate_step_no = 5

	for elem in skip_step_li:
		if elem in {2, 3, 4}:
			num_skipped_steps += 1

		if elem == 2:
			situation_step_no -= 1
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 3:
			thinking_trap_step_no -= 1
			reframe_step_no -= 1
			evaluate_step_no -= 1
		if elem == 4:
			reframe_step_no -= 1
			evaluate_step_no -= 1


	total_steps = 5 - num_skipped_steps

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index_multiple_select.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step': skip_step, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A, 'multiple_cognitive_distortions': multiple_cognitive_distortions})



def index_collaborative(request):
	# if request.user.is_authenticated and request.user.username == 'test_user':
	# Generate new_user_id
	
	# Compute Loading time

	start_time = time.time()

	try:
		max_user_id = User.objects.all().order_by("-user_id")[0].user_id
	except:
		max_user_id = 0


	if 'user_id' in request.session:
		user_id = request.session['user_id']
		condition = request.session['condition']

	else:
		user_id = max_user_id + 1
		condition = 0
		ip_address = get_ip_address(request)
		curr_user = User(user_id = user_id, ip_address = ip_address, condition = condition)
		curr_user.save()

		request.session['user_id'] = max_user_id + 1
		request.session['condition'] = condition

	referral_code = request.GET.get('referral_code', None)
	skip_step = request.GET.get('skip_step', None)

	prompt_to_use = request.GET.get('prompt_to_use', None)
	more_suggestions_btn = request.GET.get('more_suggestions_btn', None)

	descriptive_thought_Q = request.GET.get('descriptive_thought_Q', None)

	A_A = request.GET.get('A_A', None)

	# Randomly assign remove_negative_feeling

	refresh_btn = 0 # np.random.choice([0, 1], p=[0.5, 0.5])

	remove_negative_feeling = 0 # np.random.choice([0, 1], p=[0.5, 0.5])


	if prompt_to_use == None:
		prompt_to_use = 'expert_new' # np.random.choice(['initial', 'expert', 'expert_new'], p=[0.33, 0.33, 0.34])
	
	if more_suggestions_btn == None:
		more_suggestions_btn = 1 #np.random.choice([0, 1], p=[0.5, 0.5])

	if A_A == None:
		A_A = np.random.choice([0, 1], p=[0.5, 0.5])

	# if skip_step == None:
	# 	skip_step = np.random.choice(['0', '3'], p=[0.5, 0.5])

	# 	if skip_step == '0':
	# 		skip_step = None

	# remove_negative_feeling = int(request.GET.get('remove_negative_feeling', 0))

	skip_step_li = []

	if skip_step:
		skip_step_li_str = skip_step.strip().split(',')
		skip_step_li = [int(elem) for elem in skip_step_li_str]
	else:
		skip_step = ''

	# if descriptive_thought_Q == None:
	# 	if 3 in skip_step_li:
	# 		descriptive_thought_Q = np.random.choice([0, 1], p=[0.5, 0.5])
	
	# Count number of skipped steps
	num_skipped_steps = 0

	situation_step_no = 3
	thinking_trap_step_no = 4
	reframe_step_no = 5
	evaluate_step_no = 6

	for elem in skip_step_li:
		if elem in {2, 3, 4}:
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

	end_time = time.time()

	loading_time = end_time - start_time


	if referral_code:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), referral_code = referral_code, skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A)
		curr_thought_record.save()
	else:
		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, loading_time = loading_time, A_A = A_A)
		curr_thought_record.save()


	thought_record_id = curr_thought_record.thought_record_id

	return render(request, "diy_tool/index_collaborative.html", {'user_id': user_id, 'condition': condition, 'thought_record_id': thought_record_id, 'skip_step_li': skip_step_li, 'remove_negative_feeling': remove_negative_feeling, 'prompt_to_use': prompt_to_use, 'refresh_btn': refresh_btn, 'more_suggestions_btn': more_suggestions_btn, 'descriptive_thought_Q': descriptive_thought_Q, 'situation_step_no': situation_step_no, 'thinking_trap_step_no': thinking_trap_step_no, 'reframe_step_no': reframe_step_no, 'evaluate_step_no': evaluate_step_no, 'total_steps': total_steps, 'A_A': A_A})





def check_random_numbers(request):
	K = 8000
	GROUP_COUNT = {'A': 0, 'B': 0}

	for i in range(K):
		group = np.random.choice(['A', 'B'], p=[0.5, 0.5])
		
		GROUP_COUNT[group] += 1
		
	ratio_a = GROUP_COUNT['A'] / (GROUP_COUNT['A'] + GROUP_COUNT['B'])
	ratio_b = GROUP_COUNT['B'] / (GROUP_COUNT['A'] + GROUP_COUNT['B'])

	ratio = GROUP_COUNT['A'] / GROUP_COUNT['B']

	print(i, ratio_a, ratio_b, ratio)

	return render(request, "diy_tool/check_random_numbers.html", {'ratio_a': ratio_a, 'ratio_b': ratio_b, 'ratio': ratio})


def save_consent(request):
	if request.method == "GET":
		thought_record_id = request.GET.get('thought_record_id', -1)
		user_id = request.GET.get('user_id', -1)

		curr_consent = Consent(thought_record_id=int(thought_record_id), user_id = int(user_id), consent_obtained=1)
		curr_consent.save()

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
								)

		curr_outcome.save()

		print(thought_record_id, 'outcome saved')

		return JsonResponse({'upload': 'successful',}, safe=False)


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

		
		if 'user_id' in request.session:
			user_id = request.session['user_id']
			condition = request.session['condition']

		else:
			try:
				max_user_id = User.objects.all().order_by("-user_id")[0].user_id
			except:
				max_user_id = 0
			user_id = max_user_id + 1
			condition = 0
			curr_user = User(user_id = int(user_id), condition = condition)
			curr_user.save()

			request.session['user_id'] = max_user_id + 1
			request.session['condition'] = condition

		curr_thought_record = ThoughtRecord(user_id = int(user_id), skip_step = skip_step, remove_negative_feeling = remove_negative_feeling, prompt_to_use = prompt_to_use, refresh_btn = refresh_btn, more_suggestions_btn = more_suggestions_btn, descriptive_thought_Q = descriptive_thought_Q, A_A = A_A, multiple_cognitive_distortions = multiple_cognitive_distortions, extra_q = extra_q, emotion_questions = emotion_questions, personalize = personalize, readable = readable, psychoeducation = psychoeducation, ai = ai, include_emotions = include_emotions)
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
				subtext = CATEGORIES_SUBTEXT[elem[0]]
			except:
				try:
					subtext = CATEGORIES_SUBTEXT_LOWERCASE_KEYS[elem[0].lower()]
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
		else:
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
		else:
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

		else:
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