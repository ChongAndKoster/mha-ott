import os
import openai
import random
import time
import numpy as np
from random import shuffle
from tqdm import tqdm

from definitions import *
from prompts import *
from themes_prompt import *
from themes_prompt_new import *


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


def get_theme(situation, thought, curr_theme):
	print('Running get_theme...')

	MAX_RETRIES = 1

	current_tries = 1

	theme_pred_prompt = thought.strip() + ' ' + situation.strip()

	# if theme_pred_prompt == "":
	# 	theme_pred_prompt = thought.strip()

	while current_tries <= MAX_RETRIES:
		try:				
			openai.api_base = "https://reframing.openai.azure.com"
			openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
			openai.api_version = "2022-12-01"
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

			current_tries += 1
			break
		except Exception as e:
			print('error-theme-2-pred: ', str(e))
			print('theme retrying')
			time.sleep(1)
			current_tries += 1

	# print(curr_response_cd)
	try:
		curr_theme[0] = curr_response_theme['choices'][0]['text'].replace('\n', ' ').strip()
		curr_theme_category = extract_category_theme(curr_theme[0])
		curr_distr = extract_category_distribution_theme(curr_response_theme)
		curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)
		curr_theme[0] = curr_distr_sorted[0][0]
	except:
		curr_theme[0] = 'Tasks & achievement'
		curr_theme_category = 'Tasks & achievement'
		curr_distr = {}



def rational_response_request_theme_new_1(situation, thought, cognitive_distortion_category, curr_theme):

	# print('Running 1...')

	random_top_p = random.randint(0, 1)

	prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

	# Get Theme
	


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


		else:
			curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
			curr_prompt_str = 'THEME_PROMPT_1'

		# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


		MAX_RETRIES = 3

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
					openai.api_base = "https://reframing.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2022-12-01"
					openai.api_type = "azure"
					deployment = "Reframing_Davinci"
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
					request_timeout=20.0,
				)
				current_tries += 1
				break
			except Exception as e:
				print('error-theme-new: ', str(e))
				print('response theme retrying')
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)

		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()


			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				pass
			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			print(curr_response_reframing_final)
			
			return
		except:
			return



def rational_response_request_theme_new_2(situation, thought, cognitive_distortion_category, curr_theme):

	# print('Running 2...')

	random_top_p = random.randint(0, 1)

	prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

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


		else:
			curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
			curr_prompt_str = 'THEME_PROMPT_1'

		# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


		MAX_RETRIES = 3

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
					openai.api_base = "https://reframing.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2022-12-01"
					openai.api_type = "azure"
					deployment = "Reframing_Davinci"
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
					request_timeout=20.0,
				)
				current_tries += 1
				break
			except Exception as e:
				print('error-theme-new: ', str(e))
				print('response theme retrying')
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)

		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()


			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				pass
			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str
			print(curr_response_reframing_final)
			return
		except:
			return
		

def rational_response_request_theme_new_3(situation, thought, cognitive_distortion_category, curr_theme):

	# print('Running 3...')
	random_top_p = random.randint(0, 1)

	prompt_input = 'Situation: ' + situation.strip() + '\nDistorted Thought: ' + thought.strip()

	time.sleep(1)



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


		else:
			curr_reframing_prompt = 'Write a rational response to the following distorted thoughts:\n\n' + '\n\n'.join(curr_prompt_example_li)
			curr_prompt_str = 'THEME_PROMPT_1'

		# print('curr_reframing_prompt:', curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:')


		MAX_RETRIES = 3

		current_tries = 1

		while current_tries <= MAX_RETRIES:
			try:
				if current_tries <= 1 and curr_theme.strip().lower() != 'suicide':
					openai.api_base = "https://reframing.openai.azure.com"
					openai.api_key = os.getenv("OPENAI_API_KEY_AZURE")
					openai.api_version = "2022-12-01"
					openai.api_type = "azure"
					deployment = "Reframing_Davinci"
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
					request_timeout=20.0,
				)
				current_tries += 1
				break
			except Exception as e:
				print('error-theme-new: ', str(e))
				print('response theme retrying')
				current_tries += 1
				if current_tries > MAX_RETRIES:
					break
				time.sleep(5)

		try:
			curr_response_reframing_str = curr_response_reframing['choices'][0]['text'].replace('\n', ' ').strip()


			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				pass
			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			print(curr_response_reframing_final)
			return
		except:
			return
		

import pandas as pd
import threading

# df = pd.read_csv('/projects/bdata/talklife/dssg/ashish/Dataset/Cognitive-Distortions/changing_thoughts_tool/changing_thoughts_till_outcome_Feb_3.csv')

# # start_time,end_time,thought_record_id,thought,situation,thinking_trap_generated_initial,thinking_trap_generated_initial_perc,thinking_trap_generated_others,thinking_trap_selected,reframes_generated,reframe_selected_or_added,reframe_final,believable,stickiness,helpfulness,learnability,thinking_traps_addressed_final,positivity_final,actionability_final,specificity_final,readability_final,empathy_final


# # get situation, thought, thinking_trap_selected

# all_li = []

# for idx, row in df.iterrows():
# 	curr_dict = {}
# 	curr_dict['situation'] = row['situation']
# 	curr_dict['thought'] = row['thought']
# 	curr_dict['cognitive_distortion_category'] = row['thinking_trap_selected']
# 	all_li.append(curr_dict)

# time_taken = []

# # iterate for 50 turns
# for idx in tqdm(range(50)):
# 	# sample a dict from all_li
# 	curr_dict = random.choice(all_li)

# 	situation = curr_dict['situation']
# 	thought = curr_dict['thought']
# 	cognitive_distortion_category = curr_dict['cognitive_distortion_category']

# 	# call rational_response_request_theme_new_1, rational_response_request_theme_new_2, and rational_response_request_theme_new_3 in parallel as threads
# 	# wait for all threads to finish


# 	# time the call
# 	start_time = time.time()

# 	curr_theme = ['',]

# 	t0 = threading.Thread(target=get_theme, args=(situation, thought, curr_theme))
# 	t0.start()

# 	# get t0's output
# 	t0.join()

# 	print('curr_theme:', curr_theme)


# 	t1 = threading.Thread(target=rational_response_request_theme_new_1, args=(situation, thought, cognitive_distortion_category, curr_theme[0]))
# 	t2 = threading.Thread(target=rational_response_request_theme_new_2, args=(situation, thought, cognitive_distortion_category, curr_theme[0]))
# 	t3 = threading.Thread(target=rational_response_request_theme_new_3, args=(situation, thought, cognitive_distortion_category, curr_theme[0]))

# 	t1.start()
# 	t2.start()
# 	t3.start()

# 	t1.join()
# 	t2.join()
# 	t3.join()

# 	# time the call
# 	end_time = time.time()

# 	print('Time taken:', end_time - start_time)

# 	time_taken.append(end_time - start_time)

# 	# sleep for 15 seconds
# 	time.sleep(15)

# print('Average time taken:', np.mean(time_taken), np.std(time_taken))

df = pd.read_csv('/projects/bdata/talklife/dssg/ashish/Dataset/Cognitive-Distortions/changing_thoughts_tool/changing-thoughts-records-Aug-12.csv')

thought_record_id = 10173

thought = df[df['thought_record_id'] == thought_record_id]['thought'].values[0]
situation = df[df['thought_record_id'] == thought_record_id]['situation'].values[0]
cognitive_distortion_category = df[df['thought_record_id'] == thought_record_id]['thinking_trap_selected'].values[0]

curr_theme = ['',]

get_theme(situation, thought, curr_theme)

print('curr_theme:', curr_theme)

rational_response_request_theme_new_1(situation, thought, cognitive_distortion_category, curr_theme[0])
rational_response_request_theme_new_2(situation, thought, cognitive_distortion_category, curr_theme[0])
rational_response_request_theme_new_3(situation, thought, cognitive_distortion_category, curr_theme[0])
