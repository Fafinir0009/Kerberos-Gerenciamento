from datetime import date

from django.test import TestCase
from django.urls import reverse

from kerberos.forms.FormPet import PetForm
from kerberos.models.pet import Pet
from kerberos.models.usuario import Usuario


class PetAuthorizationTests(TestCase):
    def setUp(self):
        self.cliente_a = Usuario.objects.create_user(
            username='cliente_a@email.com',
            email='cliente_a@email.com',
            nome='Cliente A',
            password='Senha@123',
        )
        self.cliente_b = Usuario.objects.create_user(
            username='cliente_b@email.com',
            email='cliente_b@email.com',
            nome='Cliente B',
            password='Senha@123',
        )
        self.pet_a = Pet.objects.create(
            nome='Rex',
            data_de_nascimento=date(2021, 1, 15),
            raca='Vira-lata',
            porte='Pequeno',
            observacao='Pet do cliente A',
            usuario=self.cliente_a,
        )
        self.pet_b = Pet.objects.create(
            nome='Luna',
            data_de_nascimento=date(2020, 5, 20),
            raca='Poodle',
            porte='Médio',
            observacao='Pet do cliente B',
            usuario=self.cliente_b,
        )

    def test_cliente_somente_ve_seus_pets(self):
        self.client.force_login(self.cliente_a)
        response = self.client.get(reverse('listar_pets'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pet_a.nome)
        self.assertNotContains(response, self.pet_b.nome)

    def test_form_pet_associa_usuario_logado(self):
        data = {
            'nome': 'Bidu',
            'data_de_nascimento': '2022-07-10',
            'raca': 'Shih Tzu',
            'porte': 'Pequeno',
            'observacao': 'Pet do cliente A',
        }
        form = PetForm(data=data, user=self.cliente_a)

        self.assertTrue(form.is_valid(), form.errors)
        pet = form.save()
        self.assertEqual(pet.usuario, self.cliente_a)
