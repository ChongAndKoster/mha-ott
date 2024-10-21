
DISTORTION_DEFINITIONS = {
			"All-or-Nothing Thinking": "Things in life are rarely black and white. There are shades of gray—and all sorts of other colors too! To break free from All-or-Nothing Thinking, focus on what's positive or neutral about the situation. \"Maybe I didn't get an A, but a C is still a passing grade. Now I know that this subject is hard for me, and I may need to spend more time studying.\"", 
			"Overgeneralizing": "We often notice when things go wrong—and forget about the times they went right. Even if things have gone wrong many times in the past, that doesn't mean they will stay that way. Try to recall times when things went well for you. Imagine what it would be like for things to go well next time.",
			"Labeling": "People are complex. None of us have just one thing that defines us. To break free from Labeling, consider all different aspects of a person. \"I may not be the most outgoing person, but I'm a good friend to the people closest to me.\"",
			"Fortune Telling": "No one can predict the future. To break free from Fortune Telling, be curious about what's going to happen next. Focus on what you can control, and let go of what you can't.",
			"Mind Reading": "No one can know what other people are thinking. To break free from Mind Reading, try to imagine other, less negative possibilities. \"She didn't say hello, but maybe she just didn't hear me.\" When possible, try to ask the person what they're thinking, rather than just assuming.",
			"Emotional Reasoning": "Our feelings provide valuable information to us, but they're only part of the picture. To break free from Emotional Reasoning, consider all the information you have.",
			"Should Statements": "To break free from \"should\" statements, think about where your unrealistic expectations came from. Has someone told you that you need to be a certain way? It's a good thing to want to be your \"best self.\" But we all make mistakes along the way. Let your mistakes be an opportunity to learn and grow.",
			"Personalizing": "As humans, we all have a tendency to think that we have more impact on other people than we really do. To break free from personalization, think about all the other things that could be affecting someone's behavior. \"Maybe they're just having a bad day. Maybe they're distracted.\"",
			"Disqualifying the Positive": "To break free of this thinking trap, go out of your way to notice the positive side. For every negative thing you notice, try pointing out three positive things. At first, it may feel forced, but over time you'll find yourself noticing the small things and feeling more grateful.",
			"Magnification": "In magnification, when you evaluate yourself, another person, or a situation., you unreasonably magnify the negative and/or minimize the positive.",
			"Catastrophizing": "Keep in mind that worst-case scenarios are very unlikely. Try to remind yourself of all the more likely, less severe things that could happen. Expecting the worst can even become a self-fulfilling prophecy. It's okay to be prepared, but try to go into situations expecting a positive outcome.",
			"Comparing and Despairing": "It's best not to compare yourself to others at all—but that's easier said than done. Remember that what you see on social media and in public is everyone showing off their best. You don't see their worst—and they probably don't see yours.",
			"Blaming": "Take responsibility for whatever you can—no more, no less. \"It was okay for me to feel angry in that situation. But I didn't have to take it out on everyone else. Next time, I'll try taking a deep breath before I act.\" And remember: Blaming yourself is still Blaming! Try to think less of whose fault it is, and focus instead on what you can do to make things better.",
			"Not Distorted": "The thought doesn't seem distorted.",
			"Negative Feeling or Emotion": "Feeling negative emotions is a normal part of life. Sometimes we get \"stuck\" in those feelings and don't know how to move forward. First, it's important to allow ourselves to feel these emotions and to accept them for what they are. To get un-stuck, it helps to think about what we can control, and what positive things we can be grateful for.",
			"None of These Thinking Traps Seem Right to Me": "That's okay—we'll give you the space to work through your negative thought in whatever way makes sense to you.",
}


CATEGORIES = ["All-or-Nothing Thinking", 
			"Overgeneralizing",
			"Labeling",
			"Fortune Telling",
			"Mind Reading",
			"Emotional Reasoning",
			"Should Statements",
			"Personalizing",
			"Disqualifying the Positive",
			"Catastrophizing",
			"Catastrophizing",
			"Comparing and Despairing",
			"Blaming",
			 "Negative Feeling or Emotion",
			 "Negative Feeling or Emotion",]

CATEGORIES_SHUFFLED = ["All-or-Nothing Thinking", 
			"Overgeneralizing",
			"Labeling",
			"Fortune Telling",
			"Mind Reading",
			"Emotional Reasoning",
			"Should Statements",
			"Personalizing",
			"Disqualifying the Positive",
			"Catastrophizing",
			"Catastrophizing",
			"Comparing and Despairing",
			"Blaming",
			 "Negative Feeling or Emotion",
			 "Negative Feeling or Emotion"]

CATEGORIES_PREFIX = ["All", 
			"Over",
			"Label",
			"Fortune",
			"Mind",
			"Em",
			"Should",
			"Personal",
			"Disqualifying",
			"Catastrophizing",
			"Catastrophizing",
			"Comparing",
			"Blaming",
			 "Not",
			 "Negative"]

CATEGORIES_SUBTEXT = {"All-or-Nothing Thinking": "Thinking in extremes. \"If it isn't perfect, I failed. There's no such thing as 'good enough'.\"", 
			"Overgeneralizing": "Jumping to conclusions based on one experience. \"They didn't text me back. Nobody ever texts me back.\"",
			"Labeling": "Defining a person based on one action or characteristic. \"I said something embarrassing. I'm such a loser.\"",
			"Fortune Telling": "Trying to predict the future. Focusing on one possibility and ignoring other, more likely outcomes.",
			"Mind Reading": "Assuming you know what someone else is thinking. \"She didn't say hello. She must be mad at me.\"",
			"Emotional Reasoning": "Treating your feelings like facts. \"I woke up feeling anxious. I just know something bad is going to happen today.\"",
			"Should Statements": "Setting unrealistic expectations for yourself. \"I shouldn't need to ask for help. I should be independent.\"",
			"Personalizing": "Taking things personally or making them about you. \"He's quiet today. I wonder what I did wrong.\"",
			"Disqualifying the Positive": "When something good happens, you ignore it or think it doesn't count. \"I only won because I got lucky.\"",
			"Catastrophizing": "Focusing on the worst-case scenario. \"My boss asked if I had a few minutes to talk. I'm going to get fired!\"",
			"Magnification": "Judging a situation entirely on the negative parts and not considering the positive parts",
			"Comparing and Despairing": "Comparing your worst to someone else's best.",
			"Blaming": "Giving away your own power to other people. \"It's not my fault I yelled. You made me angry!\"",
			"Negative Feeling or Emotion": "Getting \"stuck\" on a distressing thought, emotion, or belief.",
			"None of These Thinking Traps Seem Right to Me": "That's okay—we'll give you the space to work through your negative thought in whatever way makes sense to you.",
}


CATEGORIES_SUBTEXT_LOWERCASE_KEYS = {}

for k, v in CATEGORIES_SUBTEXT.items():
	CATEGORIES_SUBTEXT_LOWERCASE_KEYS[k.lower()] = v



FLAG_LIST = ['suicide',
				'suicidal',
                'survive',
				'death',
				'dead',
				'die',
				'died',
				'dying',
				'homicide',
				'murder',
				'kill',
				'alive',
				'5150',
				'5250',
				'Shoot',
				'Trigger',
				'Gun',
				'Goodbye',
				'Kamikaze',
				'take my life',
				'take my own life',
				'not wake up',
				'not live anymore',
				'not alive anymore',
				'end my life',
				'end life',
				'poison',
				'pills',
				'drug',
				'ibuprofen',
				'sedative',
				'swallowed',
				'burn',
				'blood',
				'bleeding',
				'bled',
				'comatose',
				'noose',
				'jump',
				'bag around head',
				'belt around neck',
				'cut',
				'self-harm',
				'self harm',
				'harm',
				'pain',
				'suffer',
				'overdose',
				'risk',
				'unalive',
				'kys ',
				'Hang yourself',
				'Hang myself',
				'rape',
				'raping',
				'molest',
				'rapist',
				'raped',
				'pig',
]



THEMES_CATEGORIES = ['Body image', \
			 'Dating & marriage', \
			'Family', \
			'Fear', \
			'Friendship', \
			'Habits', \
			'Health', \
			'Identity', \
			'Loneliness', \
			'Money', \
			'Parenting', \
			'School', \
			'Suicide', \
			'Tasks & achievement', \
			'Trauma', \
			'Work',]

THEMES_CATEGORIES_PREFIX = ['Body',
			 'Dating', \
			'Family', \
			'Fear', \
			'Friendship', \
			'Hab', \
			'Health', \
			'Identity', \
			'L', \
			'Money', \
			'Parent', \
			'School', \
			'Suicide', \
			'Task', \
			'Tra', \
			'Work', ]


THEMES_CATEGORIES_NEW = ['body image', 'dating & marriage', 'family', 'fear', 'friendship', 'habits', 'health', 'hopelessness/depression', 'identity', 'loneliness', 'money', 'parenting', 'school', 'tasks & achievement', 'trauma']


COGNITIVE_DISTORTION_SYSTEM_PROMPT = """Cognitive distortions are biased perspectives we take on ourselves and the world around us. They are irrational thoughts and beliefs that we unknowingly reinforce over time.

Output as many cognitive distortions as possible as a set. More is better. Choose from the following list: 'All-or-Nothing Thinking', 'Overgeneralizing', 'Labeling', 'Fortune Telling', 'Mind Reading', 'Emotional Reasoning', 'Should Statements', 'Personalizing', 'Disqualifying the Positive', 'Catastrophizing', 'Comparing and Despairing', 'Blaming', 'Negative Feeling or Emotion'"""


COGNITIVE_DISTORTION_EXAMPLES = """I'm always late -> {'Overgeneralizing'}
I'm late for the meeting. Everyone will look down upon me -> {'Fortune Telling', 'Mind Reading'}
I'm late for the meeting. This shows what a jerk I am -> {'Labeling'}
I'm late for the meeting. I'll make a fool of myself -> {'Fortune Telling', 'Labeling'}
I'm late for the meeting. I never do anything right -> {'Overgeneralizing'}
My tire is flat. I'm so stupid -> {'Labeling'}
My tire is flat. I should have gotten a new tire last month -> {'Should Statements'}
My tire is flat. I must have gotten a new tire last month -> {'Should Statements'}
Everyone knows how disorganized and selfish I am -> {'Mind Reading'}
I'm completely self-centered and thoughtless -> {'Labeling', 'All-or-Nothing Thinking'}
My roommate asked me to clean the apartment. She probably hates me -> {'Mind Reading'}
A good mother spends time with her kids on some activity every night -> {'Overgeneralizing'}
I'm a total failure -> {'All-or-Nothing Thinking'}
I never do anything right -> {'Overgeneralizing'}
I always do lousy on tests -> {'Overgeneralizing'}
The test makes me nervous, so I won't do well on it -> {'Emotional Reasoning'}
I'll have to skip this section of the book -> {'Fortune Telling'}
They made a terrible mistake by choosing me -> {'Mind Reading'}
My writing is too drab -> {'Catastrophizing'}
They are not interesting -> {'Labeling'}
They are boring -> {'Labeling'}
I know this is bad because I feel bored -> {'Emotional Reasoning'}
This party will be a drag -> {'Fortune Telling'}
I never get what I want -> {'Overgeneralizing'}
I'll forget what I'm supposed to say -> {'Fortune Telling'}
My speech isn't any good -> {'All-or-Nothing Thinking'}
My mind will blank out -> {'Fortune Telling'}
I'll make a fool of myself -> {'Fortune Telling', 'Labeling'}
What did I do to foul things up? -> {'Personalizing'}
I'll never get this done -> {'Fortune Telling', 'Overgeneralizing'}
I should be well by now -> {'Should Statements'}
I must be well by now -> {'Should Statements'}
I'm not getting anywhere -> {'All-or-Nothing Thinking'}
That improvement was a fluke -> {'Disqualifying the Positive'}
I'll never get better -> {'Catastrophizing'}
I just can't control myself -> {'All-or-Nothing Thinking'}
I must look like a balloon -> {'Labeling'}
My dieting and jogging all week have gone down the drain -> {'Disqualifying the Positive'}
I shouldn't have eaten that -> {'Should Statements'}
I mustn't have eaten that -> {'Should Statements'}
I'm going to pig out all weekend -> {'Fortune Telling'}
I'm a bad mother -> {'Labeling'}
The recruiters didn't call me. I haven't got the job, in the past when I was successful, I was called straight away -> {'Overgeneralizing'}
I will end up with no career -> {'Catastrophizing'}
I will end up with no money -> {'Catastrophizing'}
I haven't got the job -> {'Fortune Telling'}
I spent 3 hours but was only able to make 2 slides. I've wasted all that time -> {'Disqualifying the Positive'}
Looks like the customer got scared -> {'Mind Reading'}
I have made the matters worse -> {'Personalizing'}
A stranger looked at your dress. She thought that I look stupid -> {'Mind Reading'}
I should have never worn these jeans -> {'Should Statements'}
I must have never worn these jeans -> {'Should Statements'}
I almost failed in a subject. I have ruined everything -> {'All-or-Nothing Thinking'}
I only got good grades in two subjects. How could I have done so badly? -> {'Disqualifying the Positive'}
I am a failure! -> {'Labeling'}
I made a mistake in my presentation. People are going to think I am stupid -> {'Mind Reading'}
I'm such an idiot -> {'Labeling'}
The meal should have been perfect -> {'Should Statements'}
The meal must have been perfect -> {'Should Statements'}
My friends are not replying to my messages. They obviously don't want to be friends with me -> {'Mind Reading'}
My friends are not talking to me. It must be my fault -> {'Personalizing'}
I posted a joke online but none of my friends reacted. I will lose my friends because of this -> {'Catastrophizing'}
If I am feeling this guilty right now, this must mean that I did something wrong -> {'Emotional Reasoning'}
Maybe people found my joke offensive -> {'Mind Reading'}
I shouldn't have changed my hair -> {'Should Statements'}
Most of them didn't mention my hair -> {'Catastrophizing'}
I am a lousy writer -> {'Labeling'}
I didn't win so I must be completely rubbish -> {'All-or-Nothing Thinking'}
Being a runner up means nothing -> {'Disqualifying the Positive'}
They probably made everyone a runner up to make people feel better -> {'Mind Reading'}
I will never become a successful writer -> {'Fortune Telling'}
I am an awful person -> {'Labeling'}
They think that I am a horrible human being -> {'Mind Reading'}
I have lost my temper like this in the previous job and was called into a disciplinary meeting, I will probably lose my job over this -> {'Overgeneralizing'}
I will probably lose my job over this -> {'Fortune Telling', 'Catastrophizing'}
I feel so anxious maybe I left something turned on in the kitchen -> {'Emotional Reasoning'}
What if something falls on the coffee maker and turns in on -> {'Fortune Telling'}
What if the whole kitchen sets on fire -> {'Catastrophizing'}
My entire house will burn down -> {'Catastrophizing'}
I will be homeless -> {'Catastrophizing'}
The doctor probably just didn't want to let me know -> {'Mind Reading'}
They want to see me so this must be really bad -> {'Disqualifying the Positive'}
The color in their work is so much more vibrant, mine doesn't look this good -> {'Comparing and Despairing'}
I bet people think now that I am a rubbish artist -> {'Mind Reading'}
I shouldn't have posted it -> {'Should Statements'}
Grandma is going to be so angry with me -> {'Fortune Telling', 'Mind Reading'}
She is probably going to kick me out and never invite me over again -> {'Catastrophizing'}
I am such an idiot -> {'Labeling'}
If I couldn't make this relationship work, I will never succeed at finding a lifelong partner -> {'Overgeneralizing'}
I am unlovable -> {'Labeling'}
If she has cheated on me, then every next girl will probably do the same -> {'Overgeneralizing'}
I can't believe I have lost her now -> {'Disqualifying the Positive'}
She will not want to see me again -> {'Fortune Telling', 'Catastrophizing'}
She must think that I am a weirdo -> {'Mind Reading'}
I should have ordered a milder dish -> {'Should Statements'}
I must have ordered a milder dish -> {'Should Statements'}
I'm late again. My boss will be furious with me like he was last week when I was late because I overslept -> {'Overgeneralizing'}
I will lose my job over this -> {'Fortune Telling', 'Catastrophizing'}
My present was much smaller in size than the others -> {'Comparing and Despairing'}
She said she liked it, but she said that to everyone, so she was probably just trying to be nice -> {'Disqualifying the Positive'}
I made this so awkward -> {'Emotional Reasoning'}
I will get murdered! -> {'Catastrophizing'}
My friend had been robbed last month and they broke in through the kitchen -> {'Overgeneralizing'}
Something scary is in the kitchen -> {'Emotional Reasoning'}
I have never done bowling before, so I will definitely be bad at this -> {'All-or-Nothing Thinking'}
Maybe they invited me to make fun of me -> {'Mind Reading'}
Maybe they knew that I would make a fool of myself -> {'Mind Reading'}
Something bad has happened to him -> {'Catastrophizing'}
Maybe he doesn't like me anymore -> {'Mind Reading'}
Maybe doesn't want to be my friend any longer -> {'Mind Reading'}
I should have messaged him earlier -> {'Should Statements'}
I must message him earlier -> {'Should Statements'}
I am such a bad friend -> {'Labeling'}
Her health could decline further -> {'Fortune Telling'}
She could die -> {'Catastrophizing'}
I should have visited her more often -> {'Should Statements'}
She probably thinks I am the worst grandchild ever -> {'Mind Reading'}
I should have spent more time reading reviews before buying -> {'Should Statements'}
I can return it and get a different one, but I have wasted so much time -> {'Disqualifying the Positive'}
My niece's birthday party had twice the amount of people -> {'Comparing and Despairing'}
I bet more people will cancel -> {'Fortune Telling'}
There will be very few people there -> {'Fortune Telling'}
If there aren't many people there, the party simply can't be a success -> {'All-or-Nothing Thinking'}
Because I lost the elections, I'm a zero -> {'All-or-Nothing Thinking'}
I got a B on my exam. I'm a total failure -> {'All-or-Nothing Thinking'}
The birds are always crapping on my window -> {'Overgeneralizing'}
I'm never going to get a date -> {'Overgeneralizing'}
My boss complimented me but they are just being nice -> {'Disqualifying the Positive'}
Getting good marks was a fluke. It doesn't count -> {'Disqualifying the Positive'}
I made a mistake. How terrible -> {'Catastrophizing'}
I'm always a horrible mother -> {'All-or-Nothing Thinking'}
I'm never going to get it together -> {'All-or-Nothing Thinking'}
My neighbor rushed by me and didn't even acknowledge me. I must have done something wrong -> {'Mind Reading'}
I submitted my application, but I already know they won't call me back for an interview. -> {'Fortune Telling'}
Why did I use that word in that email? I'm sure I'm going to get fired -> {'Catastrophizing'}
Yeah I got a raise, but it's not big deal -> {'Disqualifying the Positive'}
I feel like crap, so I'm probably a crappy person -> {'Emotional Reasoning'}
I should really exercise more -> {'Should Statements'}
My brother should have talked to me before he made any decisions about where our family is going -> {'Should Statements'}
I'm so gross -> {'Labeling'}
He's so inconsiderate -> {'Labeling'}
I'm a huge nobody -> {'Labeling'}
They didn't like me, I'm unlovable -> {'All-or-Nothing Thinking'}
Our relationship ended because I was a bad partner -> {'Personalizing'}
Our project is slowed down because they never made a point to contact me. This is all their fault -> {'Blaming'}
We were late to the dinner party and caused the hostess to overcook the meal -> {'Personalizing'}
If I had only pushed my husband to leave on time, this wouldn't have happened -> {'Personalizing'}
Stop making me feel bad about myself -> {'Blaming'}
I shouldn't be so lazy -> {'Should Statements'}
I feel it, therefore it must be true -> {'Emotional Reasoning'}
I'm a loser -> {'Labeling'}
I've blown my diet completely -> {'All-or-Nothing Thinking'}
I feel guilty. I must be a rotten person -> {'Emotional Reasoning'}
I feel hopeless. I must be hopeless -> {'Emotional Reasoning'}
I shouldn't eat that doughnut -> {'Should Statements'}
He shouldn't have been so stubborn -> {'Should Statements'}
I shouldn't have made so many mistakes -> {'Should Statements'}
If only I were better in bed, he wouldn't beat me -> {'Personalizing'}
The reason my marriage is so lousy is because my spouse is totally unreasonable -> {'Blaming'}
I never say the right thing -> {'Overgeneralizing'}
Nothing ever goes my way -> {'All-or-Nothing Thinking', 'Overgeneralizing'}
I felt awkward during my job interview. I am always so awkward -> {'Overgeneralizing'}
My mom is always upset. She would be fine if I did more to help her -> {'Personalizing'}
She probably thinks I'm ugly -> {'Mind Reading'}
I feel like a bad friend, therefore I must be a bad friend -> {'Emotional Reasoning'}
I should always be friendly -> {'Should Statements'}
I never do a good enough job on anything -> {'All-or-Nothing Thinking'}
I made a mistake, therefore I'm a failure -> {'All-or-Nothing Thinking'}
I ate more than I planned, so I blew my diet completely -> {'All-or-Nothing Thinking'}
I will fail and it will be unbearable -> {'Fortune Telling', 'Catastrophizing'}
I passed the exam, but I was just lucky -> {'Disqualifying the Positive'}
Going to college is not a big deal; anyone can do it -> {'Disqualifying the Positive'}
I feel she loves me, so it must be true -> {'Emotional Reasoning'}
I am terrified of planes, so it must be dangerous -> {'Emotional Reasoning'}
I got a B. This proves how inferior I am -> {'Catastrophizing'}
I got an A. It doesn't mean I'm smart -> {'Catastrophizing'}
He's thinking I have failed -> {'Mind Reading'}
She thought I didn't know the project -> {'Mind Reading'}
He knows I do not like to be touched this way -> {'Mind Reading'}
Every time I take a day off from work, it rains -> {'Overgeneralizing'}
You only pay attention to me when I cook food -> {'Overgeneralizing'}
My husband left me because I was a bad wife -> {'Personalizing'}
I should have been a better mother -> {'Should Statements'}
He should have married Ann instead of Mary -> {'Should Statements'}
My parents are the ones to blame for my unhappiness -> {'Blaming'}
It is my fault that my son married a selfish and uncaring person -> {'Personalizing'}
My father always prefers my elder brother -> {'Comparing and Despairing'}
She is more successful than I am -> {'Comparing and Despairing'}
He thinks I'm an idiot -> {'Mind Reading'}
If I talk, I will mess up and not say what I mean -> {'Fortune Telling'}
I will never get into college -> {'Fortune Telling', 'Catastrophizing'}
I'm disgusting -> {'Labeling'}
He's horrible -> {'Labeling'}
She's irrelevant -> {'Labeling'}
That's what I'm supposed to do, so it doesn't count -> {'Disqualifying the Positive'}
Those successes were easy, so they don't matter -> {'Disqualifying the Positive'}
I fail all the time -> {'Overgeneralizing'}
It was a waste of time -> {'All-or-Nothing Thinking'}
I get rejected by everyone -> {'All-or-Nothing Thinking'}
I should do well -> {'Should Statements'}
My relationship ended because I wasn't fun enough -> {'Personalizing'}
It was my fault my group got a bad grade -> {'Personalizing'}
She's to blame for the way I feel -> {'Blaming'}
My parents caused all my problems -> {'Blaming'}
My teacher is the reason I'm not doing well -> {'Blaming'}
I feel anxious, therefore I must be in danger -> {'Emotional Reasoning'}
Others did better than I did on the test -> {'Comparing and Despairing'}
People my age are more successful than I am -> {'Comparing and Despairing'}
I'm unlovable. My friends hang out with me only because they must feel sorry for me -> {'Disqualifying the Positive'}
“I'm a bad person. I only help others because it makes me feel better about myself -> {'Disqualifying the Positive'}
I feel sad, therefore I must be depressed -> {'Emotional Reasoning'}
He thinks I'm a loser -> {'Labeling'}
I'll fail the exam -> {'Fortune Telling'}
I won't get the job -> {'Fortune Telling'}
I'm undesirable -> {'Labeling'}
That's what wives are supposed to do. So it doesn't count when she's nice to me -> {'Disqualifying the Positive'}
I seem to fail at everything -> {'Overgeneralizing'}
The marriage ended because I failed -> {'Personalizing'}
I did that really badly -> {'All-or-Nothing Thinking'}
Everything always goes badly for me -> {'Overgeneralizing'}
Mary doesn't like me at all -> {'Mind Reading'}
I should have completed everything I planned to do -> {'Should Statements'}
I'm pathetic -> {'Labeling'}
That was really a terrible day -> {'Catastrophizing'}
I didn't get all my work done today again. I'll get the sack -> {'Catastrophizing'}
I made a real fool of myself at that party -> {'Labeling', 'Catastrophizing'}
My husband didn't eat that chocolate cake I baked for him. He thinks I'm a terrible cook -> {'Mind Reading'}
That was a terrible mistake; I'll never learn to do this properly -> {'Overgeneralizing'}
I must make a good impression at this party -> {'Should Statements'}
I was so irritable with the children this morning. I'm a terrible mother and a wicked person -> {'Overgeneralizing'}
I can't stand being alone now that Jane has gone -> {'Disqualifying the Positive'}
I must be really stupid to have these distorted thoughts -> {'Personalizing'}
Mary doesn't like me at all. She would never have shouted at me like that if she did -> {'Personalizing'}
I'll never be able to face them again -> {'Fortune Telling', 'Catastrophizing'}
I'll never manage to stand up for myself. I never have -> {'Fortune Telling', 'Catastrophizing'}
If I'm not a total success, I'm a failure -> {'All-or-Nothing Thinking'}
I'll be so upset, I won't be able to function at all -> {'Catastrophizing'}
I did that project well, but that doesn't mean I'm competent; I just got lucky -> '{Disqualifying Positive'}
Getting a mediocre evaluation proves how inadequate I am -> {'Catastrophizing'}
Getting high marks doesn't mean I am smart -> {'Disqualifying the Positive'}
I was so uncomfortable talking to this person. I don't have what it takes to make friends -> {'Overgeneralizing'}
The repairman was curt to me because I did something wrong -> {'Personalizing'}
I should always do my best -> {'Should Statements'}
My son's teacher cannot do anything right -> {'Blaming'}
If I did not have friends, I would be lonely -> {'All-or-Nothing Thinking'}
feeling down -> {'Negative Feeling or Emotion'}
guilt of losing a friend -> {'Negative Feeling or Emotion'}
i'm worried about my chest pain -> {'Negative Feeling or Emotion'}
turning my mind off -> {'Negative Feeling or Emotion'}
my partner left me -> {'Negative Feeling or Emotion'}
afraid of people -> {'Negative Feeling or Emotion'}
ashamed and embarressed -> {'Negative Feeling or Emotion'}
my phyical appearance -> {'Negative Feeling or Emotion'}
school and my future -> {'Negative Feeling or Emotion'}
keeping a good relationship with my son -> {'Negative Feeling or Emotion'}
concentrate on one thing at the time -> {'Negative Feeling or Emotion'}
i don't know -> {'Negative Feeling or Emotion'}
it's too loud in here -> {'Negative Feeling or Emotion'}
possible heart problems -> {'Negative Feeling or Emotion'}
parents are a thing -> {'Negative Feeling or Emotion'}
health concerns, financial insecurity, living independently again -> {'Negative Feeling or Emotion'}
i feel good -> {'Negative Feeling or Emotion'}
i feel bad -> {'Negative Feeling or Emotion'}
i feel angry -> {'Negative Feeling or Emotion'}
i am sad -> {'Negative Feeling or Emotion'}
i am feeling lonely -> {'Negative Feeling or Emotion'}
i'm going to prison -> {'Negative Feeling or Emotion'}
why am i sad? -> {'Negative Feeling or Emotion'}
we don't have money -> {'Negative Feeling or Emotion'}
I am worried about my finances -> {'Negative Feeling or Emotion'}
ptsd and anxiety -> {'Negative Feeling or Emotion'}
my kids getting older -> {'Negative Feeling or Emotion'}
school grades future -> {'Negative Feeling or Emotion'}
missing my new ex-boyfriend so much -> {'Negative Feeling or Emotion'}
missing my ex boyfriend -> {'Negative Feeling or Emotion'}
my mental health -> {'Negative Feeling or Emotion'}
felling like here but not -> {'Negative Feeling or Emotion'}
feeling so flat and unmotivated -> {'Negative Feeling or Emotion'}
depression and relationship issue -> {'Negative Feeling or Emotion'}
guilt and anxiety -> {'Negative Feeling or Emotion'}
my relationship is going downhill -> {'Negative Feeling or Emotion'}
i lost what i used to be proud of -> {'Negative Feeling or Emotion'}
i feel like i'm drowning -> {'Negative Feeling or Emotion'}
my husbands infidelity -> {'Negative Feeling or Emotion'}
relationship problem with wife -> {'Negative Feeling or Emotion'}
feeling like i belong -> {'Negative Feeling or Emotion'}
i don't want to fail my board exam again -> {'Negative Feeling or Emotion'}
looks, weight, social ability -> {'Negative Feeling or Emotion'}
i cant sleep -> {'Negative Feeling or Emotion'}
to get out of my 41 year marriage -> {'Negative Feeling or Emotion'}
how do i start to love myself? -> {'Negative Feeling or Emotion'}
I didn't do very well at dieting -> {'Negative Feeling or Emotion'}
Communication worries -> {'Negative Feeling or Emotion'}
I need to develop myself in that direction -> {'Negative Feeling or Emotion'}
I need to learn more -> {'Negative Feeling or Emotion'}
I need a change of pace -> {'Negative Feeling or Emotion'}
Worry about ability to survive -> {'Negative Feeling or Emotion'}
Lack of monetary income -> {'Negative Feeling or Emotion'}
I am insecure about my relations -> {'Negative Feeling or Emotion'}
I would have to devote myself to bettering that aspect of myself -> {'Negative Feeling or Emotion'}
i got a no for answer -> {'Negative Feeling or Emotion'}
i really wanted to go on a date with that person -> {'Negative Feeling or Emotion'}
I don't want her to leave home -> {'Negative Feeling or Emotion'}
going to fail at my interview -> {'Fortune Telling'}
i'm worried that i won't develop better discipline -> {'Fortune Telling'}
what if we never get engaged -> {'Overgeneralizing'}
i'll never lose enough weight to look skinny -> {'Fortune Telling'}
i'm so weak, helpless and out of control -> {'Labeling'}
i'm going to be lonely forever -> {'Overgeneralizing'}
my parents don't love me and they never will -> {'Overgeneralizing'}
if i can't pass in college, i can't get a good job, or a good life -> {'All-or-Nothing Thinking'}
that i am alone and always will be -> {'Catastrophizing', 'Fortune Telling', 'Overgeneralizing'}
i am unwanted -> {'Labeling'}
not being smart enough -> {'All-or-Nothing Thinking'}
lack of sexual interest from my significant other -> {'Blaming'}
i hate to be told anything -> {'Overgeneralizing'}
what if i stop breathing for no reason? -> {'Catastrophizing'}
what if I die -> {'Catastrophizing'}
I will die -> {'Catastrophizing'}
someday i'll stop trying -> {'Catastrophizing'}
feeling unworthy -> {'Labeling'}
i'm never going to live a normal life -> {'Catastrophizing', 'Fortune Telling', 'Overgeneralizing'}
about my boyfriend if he's cheating on me again -> {'Mind Reading'}
the worthlessness of life -> {'Disqualifying the Positive'}
everyone hates me, including me -> {'Overgeneralizing'}
i should be sleeping -> {'Should Statements'}
afraid something i did will hurt me -> {'Emotional Reasoning', 'Fortune Telling'}
i overthink the worst possibility to happen -> {'Catastrophizing'}
i can't ever relax -> {'Overgeneralizing'}
always going to be lonely -> {'Overgeneralizing'}
i dont have a full purpose -> {'All-or-Nothing Thinking'}
I don't have enough willpower -> {'Overgeneralizing'}
I might lose my job -> {'Catastrophizing'}
I am not a good person in society -> {'All-or-Nothing Thinking', 'Labeling'}
This person is not my boss and is not even providing accurate information! Why are they acting like this? -> {'Mind Reading'}
Because other did better than me -> {'Comparing and Despairing'}
I should have behaved differently -> {'Should Statements'}
I don't think I can get all my work done today -> {'Fortune Telling'}
I could get fired -> {'Catastrophizing'}
She doesn't like the way I look -> {'Mind Reading'}
My girlfriend wasnt texting anyone, and did not get me anniversary present I am scared my girlfriend is going to break up with me because I dont do much for her. -> {'All-or-Nothing Thinking', 'Catastrophizing', 'Catastrophizing'}
I am unable to give my children any time A good mother spends time with her kids on some activity every night -> {'Overgeneralizing'}
Would my death have an impact on people? Like is there anyone on here that's had someone close to them commit suicide and knows what it's like? Would anyone care if I died? -> {'Overgeneralizing'}
Stomach ache every day I might be having a serious illness -> {'Fortune Telling', 'Catastrophizing'}
My son threw a tantrum at an indoor playground and I had to carry him out kicking and screaming I'm a bad mom -> {'Negative Feeling or Emotion', 'Labeling'}
im scared of the human mind i cant trust people -> {'Fortune Telling', 'Emotional Reasoning'}
Being transgender I'm not who I want to be. I hate my appearance and my voice. -> {'Catastrophizing'}
I made very good English presentation but I got nervous because of the amount of people and I forgot my text I'm scared to present in front of other people and I panic -> {'Negative Feeling or Emotion', 'Emotional Reasoning', 'Catastrophizing'}
i still can't speak or understand korean, even after 6 months here i'm not good enough -> {'All-or-Nothing Thinking', 'Overgeneralizing'}
My manager is giving more responsibilities to another co-worker. I deserve more than the other co-worker to get more responsibilities. -> {'Personalizing'}
My husband did something for me even if it's clear I didn't want it. I don't know why I keep trying. I should just give up. Surrender. Sleep forever. -> {'Catastrophizing'}
I get so annoyed and frustrated when my baby cries i am a terrible mom -> {'Negative Feeling or Emotion'}
Breakup after loving truly. I am scared of my future life and being in sorrow of breakup and didn't feel light of overthinking -> {'Emotional Reasoning'}
My wife has left me. I'm going to be alone -> {'Catastrophizing', 'Catastrophizing'}
I applied for a job and just got a call saying I didn't get the job. I am not good enough for anyone. -> {'All-or-Nothing Thinking', 'Overgeneralizing', 'Labeling'}
I'm late for the meeting This shows what a jerk I am -> {'Labeling'}
I had a complaint against my work which I felt unnecessary to bring to my attention as it was very minor. There was no need to even say anything it was very minor. -> {'Negative Feeling or Emotion', 'Catastrophizing'}
I was on a date and started to cough badly as the food was too hot I should have ordered a milder dish -> {'Should Statements'}
My first boyfriend and I broke up 6 years ago My partner will leave me if my depression doesn't go away soon. -> {'Fortune Telling', 'Mind Reading'}
A potential client decided to work with another company I failed our company & myself -> {'Personalizing'}
I had a disagreement about our finances with my partner at our home about a week ago that caused her to leave the apartment and not talk, call, or text me for hours. I worried that she might break up with me and that I'd never see her again. -> {'All-or-Nothing Thinking', 'Fortune Telling', 'Negative Feeling or Emotion', 'Overgeneralizing', 'Catastrophizing', 'Mind Reading'}
I am trying to write up an essay and can't think of anything I'm wasting all my time -> {'All-or-Nothing Thinking'}
I posted a joke online and none of my friends reacted Maybe my friends found the joke offensive, I'll lose some friends because of this -> {'Catastrophizing'}
I have a flight in the evening Something will go wrong on my flight today -> {'Fortune Telling'}
I had a fight with my husband My best friend doesn't fight with my husband this much, so I must be doing something wrong -> {'Comparing and Despairing'}
I do gas stations audits and I messed up and forgot something I was supposed to do I felt like a failure and am ashamed I made this mistake -> {'Negative Feeling or Emotion', 'All-or-Nothing Thinking'}
My diet is not working I feel like a failure -> {'Emotional Reasoning'}
I was unable to visit my Mother in the hospital in another state. I am the worst daughter in the world. -> {'Negative Feeling or Emotion', 'All-or-Nothing Thinking', 'Labeling'}
I'm late for the meeting I never do anything right -> {'Overgeneralizing'}
I ask out a co-worker who I became fond of recently but was turned down. I'm not good enough for her. -> {'Mind Reading', 'Negative Feeling or Emotion', 'Personalizing', 'Emotional Reasoning'}
My relationship of 2 years ended out of nowhere, constantly stressed about my job, i ever feel like be worth it to another person or to my friends unless they need something. I don’t feel like I’m worth it. -> {'All-or-Nothing Thinking', 'Catastrophizing', 'Negative Feeling or Emotion'}
I was on a coffee break and my boss reminded me of work that needs to get done. My boss must think I'm lazy. -> {'Mind Reading', 'Personalizing'}
A neighbor borrowed my smartphone charger and never returned it. he took me for granted! -> {'Catastrophizing', 'Labeling', 'Personalizing'}
My husband could not understand why I was upset with him. I don't understand why he can't see that he overreacted. -> {'Blaming', 'All-or-Nothing Thinking', 'Labeling'}
After I complained about not spending time together, my boyfriend did not want to go on a date last weekend. He doesn't love me. -> {'Overgeneralizing', 'Personalizing'}
I'm hanging out with a friend chit chatting, but realizing he's not putting much effort, like usual, into having good conversation.  He just repeats the same thing ad nauseam. He's a nice guy, but I don't want to be friends with him any more as he's putting no effort into not being completely boring. -> {'Labeling', 'Catastrophizing'}
Time is running short on the workday, my boss asks me if I can finish a task that will require me to stay for a few extra hours. Why would you wait until the last minute to ask me this. -> {'Blaming', 'Catastrophizing'}
I saw my friend comment on an Instagram post when he's been ignoring me. My friend doesn't like me anymore. -> {'Mind Reading', 'Personalizing'}
I missed a personal deadline for a project a friend asked me to help with. I made a deadline and missed it. -> {'Negative Feeling or Emotion'}
My mom cooked me breakfast and the eggs which she knows i like over medium were over cooked. I became very upset. frustration -> {'Catastrophizing', 'Disqualifying the Positive'}
My friend and I had made plans months ago to go to a basketball game. The day before the game he calls me and says he cant go because he forgot he made plans with his wife. I started yelling at him and told him these tickets were expensive and you promised me. I was really angry for cancelling last minute because he has done this in the past I get upset when people cant keep there promises. The plans he made were not that critical. Why put me in a tough bind -> {'Negative Feeling or Emotion', 'Blaming', 'Personalizing'}
My grandma died three years ago and my aunt recently had major surgery. I'm scared of losing loved ones -> {'Negative Feeling or Emotion', 'Catastrophizing'}
I'm afraid of pregnancy and I think i'm not mentally or emotionally prepared I can't be a mother -> {'Fortune Telling', 'Emotional Reasoning'}
My spouse became verbally abusive with me. He might hit me -> {'Negative Feeling or Emotion'}
I saw a profile picture of a close friend on a dating app that I had feelings for. I am not the kind of person that she would like to go out with. -> {'Mind Reading', 'All-or-Nothing Thinking', 'Comparing and Despairing'}
I am trying to diet but I gained weight this week. I don't have the discipline to diet. -> {'All-or-Nothing Thinking', 'Catastrophizing'}"""


COGNITIVE_DISTORTION_PROBABILITIES = """Cognitive distortions are biased perspectives we take on ourselves and the world around us. They are irrational thoughts and beliefs that we unknowingly reinforce over time. For a given thought and associated cognitive distortions, output the probabilities of each cognitive distortion as a dictionary.

Thought: My husband cancelled our wedding anniversary dinner. The thought that he does not care about me anymore.
Cognitive Distortions: {'Mind Reading', 'Catastrophizing', 'Personalizing'}
Probabilities: {'Mind Reading': 0.75, 'Catastrophizing': 0.1, 'Personalizing': 0.3}

Thought: First interview after studying and getting my diploma. I'll screw it over
Cognitive Distortions: {'Fortune Telling', 'Catastrophizing'}
Probabilities: {'Fortune Telling': 0.9, 'Catastrophizing': 0.8}"""