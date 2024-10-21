from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
	add_form = CustomUserCreationForm
	# form = CustomUserChangeForm
	model = CustomUser
	list_display = ('username', 'is_staff', 'is_active', 'is_new_user',)
	list_filter = ('username', 'is_staff', 'is_active', 'is_new_user',)
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Permissions', {'fields': ('is_staff', 'is_active')}),
		('Annotation', {'fields': ('is_new_user',)}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active', 'is_new_user',)}
		),
	)
	search_fields = ('username',)
	ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
