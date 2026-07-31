from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)

    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    def __str__(self):
        return self.nome

    def CriarUsuario(self):
        return Usuario(nome, email, telefone, endereco)

