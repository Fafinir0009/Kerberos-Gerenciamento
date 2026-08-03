from django.urls import path
from . import views

urlpatterns = [
    path('', views.home , name='home'),
    path('', views.listar_usuarios , name='listar_usuarios'),
]