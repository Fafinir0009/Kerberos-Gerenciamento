from datetime import date, timedelta
from decimal import Decimal
import re

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from kerberos.forms.FormAgendamento import AgendamentoForm
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

    def test_form_pet_rejeita_data_de_nascimento_anterior_a_100_anos(self):
        data = {
            'nome': 'Bidu',
            'data_de_nascimento': '0001-01-01',
            'raca': 'Shih Tzu',
            'porte': 'Pequeno',
            'observacao': '',
        }
        form = PetForm(data=data, user=self.cliente_a)

        self.assertFalse(form.is_valid())
        self.assertIn('data_de_nascimento', form.errors)

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

    def test_edicao_de_perfil_preserva_permissao_staff(self):
        usuario = Usuario.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            nome='Administrador',
            password='Existing-Strong-Password!2026',
            is_staff=True,
        )
        data = {
            'nome': 'Administrador Atualizado',
            'email': 'admin@example.com',
            'telefone': '(11) 91234-5678',
            'senha': '',
            'confirmar_senha': '',
        }
        form = UsuarioForm(data=data, instance=usuario)

        self.assertTrue(form.is_valid(), form.errors)
        usuario_atualizado = form.save()

        self.assertTrue(usuario_atualizado.is_staff)

    def test_telefone_opcional_aceita_vazio(self):
        data = self.data.copy()
        data['telefone'] = ''
        form = UsuarioForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)


class UsuarioLoginTests(TestCase):
    def test_tela_login_solicita_email(self):
        response = self.client.get(reverse('login'))

        self.assertContains(response, 'type="email"')
        self.assertContains(response, 'E-mail')

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

    def test_login_de_cliente_rejeita_username_que_nao_seja_email(self):
        usuario = Usuario.objects.create_user(
            username='cliente-login',
            email='cliente-login@example.com',
            nome='Cliente Login',
            password='Strong-Login-Password!2026',
        )

        response = self.client.post(
            reverse('login'),
            {
                'username': usuario.username,
                'password': 'Strong-Login-Password!2026',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_pode_entrar_com_username(self):
        usuario = Usuario.objects.create_user(
            username='admin-login',
            email='admin-login@example.com',
            nome='Administrador',
            password='Strong-Login-Password!2026',
            is_staff=True,
        )

        response = self.client.post(
            reverse('admin:login'),
            {
                'username': usuario.username,
                'password': 'Strong-Login-Password!2026',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_admin_pode_entrar_com_email(self):
        usuario = Usuario.objects.create_user(
            username='admin-login',
            email='admin-login@example.com',
            nome='Administrador',
            password='Strong-Login-Password!2026',
            is_staff=True,
        )

        response = self.client.post(
            reverse('admin:login'),
            {
                'username': usuario.email,
                'password': 'Strong-Login-Password!2026',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

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

    def test_relatorio_lista_todos_status_mas_fatura_so_concluidos_passados(self):
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
                'data_fim': (agora.date() + timedelta(days=1)).isoformat(),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Faturado (concluídos)')
        self.assertContains(response, 'Ticket Médio')
        self.assertEqual(len(response.context['agendamentos']), 4)
        self.assertIn(
            Agendamento.StatusChoices.PENDENTE,
            {agendamento.status for agendamento in response.context['agendamentos']},
        )
        self.assertIn(
            Agendamento.StatusChoices.CANCELADO,
            {agendamento.status for agendamento in response.context['agendamentos']},
        )
        self.assertEqual(response.context['total_atendimentos'], 1)
        self.assertEqual(response.context['total_faturamento'], Decimal('30.00'))

    def test_cliente_acessa_historico_apenas_dos_proprios_agendamentos(self):
        agora = timezone.now()
        agendamento_cliente = self.criar_agendamento(
            Agendamento.StatusChoices.CONCLUIDO,
            agora - timedelta(days=1),
        )

        outro_cliente = Usuario.objects.create_user(
            username='outro-cliente@example.com',
            email='outro-cliente@example.com',
            nome='Outro Cliente',
            password='Strong-Client-Password!2026',
        )
        outro_pet = Pet.objects.create(
            nome='Bolt',
            data_de_nascimento=date(2021, 5, 1),
            raca='SRD',
            porte='Médio',
            usuario=outro_cliente,
        )
        Agendamento.objects.create(
            usuario=outro_cliente,
            pet=outro_pet,
            data=agora - timedelta(days=1),
        )

        self.client.force_login(self.cliente)
        response = self.client.get(
            reverse('relatorio'),
            {
                'data_inicio': (agora.date() - timedelta(days=2)).isoformat(),
                'data_fim': agora.date().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [agendamento.pk for agendamento in response.context['agendamentos']],
            [agendamento_cliente.pk],
        )
        self.assertContains(response, 'Histórico de Atendimentos')
        self.assertContains(response, 'Histórico de Agendamentos')
        self.assertNotContains(response, 'Total Investido')
        self.assertNotContains(response, 'Atendimentos Concluídos')
        self.assertNotContains(response, 'Ticket Médio')
        self.assertNotContains(response, 'Bolt')


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

    def test_form_rejeita_agendamento_no_passado(self):
        data_passada = timezone.localtime() - timedelta(days=1)
        form = AgendamentoForm(
            data={
                'pet': self.pet.pk,
                'data': data_passada.strftime('%Y-%m-%dT%H:%M'),
                'servicos': [self.servico.pk],
            },
            usuario=self.cliente,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_form_rejeita_data_de_agendamento_do_ano_0001(self):
        form = AgendamentoForm(
            data={
                'pet': self.pet.pk,
                'data': '0001-01-01T00:00',
                'servicos': [self.servico.pk],
            },
            usuario=self.cliente,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_edicao_de_agendamento_historico_preserva_data_original(self):
        data_original = timezone.localtime() - timedelta(days=1)
        self.agendamento.data = data_original
        self.agendamento.save(update_fields=['data'])
        form = AgendamentoForm(
            data={
                'pet': self.pet.pk,
                'data': data_original.strftime('%Y-%m-%dT%H:%M'),
                'servicos': [self.servico.pk],
            },
            instance=self.agendamento,
            usuario=self.cliente,
        )

        self.assertTrue(form.is_valid(), form.errors)

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

    def test_admin_altera_status_e_volta_para_data_selecionada(self):
        admin = Usuario.objects.create_user(
            username='admin-agendamento@example.com',
            email='admin-agendamento@example.com',
            nome='Admin Agendamento',
            password='Strong-Admin-Password!2026',
            is_staff=True,
        )
        self.client.force_login(admin)
        data = timezone.localtime(self.agendamento.data).date().isoformat()

        response = self.client.post(
            reverse('alterar_status_agendamento', args=[self.agendamento.pk]),
            {'status': Agendamento.StatusChoices.CONFIRMADO, 'data': data},
        )

        self.agendamento.refresh_from_db()
        self.assertEqual(self.agendamento.status, Agendamento.StatusChoices.CONFIRMADO)
        self.assertRedirects(
            response,
            f"{reverse('agendamentos')}?data={data}",
        )

    def test_alteracao_de_status_rejeita_valor_invalido(self):
        admin = Usuario.objects.create_user(
            username='admin-status@example.com',
            email='admin-status@example.com',
            nome='Admin Status',
            password='Strong-Admin-Password!2026',
            is_staff=True,
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse('alterar_status_agendamento', args=[self.agendamento.pk]),
            {'status': 'Status inválido'},
        )

        self.agendamento.refresh_from_db()
        self.assertEqual(self.agendamento.status, Agendamento.StatusChoices.PENDENTE)
        self.assertRedirects(response, reverse('agendamentos'))

    def test_cliente_nao_pode_alterar_status(self):
        self.client.force_login(self.cliente)

        response = self.client.post(
            reverse('alterar_status_agendamento', args=[self.agendamento.pk]),
            {'status': Agendamento.StatusChoices.CONFIRMADO},
        )

        self.agendamento.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.agendamento.status, Agendamento.StatusChoices.PENDENTE)


class CadastroCompostoTests(TestCase):
    def test_cadastro_preserva_nome_do_tutor_e_do_pet_separadamente(self):
        response = self.client.post(
            reverse('cadastro'),
            {
                'usuario-nome': 'Tutor Exemplo',
                'usuario-email': 'tutor-exemplo@example.com',
                'usuario-telefone': '(11) 91234-5678',
                'usuario-senha': 'Strong-Registration-Password!2026',
                'usuario-confirmar_senha': 'Strong-Registration-Password!2026',
                'usuario-aceita_regulamento': 'on',
                'endereco-cep': '01001-000',
                'endereco-logradouro': 'Praça da Sé',
                'endereco-numero': '1',
                'endereco-complemento': '',
                'endereco-bairro': 'Sé',
                'endereco-cidade': 'São Paulo',
                'endereco-uf': 'SP',
                'pet-nome': 'Chuchu',
                'pet-data_de_nascimento': '2021-02-01',
                'pet-raca': 'SRD',
                'pet-porte': 'Pequeno',
                'pet-observacao': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        usuario = Usuario.objects.get(email='tutor-exemplo@example.com')
        pet = Pet.objects.get(usuario=usuario)
        self.assertEqual(usuario.nome, 'Tutor Exemplo')
        self.assertEqual(pet.nome, 'Chuchu')

    def test_cadastro_rejeita_sem_aceite_do_regulamento(self):
        response = self.client.post(reverse('cadastro'), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Regulamento Geral')
        self.assertContains(response, 'name="usuario-aceita_regulamento"')
        self.assertContains(response, 'Li e concordo com o regulamento.')
        self.assertIn(
            'aceita_regulamento', response.context['form_usuario'].errors
        )
        self.assertEqual(Usuario.objects.count(), 0)


class PasswordChangeCsrfTests(TestCase):
    def test_logout_funciona_apos_alterar_senha_sem_recarregar_manualmente(self):
        usuario = Usuario.objects.create_user(
            username='admin-csrf@example.com',
            email='admin-csrf@example.com',
            nome='Admin CSRF',
            password='Original-Strong-Password!2026',
            is_staff=True,
        )
        client = Client(enforce_csrf_checks=True)
        client.force_login(usuario)

        perfil = client.get(reverse('perfil'))
        token_senha = re.search(
            rb'name="csrfmiddlewaretoken" value="([^"]+)"', perfil.content
        ).group(1).decode()
        csrf_antes = client.cookies['csrftoken'].value
        resposta = client.post(
            reverse('perfil'),
            {
                'csrfmiddlewaretoken': token_senha,
                'old_password': 'Original-Strong-Password!2026',
                'new_password1': 'Changed-Strong-Password!2026',
                'new_password2': 'Changed-Strong-Password!2026',
                'btn_alterar_senha': '1',
            },
            follow=True,
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(client.cookies['csrftoken'].value, csrf_antes)

        resposta_logout = client.post(
            reverse('logout'), {'csrfmiddlewaretoken': token_senha}
        )

        self.assertRedirects(resposta_logout, reverse('login'))
