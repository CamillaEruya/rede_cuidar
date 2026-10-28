# API Python

API usando FastAPI e SQLAlchemy.

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

- `GET /api/pessoas`: lista pessoas em JSON.
- `GET /api/pessoas/{id}`: retorna uma pessoa em JSON.
- `POST /api/pessoas`: cadastra uma pessoa.
- `PUT /api/pessoas/{id}`: atualiza uma pessoa.
- `DELETE /api/pessoas/{id}`: exclui uma pessoa.

A conexão usa as variáveis do `.env`; as tabelas precisam existir no banco. O script
`database.sql` contém a estrutura das tabelas e os dados iniciais de tipos e perfis.
