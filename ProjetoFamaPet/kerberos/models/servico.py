from django.db import models

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)