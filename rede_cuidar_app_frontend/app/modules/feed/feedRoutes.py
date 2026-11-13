from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.modules.feed import feedController
from app.modules.perfil.perfilController import perfil_context
from app.modules.user import userController

router = APIRouter(prefix="/feed", tags=["Feed"])

templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


async def _feed_context(request: Request) -> dict[str, Any]:
    context = await perfil_context(request)
    publicacoes, feed_error = await feedController.listar_publicacoes(request)
    context["publicacoes"] = publicacoes
    context["feed_error"] = feed_error
    context["descricao_publicacao"] = ""
    return context


@router.get("/", response_class=HTMLResponse)
async def timeline(request: Request) -> HTMLResponse:
    success, _ = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = await _feed_context(request)
    if request.query_params.get("publicado") == "1":
        context["message_publicacao"] = "Publicação compartilhada com sucesso."
        context["message_type_publicacao"] = "success"

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context
    )


@router.post("/publicar", response_class=HTMLResponse)
async def publicar(
    request: Request,
    descricao: Annotated[str, Form()] = "",
    foto: Annotated[UploadFile | None, File()] = None,
) -> Response:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado:
        return RedirectResponse(url="/", status_code=303)

    success, message = await feedController.criar_publicacao(
        request,
        descricao,
        foto,
    )
    if success:
        return RedirectResponse(url="/feed/?publicado=1", status_code=303)

    context = await _feed_context(request)
    context["descricao_publicacao"] = descricao
    context["message_publicacao"] = message
    context["message_type_publicacao"] = "error"
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context,
        status_code=400,
    )


@router.get("/feed")
async def feed(request: Request):
    success, _ = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = await _feed_context(request)

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context
    )