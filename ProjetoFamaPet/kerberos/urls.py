from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home'),
    path('clientes/', views.listar_clientes , name='listar_clientes'),
]