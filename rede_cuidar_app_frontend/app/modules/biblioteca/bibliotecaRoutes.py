from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.modules.biblioteca import bibliotecaController
from app.modules.user import userController


router = APIRouter(prefix="/biblioteca", tags=["Biblioteca"])
templates = Jinja2Templates(
    directory=[
        Path(__file__).parent / "templates",
        Path(__file__).parents[2] / "templates",
    ]
)


@router.get("/", response_class=HTMLResponse)
async def biblioteca(request: Request) -> HTMLResponse:
    success, _ = await userController.autenticar(request)

    if not success:
        return RedirectResponse(url="/", status_code=303)

    context = bibliotecaController.biblioteca_context(request)
    return templates.TemplateResponse(
        request=request,
        name="biblioteca.html",
        context=context,
    )


@router.post("/chat")
async def chat(
    request: Request,
    data: bibliotecaController.ChatRequest,
) -> JSONResponse:
    success, message = await userController.autenticar(request)
    if not success:
        return JSONResponse(status_code=401, content={"detail": message})

    result, error, status_code = await bibliotecaController.enviar_mensagem(
        request,
        data,
    )
    if error is not None:
        return JSONResponse(
            status_code=status_code,
            content={"detail": error},
        )
    if result is None:
        return JSONResponse(
            status_code=502,
            content={"detail": "A API retornou uma resposta inválida."},
        )
    return JSONResponse(content=result)


@router.get("/noticias")
async def noticias(request: Request) -> JSONResponse:
    success, message = await userController.autenticar(request)
    if not success:
        return JSONResponse(status_code=401, content={"detail": message})

    result, error, status_code = await bibliotecaController.buscar_noticias(request)
    if error is not None:
        return JSONResponse(status_code=status_code, content={"detail": error})
    if result is None:
        return JSONResponse(
            status_code=502,
            content={"detail": "A API retornou uma resposta inválida."},
        )
    return JSONResponse(content=result)
