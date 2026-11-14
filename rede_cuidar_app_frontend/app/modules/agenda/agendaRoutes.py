from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import quote

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.agenda import agendaController
from app.modules.user import userController


router = APIRouter(prefix="/agenda", tags=["Agenda"])
templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


@router.get("/", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
async def agenda(request: Request) -> HTMLResponse:
    success, _ = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = agendaController.agenda_context(request)
    return templates.TemplateResponse(
        request=request,
        name="agenda.html",
        context=context,
    )


@router.post("/novo")
async def criar_evento(
    request: Request,
    titulo: Annotated[str, Form()],
    descricao: Annotated[str, Form()],
    tipo_evento: Annotated[str, Form()],
    data_evento: Annotated[str, Form()],
    midia: Annotated[Optional[UploadFile], File()] = None,
) -> RedirectResponse:
    success, _ = await userController.autenticar(request)
    if not success or not agendaController.eh_admin(request):
        return RedirectResponse(url="/agenda?tipo=error&msg=Acesso+restrito+a+administradores", status_code=303)

    ok, msg = await agendaController.criar_evento(
        request, titulo, descricao, tipo_evento, data_evento, midia=midia
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(url=f"/agenda?tipo={tipo}&msg={quote(msg)}", status_code=303)


@router.post("/{id_agenda}/editar")
async def editar_evento(
    request: Request,
    id_agenda: int,
    titulo: Annotated[str, Form()],
    descricao: Annotated[str, Form()],
    tipo_evento: Annotated[str, Form()],
    data_evento: Annotated[str, Form()],
    status: Annotated[str, Form()] = "ATIVO",
    remover_midia: Annotated[Optional[str], Form()] = None,
    midia: Annotated[Optional[UploadFile], File()] = None,
) -> RedirectResponse:
    success, _ = await userController.autenticar(request)
    if not success or not agendaController.eh_admin(request):
        return RedirectResponse(url="/agenda?tipo=error&msg=Acesso+restrito+a+administradores", status_code=303)

    ok, msg = await agendaController.atualizar_evento(
        request,
        id_agenda,
        titulo,
        descricao,
        tipo_evento,
        data_evento,
        status,
        remover_midia=bool(remover_midia),
        midia=midia,
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(url=f"/agenda?tipo={tipo}&msg={quote(msg)}", status_code=303)


@router.post("/{id_agenda}/excluir")
async def excluir_evento(
    request: Request,
    id_agenda: int,
) -> RedirectResponse:
    success, _ = await userController.autenticar(request)
    if not success or not agendaController.eh_admin(request):
        return RedirectResponse(url="/agenda?tipo=error&msg=Acesso+restrito+a+administradores", status_code=303)

    ok, msg = await agendaController.excluir_evento(request, id_agenda)
    tipo = "success" if ok else "error"
    return RedirectResponse(url=f"/agenda?tipo={tipo}&msg={quote(msg)}", status_code=303)