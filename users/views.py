from django.shortcuts import render

# Create your views here.
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse

from django.shortcuts import render, redirect


from study.redcap_sync import redcap_sync

from study.models import Redcap_Entry_Survey, Redcap_Admin

from .models import CustomUser

class SignUp(generic.CreateView):
	form_class = CustomUserCreationForm
	success_url = reverse_lazy('login')
	template_name = 'signup.html'

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		username = username.lower().strip()

		user = authenticate(username=username)
		
		print('user: ', user)
		
		if user:
			if user.is_active:
				login(request, user, backend='users.auth_backend.PasswordlessAuthBackend')
				print("User {} logged in".format(username))
				# print('request.user.is_authenticated: ', request.user.is_authenticated)
				# print('request.session.session_key: ', request.session.session_key)		
				# request.session.modified = True

				# redirect to study/home and add request
				return redirect('/study/home')
			else:
				return HttpResponseRedirect("ACCOUNTS NOT ACTIVE")
		else:
			print("Someone tried to login and failed!")
			print("Username: {}".format(username))
			print('Trying with Redcap...')

			# sync with redcap
			try:
				redcap_sync(last_sync=True)
			except Exception as e:
				print('redcap_sync failed!', e)
				return render(request, 'users/login.html', {'failed': True})

			user = authenticate(username=username)
		
			print('user-try-2: ', user)

			if user:
				if user.is_active:
					# login user
					login(request, user, backend='users.auth_backend.PasswordlessAuthBackend')
					print("User {} logged in".format(username))

					return redirect('/study/home')
				else:
					return HttpResponseRedirect("ACCOUNTS NOT ACTIVE")
			
			else:
				print("Not found in Redcap!")
				print("Username: {}".format(username))
				return render(request, 'users/login.html', {'failed': True})

		return render(request, 'users/login.html', {'failed': True})
	else:
		return render(request, 'users/login.html', {})
