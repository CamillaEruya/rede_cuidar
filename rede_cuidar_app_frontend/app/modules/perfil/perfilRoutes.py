from pathlib import Path

from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
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
    success, _ = await userController.autenticar(request)
    
    if not success:
            return RedirectResponse(url="/", status_code=303)

    var_context = await perfilController.perfil_context(request)
    if request.query_params.get("foto_atualizada") == "1":
        var_context["message_foto_perfil"] = (
            "Foto de perfil atualizada com sucesso."
        )
        var_context["message_type_foto_perfil"] = "success"
    
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


@router.post("/foto", response_class=HTMLResponse)
async def atualizar_foto_perfil(
    request: Request,
    foto: Annotated[UploadFile, File()],
) -> Response:
    autenticado, _ = await userController.autenticar(request)
    if not autenticado:
        return RedirectResponse(url="/", status_code=303)

    success, message = await perfilController.atualizar_foto_perfil(
        request,
        foto,
    )
    if success:
        return RedirectResponse(
            url="/perfil/?foto_atualizada=1",
            status_code=303,
        )

    context = await perfilController.perfil_context(request)
    context["message_foto_perfil"] = message
    context["message_type_foto_perfil"] = "error"
    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context=context,
        status_code=400,
    )


@router.post("/profissional/atualizar", response_class=HTMLResponse)
async def atualizar_profissional(
    request: Request,
    endereco: Annotated[str, Form()],
    numero: Annotated[str, Form()],
    cidade: Annotated[str, Form()],
    estado: Annotated[str, Form()],
    cep: Annotated[str, Form()],
    telefone: Annotated[str, Form()],
    descricao: Annotated[str, Form()],
    inscricao_conselho: Annotated[str, Form()] = "",
    area_atuacao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    data = {
        "endereco": endereco.strip(),
        "numero": numero.strip(),
        "cidade": cidade.strip(),
        "estado": estado.strip(),
        "cep": cep.strip(),
        "telefone": telefone.strip(),
        "descricao": descricao.strip(),
        "inscricao_conselho": inscricao_conselho.strip() or None,
        "area_atuacao": area_atuacao.strip() or None,
    }
    success, message = await perfilController.atualizar_profissional(request, data)
    context = await perfilController.perfil_context(request)
    if not success:
        context["profissional"].update(data)
    context["success_profissional"] = success
    context["message_profissional"] = message
    context["message_type_profissional"] = "success" if success else "error"
    context["open_professional_modal"] = not success

    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context=context,
    )
