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


def get_theme(situation, thought):
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
		curr_theme = curr_response_theme['choices'][0]['text'].replace('\n', ' ').strip()
		curr_theme_category = extract_category_theme(curr_theme)
		curr_distr = extract_category_distribution_theme(curr_response_theme)
		curr_distr_sorted = sorted(curr_distr.items(), key = lambda x: x[1], reverse=True)
		curr_theme = curr_distr_sorted[0][0]
	except:
		curr_theme = 'Tasks & achievement'
		curr_theme_category = 'Tasks & achievement'
		curr_distr = {}
	
	return curr_theme



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

			return curr_response_reframing_final
		except:
			return ''



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
			return curr_response_reframing_final
		except:
			return ''
		

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

			return curr_response_reframing_final
		except:
			return ''
		

def rational_response_request_theme_new_1_gpt4(situation, thought, cognitive_distortion_category, curr_theme):

	# print('Running 1...')

	random_top_p = 1

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
					openai.api_version = "2023-06-01-preview"
					openai.api_type = "azure"
					deployment = "Reframing_GPT4"
					gpt3_model = deployment

					curr_response_reframing = openai.ChatCompletion.create(
						deployment_id=deployment,
						model='gpt-4',
						messages=[{'role': 'user', 'content': curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:'},],
						max_tokens=128,
						top_p=top_p,
						stop=['\n'],
						request_timeout=20.0,
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
						messages=[{'role': 'user', 'content': curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:'},],
						max_tokens=128,
						top_p=top_p,
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
			curr_response_reframing_str = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()

			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				pass
			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			return curr_response_reframing_final
		except:
			return ''



def rational_response_request_theme_new_2_gpt4(situation, thought, cognitive_distortion_category, curr_theme):

	# print('Running 2...')

	random_top_p = 1

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
					openai.api_version = "2023-06-01-preview"
					openai.api_type = "azure"
					deployment = "Reframing_GPT4"
					gpt3_model = deployment

					curr_response_reframing = openai.ChatCompletion.create(
						deployment_id=deployment,
						model='gpt-4',
						messages=[{'role': 'user', 'content': curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:'},],
						max_tokens=128,
						top_p=top_p,
						stop=['\n'],
						request_timeout=20.0,
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
						messages=[{'role': 'user', 'content': curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:'},],
						max_tokens=128,
						top_p=top_p,
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
			curr_response_reframing_str = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()

			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				pass
			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			return curr_response_reframing_final
		except:
			return ''



def rational_response_request_theme_new_3_gpt4(situation, thought, cognitive_distortion_category, curr_theme):

	# print('Running 3...')

	random_top_p = 1

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
					openai.api_version = "2023-06-01-preview"
					openai.api_type = "azure"
					deployment = "Reframing_GPT4"
					gpt3_model = deployment

					curr_response_reframing = openai.ChatCompletion.create(
						deployment_id=deployment,
						model='gpt-4',
						messages=[{'role': 'user', 'content': curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:'},],
						max_tokens=128,
						top_p=top_p,
						stop=['\n'],
						request_timeout=20.0,
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
						messages=[{'role': 'user', 'content': curr_reframing_prompt + "\n\n" + prompt_input + '\nRational Response:'},],
						max_tokens=128,
						top_p=top_p,
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
			curr_response_reframing_str = curr_response_reframing['choices'][0]['message']['content'].replace('\n', ' ').strip()

			curr_response_reframing_final = ''

			curr_safety_filter_reframing = safety_filter(curr_response_reframing_str)

			if curr_safety_filter_reframing:
				pass
			else:
				if curr_response_reframing_str != "":
					curr_response_reframing_final = curr_response_reframing_str

			return curr_response_reframing_final
		except:
			return ''



import pandas as pd

df = pd.read_csv('/projects/bdata/talklife/dssg/ashish/Dataset/Cognitive-Distortions/changing_thoughts_tool/changing-thoughts-records-Aug-12.csv')

print(len(df))

# filter believable == -2 and helpfulness = -2
df = df[(df['believable'] == -2) & (df['helpfulness'] == -2)]

print(len(df))

output_li = []

for ii in tqdm(range(50)):

	thought_record_id = df.sample(1)['thought_record_id'].values[0]

	thought = df[df['thought_record_id'] == thought_record_id]['thought'].values[0]
	situation = df[df['thought_record_id'] == thought_record_id]['situation'].values[0]
	cognitive_distortion_category = df[df['thought_record_id'] == thought_record_id]['thinking_trap_selected'].values[0]

	curr_theme = get_theme(situation, thought)

	print('curr_theme:', curr_theme)

	gpt3_1 = rational_response_request_theme_new_1(situation, thought, cognitive_distortion_category, curr_theme)
	gpt3_2 = rational_response_request_theme_new_2(situation, thought, cognitive_distortion_category, curr_theme)
	gpt3_3 = rational_response_request_theme_new_3(situation, thought, cognitive_distortion_category, curr_theme)

	gpt4_1 = rational_response_request_theme_new_1_gpt4(situation, thought, cognitive_distortion_category, curr_theme)
	gpt4_2 = rational_response_request_theme_new_2_gpt4(situation, thought, cognitive_distortion_category, curr_theme)
	gpt4_3 = rational_response_request_theme_new_3_gpt4(situation, thought, cognitive_distortion_category, curr_theme)

	gpt3_reframes = ';'.join([gpt3_1, gpt3_2, gpt3_3])
	gpt4_reframes = ';'.join([gpt4_1, gpt4_2, gpt4_3])

	output_li.append([thought_record_id, situation, thought, cognitive_distortion_category, curr_theme, gpt3_reframes, gpt4_reframes])


output_df = pd.DataFrame(output_li, columns=['thought_record_id', 'situation', 'thought', 'cognitive_distortion_category', 'curr_theme', 'gpt3_reframes', 'gpt4_reframes'])

output_df.to_csv('/projects/bdata/talklife/dssg/ashish/Dataset/Cognitive-Distortions/changing_thoughts_tool/changing-thoughts-records-Aug-12-sample-gpt4.csv', index=False)


