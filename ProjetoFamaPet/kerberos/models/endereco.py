from django.db import models

class Endereco(models.Model):
    rua = models.CharField(max_length=100)
    numero = models.IntegerField()
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.rua}, {self.numero}"

    def criarEndereco(self):
        return Endereco(rua, numero, bairro, cep)