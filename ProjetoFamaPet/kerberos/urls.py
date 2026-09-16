from django.urls import path
from . import views
from .views.ViewPet import (listar_pets, criar_pet, editar_pet, deletar_pet)
from .views.ViewUsuario import (listar_clientes, criar_cliente, editar_cliente, deletar_cliente)
from .views.ViewPoliticas import (politica_privacidade, politica_regulamento, politica_transporte)
from .views.ViewRelatorio import (relatorio)
from .views.ViewAgendamento import (agendamentos)
from .views.ViewPerfil import (perfil)

urlpatterns = [
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/novo/', criar_cliente, name='criar_cliente'),
    path('clientes/<int:pk>/editar/', editar_cliente, name='editar_cliente'),
    path('clientes/<int:pk>/deletar/', deletar_cliente, name='deletar_cliente'),

    path('perfil/', perfil , name='perfil'),

    path('pets/', listar_pets, name='listar_pets'),
    path('pets/novo/', criar_pet, name='criar_pet'),
    path('pets/<int:pk>/editar/', editar_pet, name='editar_pet'),
    path('pets/<int:pk>/deletar/', deletar_pet, name='deletar_pet'),

    path('relatorio/', relatorio , name='relatorio'),

    path('agendamentos/', agendamentos , name='agendamentos'),

    path('politica-privacidade/', politica_privacidade , name='politica-privacidade'),
    path('politica-transporte/', politica_transporte , name='politica-transporte'),
    path('politica-regulamento/', politica_regulamento , name='politica-regulamento'),
]