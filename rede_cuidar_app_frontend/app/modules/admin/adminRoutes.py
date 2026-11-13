from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.admin import adminController
from app.modules.perfil.perfilController import perfil_context
from app.modules.user import userController

router = APIRouter(prefix="/admin", tags=["Administração"])

templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


def _eh_admin_sessao(request: Request) -> bool:
    return request.session.get("id_tipo_perfil") == 9


@router.get("/", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
async def painel_admin(request: Request) -> HTMLResponse:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado:
        return RedirectResponse(url="/", status_code=303)

    if not _eh_admin_sessao(request):
        return RedirectResponse(url="/feed", status_code=303)

    context = await perfil_context(request)
    dados_admin = await adminController.carregar_painel_admin(request)
    context.update(dados_admin)

    context["flash_msg"] = request.query_params.get("msg")
    context["flash_type"] = request.query_params.get("tipo", "success")
    context["aba_ativa"] = request.query_params.get("aba", "usuarios")

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context=context,
    )


@router.post("/usuarios/{pessoa_id}")
async def salvar_usuario(
    request: Request,
    pessoa_id: int,
    id_tipo_perfil: Annotated[int, Form()],
    ativo: Annotated[int, Form()] = 0,
) -> RedirectResponse:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado or not _eh_admin_sessao(request):
        return RedirectResponse(url="/", status_code=303)

    ok, msg = await adminController.atualizar_usuario(
        request, pessoa_id, id_tipo_perfil, ativo
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/admin?aba=usuarios&tipo={tipo}&msg={quote(msg)}",
        status_code=303,
    )


@router.post("/profissionais/{pessoa_id}/status")
async def salvar_status_profissional(
    request: Request,
    pessoa_id: int,
    status_verificacao: Annotated[str, Form()],
) -> RedirectResponse:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado or not _eh_admin_sessao(request):
        return RedirectResponse(url="/", status_code=303)

    ok, msg = await adminController.atualizar_status_profissional(
        request, pessoa_id, status_verificacao
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/admin?aba=profissionais&tipo={tipo}&msg={quote(msg)}",
        status_code=303,
    )


@router.post("/agendas/{agenda_id}/status")
async def salvar_status_agenda(
    request: Request,
    agenda_id: int,
    status: Annotated[str, Form()],
) -> RedirectResponse:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado or not _eh_admin_sessao(request):
        return RedirectResponse(url="/", status_code=303)

    ok, msg = await adminController.atualizar_status_agenda(
        request, agenda_id, status
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/admin?aba=agendas&tipo={tipo}&msg={quote(msg)}",
        status_code=303,
    )


@router.post("/publicacoes/{publicacao_id}/status")
async def salvar_status_publicacao(
    request: Request,
    publicacao_id: int,
    ativo: Annotated[int, Form()],
) -> RedirectResponse:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado or not _eh_admin_sessao(request):
        return RedirectResponse(url="/", status_code=303)

    ok, msg = await adminController.atualizar_status_publicacao(
        request, publicacao_id, ativo
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/admin?aba=publicacoes&tipo={tipo}&msg={quote(msg)}",
        status_code=303,
    )
