# Rede Cuidar API

Backend HTTP usando FastAPI e SQLAlchemy. A API registra os routers definidos
em `app/modules/<nome>/<nome>Router.py`; controllers, models e regras auxiliares
permanecem no backend.

O endpoint `/` não serve uma página frontend. A documentação interativa fica em
`/docs`, e `GET /health` verifica se a API está disponível.

## Rotas de pessoas

- `GET /api/pessoas`: lista pessoas.
- `GET /api/pessoas/tipo-perfil`: lista tipos de perfil ativos.
- `GET /api/pessoas/{id}`: retorna uma pessoa.
- `POST /api/pessoas`: cadastra uma pessoa.
- `PUT /api/pessoas/{id}`: atualiza uma pessoa.
- `DELETE /api/pessoas/{id}`: exclui uma pessoa.

O cadastro usa os campos `id_tipo_pessoa`, `id_tipo_perfil` (opcional),
`nome_razao`, `email`, `cpf_cnpj` e `ativo`. Cada pessoa pode ter um único perfil,
referenciado diretamente por `id_tipo_perfil`.

## Cadastro de profissional

- `POST /api/profissional`: cadastra os dados profissionais de uma pessoa já
  cadastrada. Cada pessoa pode ter um único cadastro profissional.
- `GET /api/profissional/{id_pessoa}`: consulta os dados profissionais da pessoa
  autenticada.
- `GET /api/profissional`: lista os cadastros profissionais de pessoas ativas
  para a comunidade autenticada.
- `PUT /api/profissional/{id_pessoa}`: cria ou atualiza os dados profissionais da
  pessoa autenticada.

No POST, o corpo deve conter `id_pessoa`, `endereco`, `numero`, `cidade`, `estado`,
`cep`, `telefone` e `descricao`. No PUT, envie os campos profissionais sem
`id_pessoa`, que é obtido da URL. `inscricao_conselho` e `area_atuacao` são
opcionais. `status_verificacao` não pode ser alterado pelo cliente; em um novo
cadastro, inicia como `PENDENTE`.
As rotas GET e PUT exigem token Bearer e só permitem consultar ou alterar o cadastro
da própria pessoa. A rota PUT preserva o status de verificação já existente.
O catálogo inclui todos os status de verificação das pessoas ativas.

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute:

```bash
python run.py
```

A API Python ficará disponível em `http://localhost:8001`, com documentação em `/docs`.

Configure a conexão do banco no `.env`. Para usar o MySQL:

```dotenv
DB_CONNECTION=mysql
DB_DATABASE=nome_do_banco
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=usuario
DB_PASSWORD=senha
```

O SQLite continua disponível para desenvolvimento local com `DB_CONNECTION=sqlite`
e `DB_DATABASE=database.sqlite`; o arquivo do banco local não é incluído no projeto.

## Configuração do banco

A conexão usa as variáveis do `.env`. As tabelas necessárias devem existir no banco
MySQL antes de iniciar a API.
