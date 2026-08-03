from django.urls import path
from . import views

urlpatterns = [

    path('kerberos/', views.home , name='home'),
    path('kerberos/', views.listar_usuarios , name='listar_usuarios'),
]