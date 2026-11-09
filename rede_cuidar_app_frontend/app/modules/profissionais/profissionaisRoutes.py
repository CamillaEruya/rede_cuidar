from pathlib import Path

from fastapi import APIRouter, Request
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
    success, message = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = profissionaisController.profissionais_context(request)
    return templates.TemplateResponse(
        request=request,
        name="profissionais.html",
        context=context,
    )
