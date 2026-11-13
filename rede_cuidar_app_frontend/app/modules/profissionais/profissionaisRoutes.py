from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import quote

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.profissionais import profissionaisController
from app.modules.user import userController


router = APIRouter(prefix="/profissionais", tags=["Profissionais"])
templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


@router.get("/", response_class=HTMLResponse)
async def profissionais(request: Request) -> HTMLResponse:
    success, _ = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = await profissionaisController.profissionais_context(request)
    return templates.TemplateResponse(
        request=request,
        name="profissionais.html",
        context=context,
    )


@router.get("/painel", response_class=HTMLResponse)
async def painel_profissional(request: Request) -> HTMLResponse:
    success, _ = await userController.autenticar(request)
    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = await profissionaisController.painel_context(request)
    msg = request.query_params.get("msg")
    tipo = request.query_params.get("tipo")
    if msg:
        context["flash_message"] = msg
        context["flash_type"] = tipo or "success"

    return templates.TemplateResponse(
        request=request,
        name="painel_profissional.html",
        context=context,
    )


@router.post("/painel/divulgacao")
async def criar_divulgacao(
    request: Request,
    titulo: Annotated[str, Form()],
    descricao: Annotated[str, Form()],
    midia: Optional[UploadFile] = File(None),
) -> RedirectResponse:
    success, _ = await userController.autenticar(request)
    if not success:
        return RedirectResponse(url="/", status_code=303)

    ok, message = await profissionaisController.publicar_divulgacao(
        request=request,
        titulo=titulo,
        descricao=descricao,
        midia=midia,
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/profissionais/painel?tipo={tipo}&msg={quote(message)}",
        status_code=303,
    )


@router.post("/painel/divulgacao/{id_divulgacao}/excluir")
async def excluir_divulgacao(
    request: Request,
    id_divulgacao: int,
) -> RedirectResponse:
    success, _ = await userController.autenticar(request)
    if not success:
        return RedirectResponse(url="/", status_code=303)

    ok, message = await profissionaisController.excluir_divulgacao(
        request=request,
        id_divulgacao=id_divulgacao,
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/profissionais/painel?tipo={tipo}&msg={quote(message)}",
        status_code=303,
    )


@router.post("/painel/campanha")
async def contratar_campanha(
    request: Request,
    plano_codigo: Annotated[str, Form()],
) -> RedirectResponse:
    success, _ = await userController.autenticar(request)
    if not success:
        return RedirectResponse(url="/", status_code=303)

    ok, message = await profissionaisController.ativar_campanha(
        request=request,
        plano_codigo=plano_codigo,
    )
    tipo = "success" if ok else "error"
    return RedirectResponse(
        url=f"/profissionais/painel?tipo={tipo}&msg={quote(message)}",
        status_code=303,
    )