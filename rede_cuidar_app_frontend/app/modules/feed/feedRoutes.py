from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.perfil.perfilController import perfil_context
from app.modules.user import userController

router = APIRouter(prefix="/feed", tags=["Feed"])

templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


@router.get("/", response_class=HTMLResponse)
async def timeline(request: Request) -> HTMLResponse:
    success, message = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = await perfil_context(request)

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context
    )


@router.get("/feed")
async def feed(request: Request):
    success, message = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = await perfil_context(request)

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context
    )