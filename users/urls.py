from django.urls import path
from .views import SignUp, user_login

app_name = 'users'

urlpatterns = [
	path('signup/', SignUp.as_view(), name='signup'),
	path('login/', user_login, name='login'),
]