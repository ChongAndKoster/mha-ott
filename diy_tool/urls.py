from django.urls import path
# from .views import SignUp
from .views import RCT, RCT_AI, RCT_no_AI, old_index, index, index_no_AI, index_save, index_no_AI, index_demo, index_multiple_select, index_old_outcomes, index_collaborative, cognitive_distortion_request, \
					check_random_numbers, \
					rational_response_request_single, \
					rational_response_request_matched, \
					rational_response_request_attributes, \
					rational_response_request_1, \
					rational_response_request_2, \
					rational_response_request_3, \
					rational_response_request_theme_1, \
					rational_response_request_theme_2, \
					rational_response_request_theme_new_1, \
					rational_response_request_theme_new_2, \
					rational_response_request_theme_new_3, \
					rational_response_request_theme_gpt4_1, \
					rational_response_request_theme_gpt4_2, \
					rational_response_request_theme_gpt4_3, \
					get_theme, \
					combine_reframed_thoughts_single, \
					combine_reframed_thoughts, \
					combine_reframed_thoughts_new, \
					save_consent, \
					save_steps_logs, \
					save_next_check_error, \
					save_refresh_btn, \
					save_thought, \
					save_emotion, \
					save_situation, \
					save_thinking_trap_selected, \
					save_reframe_selected, \
					save_reframe_final, \
					save_outcome_questions, \
					save_demographics, \
					save_start_over, \
					save_flag_inappropriate, \
					save_load_more, \
					save_url_clicks, \
                    save_feedback, \
                    get_more_help_1, \
					get_more_help_2, \
					combine_reframe_thoughts_more_help
					

app_name = 'diy_tool'

urlpatterns = [
	path('RCT.html', RCT, name='RCT'),
	path('RCT_AI', RCT_AI, name='RCT_AI'),
	path('RCT_no_AI', RCT_no_AI, name='RCT_no_AI'),
	path('index.html', index, name='diy_tool_index'),
	path('index_no_AI.html', index_no_AI, name='diy_tool_index_no_AI'),
	path('index_save.html', index_save, name='diy_tool_index_save'),
	path('index_no_AI.html', index_no_AI, name='index_no_AI'),
	path('old_index.html', old_index, name='new_index'),
    path('index_demo.html', index_demo, name='index_demo'),
    path('index_multiple_select.html', index_multiple_select, name='index_multiple_select'),
    path('index_old_outcomes.html', index_old_outcomes, name='index_old_outcomes'),
    path('index_collaborative.html', index_collaborative, name='index_collaborative'),
	path('cognitive_distortion_request.html', cognitive_distortion_request, name='cognitive_distortion_request'),
	path('check_random_numbers.html', check_random_numbers, name='check_random_numbers'),
	path('rational_response_request_single.html', rational_response_request_single, name='rational_response_request_single'),
	path('rational_response_request_matched.html', rational_response_request_matched, name='rational_response_request_matched'),
	path('rational_response_request_attributes.html', rational_response_request_attributes, name='rational_response_request_attributes'),
	path('rational_response_request_1.html', rational_response_request_1, name='rational_response_request_1'),
	path('rational_response_request_2.html', rational_response_request_2, name='rational_response_request_2'),
	path('rational_response_request_3.html', rational_response_request_3, name='rational_response_request_3'),
	path('rational_response_request_theme_1.html', rational_response_request_theme_1, name='rational_response_request_theme_1'),
	path('rational_response_request_theme_2.html', rational_response_request_theme_2, name='rational_response_request_theme_2'),
	path('rational_response_request_theme_new_1.html', rational_response_request_theme_new_1, name='rational_response_request_theme_new_1'),
    path('rational_response_request_theme_new_2.html', rational_response_request_theme_new_2, name='rational_response_request_theme_new_2'),
	path('rational_response_request_theme_new_3.html', rational_response_request_theme_new_3, name='rational_response_request_theme_new_3'),
	path('rational_response_request_theme_gpt4_1.html', rational_response_request_theme_gpt4_1, name='rational_response_request_theme_gpt4_1'),
	path('rational_response_request_theme_gpt4_2.html', rational_response_request_theme_gpt4_2, name='rational_response_request_theme_gpt4_2'),
	path('rational_response_request_theme_gpt4_3.html', rational_response_request_theme_gpt4_3, name='rational_response_request_theme_gpt4_3'),
	path('get_theme.html', get_theme, name='get_theme'),
	path('combine_reframed_thoughts_single.html', combine_reframed_thoughts_single, name='combine_reframed_thoughts_single'),
	path('combine_reframed_thoughts.html', combine_reframed_thoughts, name='combine_reframed_thoughts'),
	path('combine_reframed_thoughts_new.html', combine_reframed_thoughts_new, name='combine_reframed_thoughts_new'),
	path('save_consent.html', save_consent, name='save_consent'),
	path('save_steps_logs.html', save_steps_logs, name='save_steps_logs'),
	path('save_next_check_error.html', save_next_check_error, name='save_next_check_error'),
	path('save_refresh_btn.html', save_refresh_btn, name='save_refresh_btn'),
	path('save_thought.html', save_thought, name='save_thought'),
	path('save_emotion.html', save_emotion, name='save_emotion'),
	path('save_situation.html', save_situation, name='save_situation'),
	path('save_thinking_trap_selected.html', save_thinking_trap_selected, name='save_thinking_trap_selected'),
	path('save_reframe_selected.html', save_reframe_selected, name='save_reframe_selected'),
	path('save_reframe_final.html', save_reframe_final, name='save_reframe_final'),
	path('save_outcome_questions.html', save_outcome_questions, name='save_outcome_questions'),
	path('save_demographics.html', save_demographics, name='save_demographics'),
	path('save_start_over.html', save_start_over, name='save_start_over'),
	path('save_flag_inappropriate.html', save_flag_inappropriate, name='save_flag_inappropriate'),
	path('save_load_more.html', save_load_more, name='save_load_more'),
	path('save_url_clicks.html', save_url_clicks, name='save_url_clicks'),
	path('save_feedback.html', save_feedback, name='save_feedback'),
	path('get_more_help_1.html', get_more_help_1, name='get_more_help_1'),
	path('get_more_help_2.html', get_more_help_2, name='get_more_help_2'),
	path('combine_reframe_thoughts_more_help.html', combine_reframe_thoughts_more_help, name='combine_reframe_thoughts_more_help'),
	# path('index.html', index_examples, name='index_examples'),
]