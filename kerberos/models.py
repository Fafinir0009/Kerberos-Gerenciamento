from django.db import models

class Endereco(models.Model):
    rua = models.CharField(max_length=100)
    numero = models.IntegerField()
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.rua}, {self.numero}"

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
    observacao = models.TextField(blank=True)

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="pets"
    )

    def __str__(self):
        return self.nome

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome


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
    def valor_total(self):
        return sum(servico.valor for servico in self.servicos.all())

    def __str__(self):
        return f"{self.pet.nome} - {self.data.strftime('%d/%m/%Y %H:%M')}"
