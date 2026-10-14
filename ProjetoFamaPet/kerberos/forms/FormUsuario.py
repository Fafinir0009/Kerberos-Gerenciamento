from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import Usuario
from .mixins import NomeValidationMixin


class UsuarioForm(NomeValidationMixin, forms.ModelForm):

    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Crie uma senha segura",
            "autocomplete": "new-password",
            "class": "form-control",
        }),
    )
    confirmar_senha = forms.CharField(
        label="Confirme a Senha",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Repita a senha",
            "autocomplete": "new-password",
            "class": "form-control",
        }),
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']
        error_messages = {
            'email': {
                'unique': "Já existe um usuário cadastrado com este e-mail.",
            },
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Nome completo',
                'autocomplete': 'name',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'seuemail@exemplo.com',
                'autocomplete': 'email',
                'class': 'form-control',
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(11) 91234-5678',
                'autocomplete': 'tel',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['senha'].required = False
            self.fields['confirmar_senha'].required = False

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        if senha:
            try:
                validate_password(senha, self.instance)
            except DjangoValidationError as error:
                raise forms.ValidationError(error.messages) from error
        return senha

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            return email.strip().lower()
        return email

    def clean_telefone(self):
        telefone = (self.cleaned_data.get('telefone') or '').strip()
        if not telefone:
            return ''

        numeros = "".join(filter(str.isdigit, telefone))

        if len(numeros) not in (10, 11):
            raise forms.ValidationError(
                "Informe um telefone válido com DDD (10 ou 11 dígitos)."
            )

        if len(numeros) == 11:
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) == 10:
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

        return telefone

    def clean(self):
        """Valida se as duas senhas informadas batem."""
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if (senha or confirmar_senha) and senha != confirmar_senha:
            self.add_error("confirmar_senha", "As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        """Preenche o username com o e-mail, aplica a criptografia e salva."""
        usuario = super().save(commit=False)
        
        email_limpo = self.cleaned_data.get("email")
        usuario.username = email_limpo
        
        senha = self.cleaned_data.get('senha')
        if senha:
            usuario.set_password(senha)
        elif not usuario.pk:
            usuario.set_unusable_password()
        usuario.is_staff = False  # Garante perfil de Cliente por padrão
        
        if commit:
            usuario.save()
        return usuario