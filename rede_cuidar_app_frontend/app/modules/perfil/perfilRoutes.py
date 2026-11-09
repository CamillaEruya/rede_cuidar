from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from app.modules.perfil import perfilController
from app.modules.user import userController


router = APIRouter(prefix="/perfil", tags=["Perfil"])
templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


@router.get("/", response_class=HTMLResponse)
async def perfil(request: Request) -> HTMLResponse:
    success, message = await userController.autenticar(request)
    
    if not success:
            return RedirectResponse(url="/", status_code=303)

    var_context = await perfilController.perfil_context(request)
    
    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context=var_context,
    )

@router.post("/atualizar", response_class=HTMLResponse)
async def atualizar(
    request: Request,
    nome_razao: Annotated[str, Form()],
    email: Annotated[str, Form()],
    id_tipo_perfil: Annotated[int, Form()],
    senha: Annotated[str, Form()],
    confirmar_senha: Annotated[str, Form()],
) -> HTMLResponse:
    data = {
                "nome_razao": nome_razao.strip(),
                "email": email.strip(),
                "id_tipo_perfil": id_tipo_perfil,
                "senha": senha.strip(),
                "confirmar_senha": confirmar_senha.strip()
            }
    success, message = await perfilController.atualizar(request, data)
    context = await perfilController.perfil_context(request)
    context["success_cadastro"] = success
    context["message_cadastro"] = message
    context["message_type"] = "success" if success else "error"

    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context=context,
    )
