# Rede Cuidar

## Subir os três serviços com Docker

Com Docker Engine e Compose v2 instalados, configure os arquivos
`rede_cuidar_api_backend/.env` e `rede_cuidar_app_frontend/.env`.
Há modelos `.env.example` nas duas pastas.

No `.env` do backend, preencha `DB_DATABASE`, `DB_USERNAME` e `DB_PASSWORD`
(senha obrigatória). O nome do banco vem de `DB_DATABASE`, por exemplo,
`rede_cuidar`. O usuário de `DB_USERNAME` recebe acesso a esse banco e usa a
senha de `DB_PASSWORD`. A API usa o mesmo banco.

Na raiz deste repositório, execute:

```sh
docker compose up -d --build
```

| Serviço / imagem | Acesso na máquina |
| --- | --- |
| `rede_cuidar_web` | http://localhost:8000 |
| `rede_cuidar_api` | http://localhost:8001/docs |
| `rede_cuidar_db` (MariaDB 11.4) | `127.0.0.1:3308` |

O banco usa a imagem local `rede_cuidar_db`, baseada em MariaDB 11.4,
compatível com o dump existente, que foi exportado do
MariaDB. Os três containers usam a rede Docker `rede_cuidar`. As imagens das
aplicações se chamam `rede_cuidar_api` e `rede_cuidar_web`; as pastas de código
permanecem com seus nomes atuais.

As portas das aplicações são definidas nos Dockerfiles. Dentro dos containers,
elas escutam em `0.0.0.0`. A API acessa `rede_cuidar_db:3306`, e a web acessa
o endereço de `API_BASE_URL` no `.env` do frontend, sem sobrescrita pelo Compose.
Para Docker, configure `API_BASE_URL=http://rede_cuidar_api:8001`; para executar
o frontend diretamente na máquina, use `API_BASE_URL=http://localhost:8001`.
A conexão da API também vem diretamente do `.env` do backend. Para Docker,
use `DB_CONNECTION=mysql`, `DB_HOST=rede_cuidar_db` e `DB_PORT=3306`.
Para executar a API diretamente na máquina usando o banco Docker, use
`DB_HOST=127.0.0.1` e `DB_PORT=3308`.

Na sua máquina, use a porta **3308** para acessar o banco Docker, evitando
conflito com o MySQL local em 3306. A porta do banco é publicada apenas em
`127.0.0.1`. Não altere `DB_PORT` para 3308 para a comunicação entre containers.

Na primeira inicialização de um volume vazio, o banco e o usuário são criados
automaticamente, e `dump/rede_cuidar_mysql.sql` é importado no banco escolhido.
O dump original permanece intacto. A API aguarda o banco estar pronto; a web
aguarda a API responder em `/health`.

Os dados ficam no volume `banco_dados`. `docker compose down` preserva os dados.
Ao recriar o container com `docker compose up -d --build`, o usuário, a senha e
o acesso ao banco são sincronizados com o `.env`, inclusive com volume existente.
A importação do dump só ocorre em volume vazio. Usuários anteriores não são
removidos automaticamente ao trocar `DB_USERNAME`.
O script de inicialização faz parte da imagem do banco: alterações nele são
detectadas por `--build`, permitindo ao Compose recriar o container automaticamente.

Para conferir os serviços e logs:

```sh
docker compose ps
docker compose logs -f
```

## Assistente da Biblioteca

O chat da biblioteca usa a API Gemini para responder perguntas com base
somente nos PDFs disponíveis. Crie uma chave no
[Google AI Studio](https://aistudio.google.com/apikey) e configure
`GEMINI_API_KEY` no `rede_cuidar_api_backend/.env`. O modelo padrão é
`gemini-3.5-flash-lite`; ele pode ser alterado em `GEMINI_MODEL`. Não coloque
a chave no frontend.

O Gemini oferece uma faixa gratuita com limites de uso sujeitos a alterações.
Na faixa gratuita, o Google pode usar as solicitações para melhorar seus
produtos. Evite enviar documentos com dados pessoais ou informações
confidenciais.

A seção de notícias consulta o Google News RSS, mostra até três resultados dos
últimos 30 dias e aceita apenas domínios institucionais e veículos reconhecidos
configurados no backend. Os links abrem o resultado no Google News; a matéria e
a publicação original continuam sob responsabilidade da fonte.

No Debian, crie a pasta compartilhada e copie para ela PDFs com texto
selecionável:

```sh
mkdir -p documentos/biblioteca
cp /caminho/para/documento.pdf documentos/biblioteca/
docker compose up -d --build
```

A pasta `documentos/biblioteca` é montada somente para leitura no container da
API. Execute o comando de build ao implantar o código ou alterar dependências;
depois disso, novos PDFs podem ser copiados para a pasta sem reconstruir ou
reiniciar os containers. O conteúdo é lido quando uma pergunta é enviada.
PDFs digitalizados precisam passar por OCR antes de serem usados. O chat mantém
o histórico apenas durante a sessão da página; as respostas incluem os nomes
dos documentos e as páginas consultadas.
