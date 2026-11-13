from typing import Optional
from fastapi import APIRouter, File, Form, Header, Query, UploadFile
from app.core.image_upload import store_media
from app.modules.agenda import agendaController

router = APIRouter(prefix="/api/agenda", tags=["Agenda"])


def _extrair_token(authorization: Optional[str]) -> str:
    if not authorization:
        return ""
    return authorization.replace("Bearer ", "").strip()


@router.get("/disponiveis")
async def listar_disponiveis(incluir_inativos: bool = Query(default=False)):
    return agendaController.listar_agendamentos_disponiveis(incluir_inativos=incluir_inativos)


@router.post("")
@router.post("/")
async def criar_evento(
    titulo: str = Form(...),
    descricao: str = Form(...),
    tipo_evento: str = Form("Comunidade"),
    data_evento: str = Form(...),
    midia: Optional[UploadFile] = File(default=None),
    x_user_id: Optional[int] = Header(default=None, alias="X-User-ID"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
):
    token = _extrair_token(authorization)
    pessoa_id = x_user_id or 0
    agendaController.validar_admin(pessoa_id, token)

    midia_url = None
    midia_tipo = None
    if midia and midia.filename:
        midia_url, midia_tipo, _ = await store_media(midia, "agenda")

    payload = {
        "titulo": titulo,
        "descricao": descricao,
        "tipo_evento": tipo_evento,
        "data_evento": data_evento,
    }
    return agendaController.criar_evento_agenda(
        pessoa_id, token, payload, midia_url=midia_url, midia_tipo=midia_tipo
    )


@router.put("/{id_agenda}")
async def atualizar_evento(
    id_agenda: int,
    titulo: str = Form(...),
    descricao: str = Form(...),
    tipo_evento: str = Form("Comunidade"),
    data_evento: str = Form(...),
    status: str = Form("ATIVO"),
    remover_midia: bool = Form(False),
    midia: Optional[UploadFile] = File(default=None),
    x_user_id: Optional[int] = Header(default=None, alias="X-User-ID"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
):
    token = _extrair_token(authorization)
    pessoa_id = x_user_id or 0
    agendaController.validar_admin(pessoa_id, token)

    nova_midia_url = None
    nova_midia_tipo = None
    if midia and midia.filename:
        nova_midia_url, nova_midia_tipo, _ = await store_media(midia, "agenda")

    payload = {
        "titulo": titulo,
        "descricao": descricao,
        "tipo_evento": tipo_evento,
        "data_evento": data_evento,
        "status": status,
    }
    return agendaController.atualizar_evento_agenda(
        id_agenda,
        pessoa_id,
        token,
        payload,
        nova_midia_url=nova_midia_url,
        nova_midia_tipo=nova_midia_tipo,
        remover_midia=remover_midia,
    )


@router.delete("/{id_agenda}")
async def excluir_evento(
    id_agenda: int,
    x_user_id: Optional[int] = Header(default=None, alias="X-User-ID"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
):
    token = _extrair_token(authorization)
    return agendaController.excluir_evento_agenda(id_agenda, x_user_id or 0, token)