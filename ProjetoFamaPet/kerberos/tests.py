from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from kerberos.forms.FormAdminUsuario import AdminUsuarioCreationForm
from kerberos.forms.FormPet import PetForm
from kerberos.forms.FormUsuario import UsuarioForm
from kerberos.models.agendamento import Agendamento, ItemAgendamento
from kerberos.models.pet import Pet
from kerberos.models.servico import Servico
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

    def test_confirmacao_de_exclusao_nao_interpola_nome_em_javascript(self):
        self.pet_a.nome = "Rex'); alert(1);//"
        self.pet_a.save()
        self.client.force_login(self.cliente_a)

        response = self.client.get(reverse('listar_pets'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'onsubmit=')
        self.assertContains(
            response,
            'data-confirm-message="Tem certeza que deseja remover este pet?"',
        )


class UsuarioFormPasswordTests(TestCase):
    def setUp(self):
        self.data = {
            'nome': 'Cliente de Teste',
            'email': 'cliente@example.com',
            'telefone': '(11) 91234-5678',
            'senha': 'L0ng-Unique-Password!2026',
            'confirmar_senha': 'L0ng-Unique-Password!2026',
        }

    def test_cadastro_rejeita_senha_fraca(self):
        self.data['senha'] = '12345678'
        self.data['confirmar_senha'] = '12345678'
        form = UsuarioForm(data=self.data)

        self.assertFalse(form.is_valid())
        self.assertIn('senha', form.errors)

    def test_cadastro_armazenha_senha_com_hash(self):
        form = UsuarioForm(data=self.data)

        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()

        self.assertTrue(usuario.check_password(self.data['senha']))
        self.assertNotEqual(usuario.password, self.data['senha'])

    def test_edicao_sem_senha_preserva_credencial(self):
        usuario = Usuario.objects.create_user(
            username='cliente@example.com',
            email='cliente@example.com',
            nome='Cliente de Teste',
            password='Existing-Strong-Password!2026',
        )
        data = {
            'nome': 'Cliente Atualizado',
            'email': 'cliente@example.com',
            'telefone': '(11) 91234-5678',
            'senha': '',
            'confirmar_senha': '',
        }
        form = UsuarioForm(data=data, instance=usuario)

        self.assertTrue(form.is_valid(), form.errors)
        usuario_atualizado = form.save()

        self.assertTrue(
            usuario_atualizado.check_password('Existing-Strong-Password!2026')
        )

    def test_telefone_opcional_aceita_vazio(self):
        data = self.data.copy()
        data['telefone'] = ''
        form = UsuarioForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)


class UsuarioLoginTests(TestCase):
    def test_usuario_pode_entrar_com_email_quando_username_e_diferente(self):
        usuario = Usuario.objects.create_user(
            username='nome-interno',
            email='cliente-login@example.com',
            nome='Cliente Login',
            password='Strong-Login-Password!2026',
        )

        response = self.client.post(
            reverse('login'),
            {
                'username': usuario.email,
                'password': 'Strong-Login-Password!2026',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            int(self.client.session['_auth_user_id']),
            usuario.pk,
        )

    def test_admin_cria_usuario_com_senha_hasheada(self):
        senha = 'Strong-Admin-Password!2026'
        form = AdminUsuarioCreationForm(data={
            'username': 'usuario-criado-admin',
            'email': 'admin-created@example.com',
            'nome': 'Usuário Criado',
            'telefone': '',
            'password1': senha,
            'password2': senha,
            'is_active': True,
            'is_staff': False,
        })

        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()

        self.assertTrue(usuario.check_password(senha))
        self.assertNotEqual(usuario.password, senha)


class RelatorioAtendimentosTests(TestCase):
    def setUp(self):
        self.staff = Usuario.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            nome='Equipe',
            password='Strong-Staff-Password!2026',
            is_staff=True,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente-relatorio@example.com',
            email='cliente-relatorio@example.com',
            nome='Cliente Relatório',
            password='Strong-Client-Password!2026',
        )
        self.pet = Pet.objects.create(
            nome='Nina',
            data_de_nascimento=date(2022, 2, 1),
            raca='SRD',
            porte='Pequeno',
            usuario=self.cliente,
        )
        self.servico = Servico.objects.create(
            nome='Banho relatório',
            valor=Decimal('30.00'),
            duracao_minutos=30,
        )

    def criar_agendamento(self, status, data):
        agendamento = Agendamento.objects.create(
            usuario=self.cliente,
            pet=self.pet,
            data=data,
            status=status,
        )
        ItemAgendamento.objects.create(
            agendamento=agendamento,
            servico=self.servico,
            servico_nome=self.servico.nome,
            preco_unitario=Decimal('30.00'),
            duracao_minutos=30,
        )
        return agendamento

    def test_relatorio_conta_somente_atendimentos_concluidos_passados(self):
        agora = timezone.now()
        self.criar_agendamento(Agendamento.StatusChoices.CONCLUIDO, agora - timedelta(hours=1))
        self.criar_agendamento(Agendamento.StatusChoices.CANCELADO, agora - timedelta(hours=2))
        self.criar_agendamento(Agendamento.StatusChoices.PENDENTE, agora - timedelta(hours=3))
        self.criar_agendamento(Agendamento.StatusChoices.CONCLUIDO, agora + timedelta(hours=1))

        self.client.force_login(self.staff)
        response = self.client.get(
            reverse('relatorio'),
            {
                'data_inicio': (agora.date() - timedelta(days=1)).isoformat(),
                'data_fim': agora.date().isoformat(),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_atendimentos'], 1)
        self.assertEqual(response.context['total_faturamento'], Decimal('30.00'))


class AgendamentoHistoricoTests(TestCase):
    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente-agendamento@example.com',
            email='cliente-agendamento@example.com',
            nome='Cliente Agendamento',
            password='Strong-Client-Password!2026',
        )
        self.pet = Pet.objects.create(
            nome='Toby',
            data_de_nascimento=date(2021, 4, 12),
            raca='SRD',
            porte='Médio',
            usuario=self.cliente,
        )
        self.servico = Servico.objects.create(
            nome='Banho histórico',
            valor=Decimal('30.00'),
            duracao_minutos=30,
        )
        self.agendamento = Agendamento.objects.create(
            usuario=self.cliente,
            pet=self.pet,
            data=timezone.now() + timedelta(days=2),
        )
        ItemAgendamento.objects.create(
            agendamento=self.agendamento,
            servico=self.servico,
            servico_nome=self.servico.nome,
            preco_unitario=Decimal('25.00'),
            duracao_minutos=25,
        )

    def test_lista_mostra_agendamento_fora_de_faixa_de_turno(self):
        data_agendamento = timezone.localtime(self.agendamento.data).replace(
            hour=12, minute=30, second=0, microsecond=0
        )
        self.agendamento.data = data_agendamento
        self.agendamento.save(update_fields=['data'])
        self.client.force_login(self.cliente)

        response = self.client.get(
            reverse('agendamentos'),
            {'data': data_agendamento.date().isoformat()},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '12:30')
        self.assertContains(response, self.pet.nome)
        self.assertContains(response, self.servico.nome)
        self.assertNotContains(response, 'Manhã')

    def test_edicao_preserva_snapshot_de_servico_inativo(self):
        self.servico.valor = Decimal('50.00')
        self.servico.duracao_minutos = 60
        self.servico.ativo = False
        self.servico.save()

        self.client.force_login(self.cliente)
        response = self.client.post(
            reverse('editar_agendamento', args=[self.agendamento.pk]),
            {
                'pet': self.pet.pk,
                'data': timezone.localtime(self.agendamento.data).strftime('%Y-%m-%dT%H:%M'),
                'servicos': [self.servico.pk],
            },
            follow=True,
        )

        self.assertContains(response, 'Agendamento atualizado com sucesso!')
        item = ItemAgendamento.objects.get(agendamento=self.agendamento)
        self.assertEqual(item.preco_unitario, Decimal('25.00'))
        self.assertEqual(item.duracao_minutos, 25)
