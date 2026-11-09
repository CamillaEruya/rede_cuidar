from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.modules.home import homeController

router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    context = homeController.home_context(request)
    context["tipos_perfil"] = await homeController.listar_tipos_perfil()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=context,
    )


@router.post("/cadastro", response_class=HTMLResponse)
async def cadastro(
    request: Request,
    nome_razao: Annotated[str, Form()],
    email: Annotated[str, Form()],
    cpf_cnpj: Annotated[str, Form()],
    senha: Annotated[str, Form()],
    confirmar_senha: Annotated[str, Form()],
    id_tipo_perfil: Annotated[int, Form()],
) -> HTMLResponse:
    success, message = await homeController.cadastrar_pessoa(
        {
            "nome_razao": nome_razao.strip(),
            "email": email.strip(),
            "cpf_cnpj": cpf_cnpj.strip(),
            "id_tipo_perfil": id_tipo_perfil,
            "senha": senha.strip(),
            "confirmar_senha": confirmar_senha.strip(),
            "ativo": True,
        }
    )
    context = homeController.home_context(request, message)
    context["tipos_perfil"] = await homeController.listar_tipos_perfil()
    context["success_cadastro"] = success
    context["message_cadastro"] = message
    context["message_type"] = "success" if success else "error"
    context["open_register"] = not success
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=context,
    )

@router.post("/logar", response_class=HTMLResponse)
async def logar(
    request: Request,
    email: Annotated[str, Form()],
    senha: Annotated[str, Form()]
) -> Response:
    success, message = await homeController.logar(
        request,
        {
            "email": email.strip(),
            "senha": senha.strip()
        }
    )
    if success:
        return RedirectResponse(url="/feed/", status_code=303)

    context = homeController.home_context(request, message)
    context["tipos_perfil"] = await homeController.listar_tipos_perfil()
    context["success_login"] = success
    context["message_login"] = message
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=context,
    )
