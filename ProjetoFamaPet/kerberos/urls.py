from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home , name='home'),
    path('/', views.listar_usuarios , name='listar_usuarios'),
]