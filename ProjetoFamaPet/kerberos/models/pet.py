from django.db import models

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
    idade = models.PositiveIntegerField()
    especie = models.CharField(max_length=20, choices=ESPECIE_ESCOLHA)
    raca = models.CharField(max_length=50)
    porte = models.CharField(max_length=20, choices=PORTE_ESCOLHA)
    observacao = models.TextField(blank=True, null=True)

    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="pets"
    )

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)