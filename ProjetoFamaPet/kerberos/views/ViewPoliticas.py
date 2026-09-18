from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def politica_privacidade(request):
    return render(request, 'politica/politica-privacidade.html')

def politica_transporte(request):
    return render(request, 'politica/politica-transporte.html')

def politica_regulamento(request):
    return render(request, 'politica/regulamento.html')