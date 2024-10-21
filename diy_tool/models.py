from django.db import models

# Create your models here.

class BaseModel(models.Model):

	class Meta:
		abstract = True
		app_label = 'diy_tool'

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class User(BaseModel):
	user_id = models.IntegerField()
	ip_address = models.TextField(default='')
	condition  = models.IntegerField(default=0)


class ThoughtRecord(BaseModel):
	thought_record_id = models.AutoField(primary_key=True)
	referral_code = models.TextField(default='')
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
	user_id = models.IntegerField()


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