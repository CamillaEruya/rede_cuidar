from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.modules.pessoas.pessoasRoutes import router as pessoas_router
from app.modules.user.userRoutes import router as user_router

app = FastAPI(title="API Python")
app.include_router(pessoas_router)
app.include_router(user_router)

@app.get("/")
def home() -> HTMLResponse:
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Rede Cuidar</title>
            <style>
                :root {
                    --azul-claro: #dfeeff;
                    --amarelo-claro: #fff1b8;
                    --rosa-claro: #f9d7e5;
                    --branco: #ffffff;
                    --texto: #1f2a37;
                    --cinza: #6b7280;
                    --sombra: rgba(58, 76, 104, 0.12);
                }

                * {
                    box-sizing: border-box;
                    font-family: Arial, Helvetica, sans-serif;
                }

                body {
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #f5f7fb 0%, #eef4ff 100%);
                    color: var(--texto);
                }

                .container {
                    display: flex;
                    width: min(1100px, 90vw);
                    min-height: 620px;
                    background: var(--branco);
                    border-radius: 26px;
                    overflow: hidden;
                    box-shadow: 0 24px 60px var(--sombra);
                }

                .info-panel {
                    flex: 1.15;
                    background: var(--branco);
                    padding: 56px 48px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }

                .tag {
                    display: inline-block;
                    background: var(--rosa-claro);
                    color: var(--texto);
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    border-radius: 999px;
                    padding: 10px 18px;
                    margin-bottom: 20px;
                    width: fit-content;
                }

                h1 {
                    margin: 0 0 16px;
                    font-size: clamp(2rem, 3vw, 3.2rem);
                    line-height: 1.1;
                }

                .subtitle {
                    margin: 0 0 28px;
                    color: var(--cinza);
                    font-size: 1.02rem;
                    line-height: 1.7;
                    max-width: 440px;
                }

                .stats {
                    display: flex;
                    gap: 20px;
                    flex-wrap: wrap;
                    margin-top: 18px;
                }

                .stat {
                    background: #f8faff;
                    border: 1px solid #edf2ff;
                    border-radius: 18px;
                    padding: 18px 20px;
                    min-width: 140px;
                }

                .stat strong {
                    display: block;
                    font-size: 1.6rem;
                    margin-bottom: 5px;
                }

                .stat span {
                    color: var(--cinza);
                    font-size: 0.82rem;
                }

                .form-panel {
                    flex: 0.95;
                    background: var(--azul-claro);
                    padding: 48px 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .form-box {
                    width: min(100%, 400px);
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.4);
                    border-radius: 22px;
                    padding: 30px;
                    backdrop-filter: blur(2px);
                }

                .form-box h2 {
                    margin: 0 0 26px;
                    text-align: center;
                    font-size: 1.8rem;
                }

                .field {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    margin-bottom: 16px;
                    color: var(--texto);
                    font-size: 0.9rem;
                    font-weight: 600;
                }

                .field input,
                .field select {
                    border: 1px solid rgba(31, 42, 55, 0.12);
                    background: var(--branco);
                    border-radius: 12px;
                    height: 48px;
                    padding: 0 14px;
                    font-size: 1rem;
                    color: var(--texto);
                    outline: none;
                }

                .field input:focus,
                .field select:focus {
                    border-color: rgba(88, 130, 202, 0.55);
                    box-shadow: 0 0 0 3px rgba(88, 130, 202, 0.12);
                }

                .actions {
                    display: flex;
                    gap: 12px;
                    margin-top: 24px;
                }

                .btn {
                    flex: 1;
                    border: none;
                    border-radius: 12px;
                    height: 48px;
                    font-size: 0.96rem;
                    font-weight: 700;
                    cursor: pointer;
                    transition: transform 0.2s ease, opacity 0.2s ease;
                }

                .btn:hover {
                    transform: translateY(-1px);
                    opacity: 0.95;
                }

                .btn-primary {
                    background: var(--rosa-claro);
                    color: var(--texto);
                }

                .btn-secondary {
                    background: var(--amarelo-claro);
                    color: var(--texto);
                }

                @media (max-width: 820px) {
                    .container {
                        flex-direction: column;
                    }

                    .info-panel,
                    .form-panel {
                        padding: 32px 22px;
                    }

                    .actions {
                        flex-direction: column;
                    }
                }
            </style>
        </head>
        <body>
            <main class="container">
                <section class="info-panel">
                    <span class="tag">Rede Cuidar</span>
                    <h1>Conectando cuidado, acolhimento e comunidade.</h1>
                    <p class="subtitle">
                        Uma plataforma pensada para apoiar pessoas e organizações com acesso,
                        informação e atenção em um ambiente seguro e acolhedor.
                    </p>

                    <div class="stats">
                        <div class="stat">
                            <strong>1.2k</strong>
                            <span>pessoas atendidas</span>
                        </div>
                        <div class="stat">
                            <strong>96%</strong>
                            <span>aprovação</span>
                        </div>
                    </div>
                </section>

                <aside class="form-panel">
                    <div class="form-box">
                        <h2>Cadastro</h2>

                        <div class="field">
                            <label for="nome">Nome</label>
                            <input id="nome" type="text" placeholder="Seu nome" />
                        </div>

                        <div class="field">
                            <label for="email">E-mail</label>
                            <input id="email" type="email" placeholder="seu@email.com" />
                        </div>

                        <div class="field">
                            <label for="perfil">Perfil</label>
                            <select id="perfil">
                                <option>Voluntário</option>
                                <option>Colaborador</option>
                                <option>Beneficiário</option>
                            </select>
                        </div>

                        <div class="actions">
                            <button class="btn btn-primary" type="button">Salvar</button>
                            <button class="btn btn-secondary" type="button">Cancelar</button>
                        </div>
                    </div>
                </aside>
            </main>
        </body>
        </html>
        """
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
