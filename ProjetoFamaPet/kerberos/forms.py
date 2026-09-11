from datetime import date
from django import forms
from . import models

# Validar os nomes
class NomeValidationMixin:
    def clean_nome(self):
        nome = self.cleaned_data.get("nome", "").strip()
        if len(nome) < 3:
            raise forms.ValidationError(
                "O nome deve ter pelo menos 3 caracteres."
            )
        return nome

# Usuario
class UsuarioForm(NomeValidationMixin, forms.ModelForm):
    class Meta:
        model = models.Usuario
        fields = ['nome', 'email', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Nome completo',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'seuemail@exemplo.com',
                'autocomplete': 'email',
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(11) 91234-5678',
                'autocomplete': 'tel',
            }),
        }
        error_messages = {
            'email': {
                'unique': "Já existe um usuário cadastrado com este e-mail.",
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if models.Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(
                "Já existe um usuário cadastrado com este e-mail."
            )
        return email

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '').strip()
        numeros = "".join(filter(str.isdigit, telefone))

        if len(numeros) not in (10, 11):
            raise forms.ValidationError(
            "Informe um telefone válido com DDD."
        )
        return telefone

# Pet
class PetForm(NomeValidationMixin, forms.ModelForm):
    class Meta:
        model = models.Pet
        fields = ['nome', 'data_de_nascimento', 'raca', 'porte', 'observacao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Nome do pet',
                'autocomplete': 'name',
            }),

            'data_de_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'max': date.today().isoformat(),
            }),

            'raca': forms.TextInput(attrs={
                'placeholder': 'Raça do pet',
            }),

            'porte': forms.Select(),

            'observacao': forms.Textarea(attrs={
                'placeholder': 'Observações sobre o pet',
                'rows': 4,
            }),
        }
    
    def clean_data_de_nascimento(self):
        data_de_nascimento = self.cleaned_data.get("data_de_nascimento")
        if data_de_nascimento and data_de_nascimento > date.today():
            raise forms.ValidationError(
                "A data de nascimento não pode ser no futuro."
            )
        return data_de_nascimento 

# Endereço
class EnderecoForm(forms.ModelForm):
    class Meta:
        model = models.Endereco
        fields = ['rua', 'numero', 'bairro', 'cep']
        widgets = {
            'rua': forms.TextInput(attrs={
                'placeholder': 'Rua/Avenida',
                'autocomplete': 'street-address',
            }),
            'numero': forms.NumberInput(attrs={
                'placeholder': 'Número',
                'min': 1,
            }),
            'bairro': forms.TextInput(attrs={
                'placeholder': 'Bairro',
                'autocomplete': 'address-level2',
            }),
            'cep': forms.TextInput(attrs={
                'placeholder': '00000-000',
                'maxlength': 9,
                'autocomplete': 'postal-code',
            }),
        }

    def clean_cep(self):
        cep = "".join(filter(str.isdigit, self.cleaned_data["cep"]))

        if len(cep) != 8:
            raise forms.ValidationError("O CEP deve conter 8 dígitos.")
        return f"{cep[:5]}-{cep[5:]}"

    def clean_numero(self):
        numero = self.cleaned_data.get("numero")

        if numero is not None and numero <= 0:
            raise forms.ValidationError(
                "O número deve ser maior que zero."
            )
        return numero

class ServicoForm(NomeValidationMixin, forms.ModelForm):
    class Meta:
        model = models.Servico
        fields = ['nome', 'descricao', 'valor']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Nome do Serviço',
            }),
            'descricao': forms.Textarea(attrs={
                'placeholder': 'Descrição do Produto',
                'rows': 3,
            }),
            'valor': forms.NumberInput(attrs={
                'placeholder': 'Valor do Serviço',
                'step': '0.01',
                'min': '0',
            }),
        }
    
    def clean_valor(self):
        valor = self.cleaned_data.get("valor")

        if valor is None or valor <= 0:
            raise forms.ValidationError(
                "O valor deve ser maior que zero."
            )
        return valor

class AgendamentoForm(forms.ModelForm):
    data = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = models.Agendamento
        fields = ["pet", "data", "servicos"]
        widgets = {
            "servicos": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario:
            self.fields["pet"].queryset = models.Pet.objects.filter(usuario=usuario)