from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

	class Meta(UserCreationForm):
		model = CustomUser
		fields = ('username', )


# class CustomUserChangeForm(UserChangeForm):

# 	class Meta:
# 		model = User # CustomUser
# 		fields = ('username', 'is_new_user')
# 		# fields = ('username',)
	