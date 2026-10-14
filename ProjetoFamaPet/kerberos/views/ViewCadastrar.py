from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages

from ..forms.FormUsuario import UsuarioForm
from ..forms.FormEndereco import EnderecoForm 
from ..forms.FormPet import PetForm


@transaction.atomic
def cadastrar_usuario(request):
    if request.method == 'POST':
        form_usuario = UsuarioForm(request.POST)
        form_endereco = EnderecoForm(request.POST)
        form_pet = PetForm(request.POST)

        if form_usuario.is_valid() and form_endereco.is_valid() and form_pet.is_valid():
            usuario = form_usuario.save(commit=False)
            usuario.save()

            endereco = form_endereco.save(commit=False)
            endereco.usuario = usuario
            endereco.save()

            pet = form_pet.save(commit=False)
            pet.usuario = usuario
            pet.save()

            messages.success(request, 'Cadastro completo realizado com sucesso! Faça seu login.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija os erros apontados nos formulários abaixo.')
    else:
        form_usuario = UsuarioForm()
        form_endereco = EnderecoForm()
        form_pet = PetForm()

    contexto = {
        'form_usuario': form_usuario,
        'form_endereco': form_endereco,
        'form_pet': form_pet,
    }
    return render(request, 'cadastro/cadastro.html', contexto)
