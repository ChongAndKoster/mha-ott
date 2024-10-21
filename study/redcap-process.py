import json


import pandas as pd

col_list = []

EVENT_NAME_TO_COLS = {}

with open('redcap-record.jsonl') as json_file:
	# file has a single list with a list of jsons

	json_list = json.load(json_file)

	for json_obj in json_list:

		# get all cols
		for k in json_obj.keys():
			if k not in col_list:
				col_list.append(k)

		if json_obj['redcap_event_name'] not in EVENT_NAME_TO_COLS:
			EVENT_NAME_TO_COLS[json_obj['redcap_event_name']] = []

		for k in json_obj.keys():
			if k not in EVENT_NAME_TO_COLS[json_obj['redcap_event_name']]:
				EVENT_NAME_TO_COLS[json_obj['redcap_event_name']].append(k)

		# add to df
		# if json_obj['redcap_event_name'] == 'baseline_arm_1':
		# only take cols from json_obj
		# json_obj = {k: json_obj[k] for k in cols}
		
print(col_list)

# check if cols are same for all events

# event_names = list(EVENT_NAME_TO_COLS.keys())

# for i in range(len(event_names)):
# 	for j in range(i+1, len(event_names)):
# 		if EVENT_NAME_TO_COLS[event_names[i]] != EVENT_NAME_TO_COLS[event_names[j]]:
# 			print('event_names[i]: ', event_names[i])
# 			print('event_names[j]: ', event_names[j])
# 			print('EVENT_NAME_TO_COLS[event_names[i]]: ', EVENT_NAME_TO_COLS[event_names[i]])
# 			print('EVENT_NAME_TO_COLS[event_names[j]]: ', EVENT_NAME_TO_COLS[event_names[j]])
# 			print('')	


# df.to_csv('redcap-records.csv', index=False)