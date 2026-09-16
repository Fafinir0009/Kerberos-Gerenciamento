from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from ..forms.FormAgendamento import AgendamentoForm
from ..models import Usuario, Pet, Agendamento

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