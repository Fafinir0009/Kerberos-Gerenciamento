from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (Endereco, Pet, Agendamento, Servico, Usuario)
from .forms.FormAdminUsuario import AdminUsuarioChangeForm, AdminUsuarioCreationForm


class UsuarioAdmin(UserAdmin):
	form = AdminUsuarioChangeForm
	add_form = AdminUsuarioCreationForm
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Dados pessoais', {'fields': ('nome', 'email', 'telefone', 'endereco')}),
		('Permissões', {
			'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
		}),
		('Acesso recente', {'fields': ('last_login',)}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': (
				'username', 'email', 'nome', 'telefone', 'password1', 'password2',
				'is_active', 'is_staff',
			),
		}),
	)
	list_display = ('username', 'email', 'nome', 'is_staff', 'is_active')
	list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
	search_fields = ('username', 'email', 'nome')
	ordering = ('username',)
	filter_horizontal = ('groups', 'user_permissions')

admin.site.register(Endereco)
admin.site.register(Pet)
admin.site.register(Agendamento)
admin.site.register(Servico)
admin.site.register(Usuario, UsuarioAdmin)