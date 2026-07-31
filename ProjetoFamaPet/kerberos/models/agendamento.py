from django.db import models

class Agendamento(models.Model):

    STATUS_ESCOLHA = [
    ("Pendente", "Pendente"),
    ("Confirmado", "Confirmado"),
    ("Concluido", "Concluido"),
    ("Cancelado", "Cancelado"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="agendamentos"
    )

    pet = models.ForeignKey(
        Pet,
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
        Servico,
        related_name="agendamentos"
    )

    @property
    def valorTotal(self):
        return sum(servico.valor for servico in self.servicos.all())

    def __str__(self):
        return f"{self.pet.nome} - {self.data.strftime('%d/%m/%Y %H:%M')}"

    def criarAgendamento(self):
        return Agendamento(usuario, pet, data, status, servico)

