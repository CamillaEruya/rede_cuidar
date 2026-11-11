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

## Publicações do feed

- `GET /api/publicacoes`: lista as publicações de pessoas ativas.
- `POST /api/publicacoes`: cria uma publicação para a pessoa autenticada. Envie
  `descricao` (até 1000 caracteres) e, opcionalmente, `foto` como caminho; é necessário
  informar o cabeçalho `X-User-ID` e um token Bearer.
- `POST /api/publicacoes/com-foto`: cria uma publicação com upload multipart
  (`descricao` opcional e `foto` obrigatória). Aceita JPG, PNG, GIF e WebP de
  até 5 MB; salva a imagem em `app/uploads/publicacoes` e registra o caminho
  em `publicacao.foto`.
- `PUT /api/publicacoes/{id_publicacao}` e
  `DELETE /api/publicacoes/{id_publicacao}`: atualizam ou desativam uma
  publicação pertencente à pessoa autenticada.

`PUT /api/pessoas/{id_pessoa}/foto-perfil` recebe o campo multipart `foto`,
autenticado com token Bearer, e atualiza `pessoa.foto_perfil`. A foto é
armazenada em `app/uploads/perfis` e pode ser exibida como avatar; sem foto, o
frontend mantém as iniciais da pessoa.

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

Para habilitar as fotos de perfil, aplique uma vez a migração
`migrations/20261110_add_foto_perfil_to_pessoa.sql` no banco configurado. Ela
adiciona a coluna opcional `pessoa.foto_perfil`; as imagens enviadas ficam em
`app/uploads/perfis` e são servidas pela rota `/uploads`.
