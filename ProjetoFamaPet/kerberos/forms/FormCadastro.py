from django import forms
from django.db import transaction
from ..models import Usuario


class CadastroForm(forms.Form):
    nome = forms.CharField(max_length=100)
    email = forms.EmailField()
    telefone = forms.CharField(max_length=20)
    senha = forms.CharField(widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("senha") != cleaned.get("confirmar_senha"):
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned

    def save(self):
        with transaction.atomic():
            usuario = Usuario.objects.create_user(
                username=self.cleaned_data["email"],
                email=self.cleaned_data["email"],
                nome=self.cleaned_data["nome"],
                password=self.cleaned_data["senha"],
                telefone=self.cleaned_data["telefone"],
            )
        return usuario