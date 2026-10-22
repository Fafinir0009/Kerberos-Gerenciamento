from django import forms
from django.db.models import Q
from django.utils import timezone
from kerberos.models.agendamento import Agendamento
from kerberos.models.pet import Pet
from kerberos.models.servico import Servico


class AgendamentoForm(forms.ModelForm):
    data = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="Data e Horário"
    )

    servicos = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        label="Serviços Desejados"
    )

    class Meta:
        model = Agendamento
        fields = ["pet", "data"]

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

        agora = timezone.localtime()
        if not self.instance.pk or not self.instance.data or self.instance.data >= agora:
            self.fields['data'].widget.attrs['min'] = agora.strftime('%Y-%m-%dT%H:%M')

        if usuario and getattr(usuario, "is_authenticated", False):
            if usuario.is_staff:
                self.fields["pet"].queryset = Pet.objects.all().select_related("usuario")
                self.fields["pet"].label_from_instance = (
                    lambda obj: f"{obj.nome} (Tutor: {obj.usuario.nome})"
                )
            else:
                self.fields["pet"].queryset = Pet.objects.filter(usuario=usuario)
        else:
            self.fields["pet"].queryset = Pet.objects.none()

        if self.instance and self.instance.pk:
            servicos_existentes = list(
                item.servico_id for item in self.instance.itens.all()
            )
            self.fields["servicos"].queryset = Servico.objects.filter(
                Q(ativo=True) | Q(pk__in=servicos_existentes)
            )
            self.fields["servicos"].initial = servicos_existentes

    def clean_pet(self):
        pet = self.cleaned_data.get("pet")
        # Apenas valida se o pet pertence ao usuário caso NÃO seja admin
        if self.usuario and not self.usuario.is_staff and pet and pet.usuario != self.usuario:
            raise forms.ValidationError("O pet selecionado não pertence à sua conta.")
        return pet

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if not data or data >= timezone.now():
            return data

        if self.instance.pk and self.instance.data:
            data_existente = self.instance.data.replace(second=0, microsecond=0)
            data_enviada = data.replace(second=0, microsecond=0)
            if data_enviada == data_existente:
                return data

        raise forms.ValidationError('Escolha uma data e horário futuros.')