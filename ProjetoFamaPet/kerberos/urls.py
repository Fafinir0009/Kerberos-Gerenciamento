from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home'),
    path('clientes/', views.listar_clientes , name='clientes'),
    path('pets/', views.listar_pets , name='pets'),
    path('relatorio/', views.relatorio , name='relatorio'),
    path('agendamentos/', views.agendamentos , name='agendamentos'),
    path('politica-privacidade/', views.politica_privacidade , name='politica-privacidade'),
    path('politica-transporte/', views.politica_transporte , name='politica-transporte'),
    path('politica-regulamento/', views.politica_regulamento , name='politica-regulamento'),
    path('vacina/', views.vacina , name='vacina'),
]