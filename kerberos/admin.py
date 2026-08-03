from django.contrib import admin
from .models import (Endereco, Pet, Agendamento, Servico, Usuario)

admin.site.register(Endereco)
admin.site.register(Pet)
admin.site.register(Agendamento)
admin.site.register(Servico)
admin.site.register(Usuario)