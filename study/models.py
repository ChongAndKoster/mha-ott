from django.db import models

# Create your models here.

class BaseModel(models.Model):

	class Meta:
		abstract = True
		app_label = 'study'

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class UserDetails(BaseModel):
	username = models.TextField(default='')
	study_id = models.TextField(default='')
	n8m95 = models.TextField(default='')
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


class ToolUseAssignments(BaseModel):
	tool_use_id = models.AutoField(primary_key=True)

	username = models.TextField(default='')
	week_no = models.IntegerField()
	usage_no = models.IntegerField(default=0)

	tool_use_num = models.IntegerField(default=0)

	date_start = models.DateTimeField(null=True)
	date_expire = models.DateTimeField(null=True)

	status = models.TextField(default='')

	type_use = models.TextField(default='') 


class ThoughtRecord(BaseModel):
	thought_record_id = models.AutoField(primary_key=True)
	username = models.TextField(default='')

	referral_code = models.TextField(default='')

	week_no = models.IntegerField(default=0)
	
	skip_step = models.TextField(default='')
	remove_negative_feeling = models.IntegerField(default=0)
	prompt_to_use = models.TextField(default='')
	refresh_btn = models.IntegerField(default=0)
	more_suggestions_btn = models.IntegerField(default=0)
	descriptive_thought_Q = models.IntegerField(default=0, null=True)
	loading_time = models.FloatField(default=0, null=True)
	A_A = models.IntegerField(default=0, null=True)
	multiple_cognitive_distortions = models.IntegerField(default=0, null=True)
	extra_q = models.IntegerField(default=0, null=True)
	emotion_questions = models.TextField(default='', null=True)
	personalize = models.IntegerField(default=0, null=True)
	readable = models.IntegerField(default=0, null=True)
	psychoeducation = models.IntegerField(default=0, null=True)
	ai = models.IntegerField(default=0, null=True)
	include_emotions = models.IntegerField(default=0, null=True)



class Thought(BaseModel):
	thought_id = models.AutoField(primary_key=True)
	thought_record_id = models.IntegerField()
	thought = models.TextField(default='')

class Emotion(BaseModel):
	emotion_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	thought_id = models.IntegerField(default=0)

	belief = models.TextField(default='')
	emotion = models.TextField(default='')
	emotion_strength = models.TextField(default='')


class Situation(BaseModel):
	situation_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	thought_id = models.IntegerField(default=0)
	
	situation = models.TextField(default='')


class Thinking_Trap_Generated(BaseModel):
	thinking_trap_generated_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	situation_id = models.IntegerField(default=0)
	
	thinking_trap_generated_cat = models.TextField(default='')
	thinking_trap_generated_other_cat = models.TextField(default='')
	thinking_trap_generated_perc = models.TextField(default='')


class Thinking_Trap_Selected(BaseModel):
	thinking_trap_selected_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	thinking_trap_generated_id = models.IntegerField(default=0)
	
	thinking_trap_selected =  models.TextField(default='')


class Reframes_Generated(BaseModel):
	reframes_generated_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	thinking_trap_selected_id = models.IntegerField(default=0)

	reframe_generated = models.TextField(default='')
	reframe_generated_prompt_type = models.TextField(default='')

class Reframes_More_Help(BaseModel):
	reframes_more_help_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	original_reframe = models.TextField(default='')

	reframe_generated = models.TextField(default='')
	reframe_generated_prompt_type = models.TextField(default='')
	more_context = models.TextField(default='')


class Reframe_Selected(BaseModel):
	reframe_selected_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	reframes_generated_id = models.IntegerField(default=0)

	reframe_selected = models.TextField(default='')


class Reframe_Final(BaseModel):
	reframe_final_id = models.AutoField(primary_key=True)

	thought_record_id = models.IntegerField()
	reframe_selected_id = models.IntegerField(default=0)

	reframe_final = models.TextField(default='')


class Consent(BaseModel):
	thought_record_id = models.IntegerField()
	user_id = models.IntegerField()
	consent_obtained = models.IntegerField(default=0)
	

class Outcome(BaseModel):
	thought_record_id = models.IntegerField()
	reframe_final_id = models.IntegerField()

	believable = models.TextField(default='')
	stickiness = models.TextField(default='')
	helpfulness = models.TextField(default='')
	learnability = models.TextField(default='')

	belief_1 = models.TextField(default='')
	emotion_strength_1 = models.TextField(default='')
	belief_2 = models.TextField(default='')
	emotion_strength_2 = models.TextField(default='')

	comments = models.TextField(default='')


class Step_Logs(BaseModel):
	thought_record_id = models.IntegerField()
	step_number_from = models.IntegerField(default=-1)
	step_number_to = models.IntegerField()

class Next_Check_Error(BaseModel):
	thought_record_id = models.IntegerField()
	step_number_from = models.IntegerField(default=-1)
	error_type = models.TextField(default='')

class Start_Over(BaseModel):
	old_thought_record_id = models.IntegerField()
	new_thought_record_id = models.IntegerField()
	step_number_from = models.IntegerField()

class Show_More_Thinking_Traps(BaseModel):
	thought_record_id = models.IntegerField()
	num_thinking_trap_shown = models.IntegerField()

class Flag_Inappropriate(BaseModel):
	thought_record_id = models.IntegerField()
	reframe = models.TextField(default='')

	delete_label = models.IntegerField(default=0)
	reason = models.TextField(default='')

class Safety_Filter(BaseModel):
	thought_record_id = models.IntegerField()
	text = models.TextField(default='')
	type = models.TextField(default='')

class Demographics(BaseModel):
	thought_record_id = models.IntegerField()
	reframe_final_id = models.IntegerField()

	age_range = models.TextField(default='')
	gender = models.TextField(default='')
	race = models.TextField(default='')
	income = models.TextField(default='')
	education = models.TextField(default='')
	population = models.TextField(default='')
	problems = models.TextField(default='')
	treatment = models.TextField(default='')
	prior_experience = models.TextField(default='')


class OpenAI_Error(BaseModel):
	thought_record_id = models.IntegerField()
	input = models.TextField(default='')
	response_no = models.TextField(default='')


class URL_Clicks(BaseModel):
	thought_record_id = models.IntegerField()
	url_text = models.TextField(default='')

class Refresh_Btn(BaseModel):
	thought_record_id = models.IntegerField()

class Feedback(BaseModel):
	thought_record_id = models.IntegerField()
	feedback = models.TextField(default='')


class Redcap_Last_Sync(BaseModel):
	pass

class Redcap_Welcome_Landing_Page(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	welcome_landing_page_complete = models.TextField(default='')

class Redcap_Week_No(BaseModel):
	study_id = models.TextField()

	w1 = models.TextField(default='')
	w2 = models.TextField(default='')
	w3 = models.TextField(default='')
	w4 = models.TextField(default='')
	w5 = models.TextField(default='')
	w8 = models.TextField(default='')


class Redcap_Payments(BaseModel):
	study_id = models.TextField()
	
	w1_paid = models.TextField(default='')
	w1_amt = models.TextField(default='')
	pay_date_w1 = models.TextField(default='')

	w2_paid = models.TextField(default='')
	w2_amt = models.TextField(default='')
	pay_date_w2 = models.TextField(default='')

	w3_paid = models.TextField(default='')
	w3_amt = models.TextField(default='')
	pay_date_w3 = models.TextField(default='')

	w4_paid = models.TextField(default='')
	w4_amt = models.TextField(default='')
	pay_date_w4 = models.TextField(default='')

	w5_paid = models.TextField(default='')
	w5_amt = models.TextField(default='')
	pay_date_w5 = models.TextField(default='')

	w8_paid = models.TextField(default='')
	w8_amt = models.TextField(default='')
	pay_date_w8 = models.TextField(default='')

class Redcap_Admin(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	trigger_consent = models.TextField(default='')
	condition = models.TextField(default='')
	start_date = models.TextField(default='')
	stop_1 = models.TextField(default='')
	test = models.TextField(default='')
	admin_complete = models.TextField(default='')

class Redcap_Events_Log(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	comms_log = models.TextField(default='')
	withdraw = models.TextField(default='')
	date_withdraw = models.TextField(default='')
	notes_withdraw = models.TextField(default='')
	events_log_complete = models.TextField(default='')

class Redcap_Consent(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	consent_yn = models.TextField(default='')
	consent_complete = models.TextField(default='')

class Redcap_Psychoed(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	psychoed_complete = models.TextField(default='')

class Redcap_Entry_Survey(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	age = models.TextField(default='')
	us_res = models.TextField(default='')
	first_name = models.TextField(default='')
	last_name = models.TextField(default='')
	email = models.TextField(default='')
	contact_pref = models.TextField(default='')
	phone = models.TextField(default='')
	entry_survey_complete = models.TextField(default='')

class Redcap_PHQ9(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	phq_1 = models.TextField(default='')
	phq_2 = models.TextField(default='')
	phq_3 = models.TextField(default='')
	phq_4 = models.TextField(default='')
	phq_5 = models.TextField(default='')
	phq_6 = models.TextField(default='')
	phq_7 = models.TextField(default='')
	phq_8 = models.TextField(default='')
	phq_9 = models.TextField(default='')
	phq_calc_1 = models.TextField(default='')
	phq_calc_2 = models.TextField(default='')
	phq_calc_3 = models.TextField(default='')
	phq_calc_4 = models.TextField(default='')
	phq_calc_5 = models.TextField(default='')
	phq_calc_6 = models.TextField(default='')
	phq_calc_7 = models.TextField(default='')
	phq_calc_8 = models.TextField(default='')
	phq_calc_9 = models.TextField(default='')
	phq_answered = models.TextField(default='')
	phq_total = models.TextField(default='')
	phq_difficult = models.TextField(default='')
	phq9_complete = models.TextField(default='')

class Redcap_GAD7(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	gad7_q1 = models.TextField(default='')
	gad7_q2 = models.TextField(default='')
	gad7_q3 = models.TextField(default='')
	gad7_q4 = models.TextField(default='')
	gad7_q5 = models.TextField(default='')
	gad7_q6 = models.TextField(default='')
	gad7_q7 = models.TextField(default='')
	gad7_total = models.TextField(default='')
	gad7_q8 = models.TextField(default='')
	gad7_complete = models.TextField(default='')

class Redcap_CR_Use(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	cr_use_q = models.TextField(default='')
	cr_use_complete = models.TextField(default='')

class Redcap_Hope(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	hope_q = models.TextField(default='')
	hope_complete = models.TextField(default='')

class Redcap_EM(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	em_1 = models.TextField(default='')
	em_2 = models.TextField(default='')
	em_3 = models.TextField(default='')
	em_4 = models.TextField(default='')
	em_5 = models.TextField(default='')
	em_6 = models.TextField(default='')
	em_complete = models.TextField(default='')

class Redcap_CCTS(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	ccts_20 = models.TextField(default='')
	ccts_28 = models.TextField(default='')
	ccts_21 = models.TextField(default='')
	ccts_06 = models.TextField(default='')
	ccts_24 = models.TextField(default='')
	ccts_11 = models.TextField(default='')
	ccts_elab = models.TextField(default='')
	ccts_wellbeing = models.TextField(default='')
	ccts_other = models.TextField(default='')
	ccts_complete = models.TextField(default='')

class Redcap_Exit(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	impact_diy = models.TextField(default='')
	use_diy = models.TextField(default='')
	impact_y_diy = models.TextField(default='')
	impact_n_diy = models.TextField(default='')
	apply_diy = models.TextField(default='')
	apply_y_diy = models.TextField(default='')
	benefit_diy = models.TextField(default='')
	benefit_y_diy = models.TextField(default='')
	takeaways_diy = models.TextField(default='')
	future_diy = models.TextField(default='')
	change_diy = models.TextField(default='')
	like_diy = models.TextField(default='')
	dislike_diy = models.TextField(default='')
	exit_complete = models.TextField(default='')

class Redcap_MiscQ(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	ther_yn = models.TextField(default='')
	mhmeds_yn = models.TextField(default='')
	therapy_post_diy = models.TextField(default='')
	therapy = models.TextField(default='')
	talk = models.TextField(default='')
	seekmh = models.TextField(default='')
	practice_cr = models.TextField(default='')
	excite_mhskill = models.TextField(default='')
	life_impact = models.TextField(default='')
	miscq_complete = models.TextField(default='')

class Redcap_Post_Diy(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	post_1 = models.TextField(default='')
	post_2 = models.TextField(default='')
	post_3 = models.TextField(default='')
	post_4 = models.TextField(default='')
	post_5 = models.TextField(default='')
	post_6 = models.TextField(default='')
	post_7 = models.TextField(default='')
	post_diy_complete = models.TextField(default='')

class Redcap_Tool_Use(BaseModel):
	study_id = models.TextField()
	n8m95 = models.TextField()
	redcap_event_name = models.TextField() 

	tool_1 = models.TextField(default='')
	tool_2 = models.TextField(default='')
	tool_3 = models.TextField(default='')
	tool_4 = models.TextField(default='')
	tool_5 = models.TextField(default='')
	tool_use_complete = models.TextField(default='')


class Psychoeducation(BaseModel):
	username = models.TextField(default='')


class Homepage(BaseModel):
	username = models.TextField(default='')