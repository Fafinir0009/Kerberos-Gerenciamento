from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from kerberos.forms.FormUsuario import UsuarioForm


@login_required
def perfil(request):
    usuario = request.user

    form_usuario = UsuarioForm(instance=usuario)
    form_senha = PasswordChangeForm(user=usuario)

    if request.method == 'POST':
        if 'btn_atualizar_dados' in request.POST:
            form_usuario = UsuarioForm(request.POST, instance=usuario)
            if form_usuario.is_valid():
                form_usuario.save()
                messages.success(request, 'Dados pessoais atualizados com sucesso!')
                return redirect('perfil')
            else:
                messages.error(request, 'Por favor, corrija os erros nos dados pessoais.')

        elif 'btn_alterar_senha' in request.POST:
            form_senha = PasswordChangeForm(user=usuario, data=request.POST)
            if form_senha.is_valid():
                user = form_senha.save()
                # Impede que a sessão caia após alterar a senha
                update_session_auth_hash(request, user)
                messages.success(request, 'Sua senha foi alterada com sucesso!')
                return redirect('perfil')
            else:
                messages.error(request, 'Erro ao alterar a senha. Verifique os requisitos.')

    return render(request, 'perfil/perfil.html', {
        'form_usuario': form_usuario,
        'form_senha': form_senha,
    })