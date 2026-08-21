# models/servico.py

from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="O valor deve ser maior que zero.")]
    )

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
