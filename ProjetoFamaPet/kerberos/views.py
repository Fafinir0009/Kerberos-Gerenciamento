from django.shortcuts import render
from .models import Usuario, Pet

def home(request):
    return render(request, 'home/index.html')


def listar_clientes(request):
    usuarios = Usuario.objects.all()
    contexto = {'usuarios': usuarios}
    return render(request, 'usuario/clientes.html', contexto)