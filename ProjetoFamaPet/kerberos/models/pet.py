# models/pet.py

from django.db import models
from django.core.validators import MaxValueValidator


class Pet(models.Model):

    PORTE_ESCOLHA = [
        ("Pequeno", "Pequeno"),
        ("Medio", "Medio"),
        ("Grande", "Grande"),
    ]

    nome = models.CharField(max_length=100)
    data_de_nascimento = models.DateField(("Data de nascimento do pet"), auto_now=False, auto_now_add=False)
    raca = models.CharField(max_length=50)
    porte = models.CharField(max_length=20, choices=PORTE_ESCOLHA)
    observacao = models.TextField(blank=True, null=True)

    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="pets"
    )

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.usuario.nome})"

    def clean(self):
        super().clean()
        if self.nome:
            self.nome = self.nome.strip()
        if self.data_de_nascimento and self.data_de_nascimento > date.today():
            raise ValidationError("A data de nascimento não pode ser maior que a data de hoje.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
