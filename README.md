# Kerberos-Gerenciamento

O Kerberos é uma plataforma de gestão focada no mercado pet, desenvolvida para simplificar o agendamento de banho e tosa, controle de horários e cadastro de clientes e pets. Ideal para petshops.

  **Funcionalidades**

Painel do Administrador (Petshop)
- Agenda Centralizada: Controle visual de horários, cliente e serviços.
- Gestão de Clientes e Pets: Histórico de atendimento, preferências informações de saúde (vacinas, alergias).
- Relatórios: Controle de fluxo de caixa e serviços realizados.

Portal do Cliente (Tutor)
- Agendamento Online: Escolha de data, horário, serviço e profissional em tempo real. 
- Meus Pets: Cadastro de múltiplos pets com foto, raça, idade e restrições.
- Histórico de Serviços: Visualização de todos os serviços agendados no passado ou futuros.


**Tecnologias Utilizadas**

- Frontend:
- Backend: Python/Django
- Banco de Dados:
- Hospedagem: 

**Como Rodar o Projeto**

Requer Python compatível com as dependências listadas em `requirements.txt`.

```bash
cd ProjetoFamaPet
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
cp .env.example .env
```

Gere uma chave secreta e configure `DJANGO_SECRET_KEY` no arquivo `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Depois, inicialize o banco e execute o servidor local:

```bash
python manage.py migrate
python manage.py runserver
```

Para produção, configure `DEBUG=False`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS` e `DATABASE_URL` com valores próprios do ambiente. Sirva
a aplicação exclusivamente por HTTPS. Configure `USE_X_FORWARDED_PROTO=True`
somente quando um proxy confiável remover e definir esse cabeçalho. Habilite
`SECURE_HSTS_INCLUDE_SUBDOMAINS` ou `SECURE_HSTS_PRELOAD` somente se todos os
subdomínios relevantes estiverem permanentemente preparados para HTTPS.
