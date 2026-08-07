from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home'),
    path('clientes/', views.listar_clientes , name='clientes'),
    path('pets/', views.listar_pets , name='pets'),
    path('relatorio/', views.relatorio , name='relatorio'),
    path('agendamentos/', views.agendamentos , name='agendamentos'),
]