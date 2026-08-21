# models/endereco.py

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator


class Endereco(models.Model):

    cep_validator = RegexValidator(
        regex=r'^\d{5}-?\d{3}$',
        message="CEP inválido. Use o formato 00000-000."
    )

    rua = models.CharField(max_length=100)
    numero = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="O número deve ser maior que zero.")]
    )
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=9, validators=[cep_validator])

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.rua}, {self.numero}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
