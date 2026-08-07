# models/agendamento.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Agendamento(models.Model):

    STATUS_ESCOLHA = [
        ("Pendente", "Pendente"),
        ("Confirmado", "Confirmado"),
        ("Concluido", "Concluido"),
        ("Cancelado", "Cancelado"),
    ]

    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="agendamentos"
    )

    pet = models.ForeignKey(
        "Pet",
        on_delete=models.CASCADE,
        related_name="agendamentos"
    )

    data = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_ESCOLHA,
        default="Pendente"
    )

    servicos = models.ManyToManyField(
        "Servico",
        related_name="agendamentos"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def valorTotal(self):
        # Soma o valor de todos os serviços vinculados
        return sum(servico.valor for servico in self.servicos.all())

    @property
    def listaServicos(self):
        return ", ".join(
            servico.nome for servico in self.servicos.all()
        )

    def __str__(self):
        return f"{self.pet.nome} - {self.data.strftime('%d/%m/%Y %H:%M')} ({self.status})"

    def clean(self):
        super().clean()
        if self.data and self.data < timezone.now():
            raise ValidationError("Não é possível realizar agendamentos para datas no passado.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)