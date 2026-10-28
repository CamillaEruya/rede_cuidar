# Rede Cuidar - Frontend

Frontend em FastAPI com templates Jinja2, organizado por módulos.

## Executar

```bash
python -m pip install -r requirements.txt
python run.py
```

Acesse `http://localhost:8000`. A API usada no cadastro é configurada em `.env`:

```dotenv
API_BASE_URL=http://localhost:8001
```

## Estrutura

- `app/main.py`: aplicação FastAPI e arquivos estáticos.
- `app/modules/home/`: `homeRoutes.py`, `homeController.py` e template da tela inicial/cadastro.
- `app/modules/feed/`: `feedRoutes.py` e template demonstrativo da timeline (`/feed`).
- `app/modules/perfil/`: `perfilRoutes.py`, `perfilController.py` e template do perfil.
- `app/modules/agenda/`: `agendaRoutes.py`, `agendaController.py` e agenda demonstrativa de eventos (`/agenda`).
- `app/modules/biblioteca/`: `bibliotecaRoutes.py`, `bibliotecaController.py` e biblioteca demonstrativa com chat e notícias (`/biblioteca`).
- `app/modules/profissionais/`: `profissionaisRoutes.py`, `profissionaisController.py` e catálogo demonstrativo de profissionais (`/profissionais`).
- `app/modules/user/`: `userController.py`, com autenticação e utilitários de usuário.
- `app/static/assets/`: logotipo da Rede Cuidar.
- `app/static/css/` e `app/static/js/`: apresentação e interações da tela.
