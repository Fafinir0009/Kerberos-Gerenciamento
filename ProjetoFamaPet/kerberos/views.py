from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from .models import Usuario, Pet, Agendamento

def home(request):
    return render(request, 'home/index.html')

def listar_clientes(request):
    usuarios = Usuario.objects.all()
    contexto = {'usuarios': usuarios}
    return render(request, 'usuario/clientes.html', contexto)

def listar_pets(request):
    pets = Pet.objects.all()
    contexto = {'pets': pets}
    return render(request, 'pet/pets.html', contexto)

def relatorio(request):
    relatorio = Agendamento.objects.prefetch_related('servicos').select_related('usuario', 'pet')
    faturamento = sum(relatorio.valorTotal for relatorio in relatorio)
    contexto = {"relatorio": relatorio,'faturamento': faturamento,}
    return render(request, 'relatorio/relatorio.html', contexto)

def agendamentos(request):
    data_str = request.GET.get('data')
    
    if data_str:
        data_selecionada = datetime.strptime(data_str, '%Y-%m-%d').date()
    else:
        data_selecionada = timezone.now().date()

    agendamentos = (
        Agendamento.objects
        .prefetch_related('servicos')
        .select_related('usuario', 'pet')
        .filter(data__date=data_selecionada)
    )
    
    contexto = {
        'agendamentos': agendamentos,
        'data_selecionada': data_selecionada,
        'agendamentos_manha': agendamentos.filter(data__time__gte='09:00', data__time__lt='12:00'),
        'agendamentos_tarde': agendamentos.filter(data__time__gte='13:00', data__time__lt='18:00'),
        'agendamentos_noite': agendamentos.filter(data__time__gte='19:00', data__time__lte='21:00'),
    }
    
    return render(request, 'agendamento/agendamentos.html', contexto)

def politica_privacidade(request):
    return render(request, 'politica/politica-privacidade.html')

def politica_transporte(request):
    return render(request, 'politica/politica-transporte.html')

def politica_regulamento(request):
    return render(request, 'politica/regulamento.html')





















































