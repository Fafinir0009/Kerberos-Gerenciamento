# models/pet.py

from django.db import models
from django.core.validators import MaxValueValidator


class Pet(models.Model):

    PORTE_ESCOLHA = [
        ("Pequeno", "Pequeno"),
        ("Medio", "Medio"),
        ("Grande", "Grande"),
    ]

    ESPECIE_ESCOLHA = [
        ("Cachorro", "Cachorro"),
        ("Gato", "Gato"),
    ]

    nome = models.CharField(max_length=100)
    idade = models.PositiveIntegerField(
        validators=[MaxValueValidator(40, message="Idade informada parece inválida.")]
    )
    especie = models.CharField(max_length=20, choices=ESPECIE_ESCOLHA)
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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
