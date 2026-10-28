
import os
from typing import Any
from dotenv import load_dotenv
from pathlib import Path
from fastapi import HTTPException
from app.modules.pessoas import pessoasModel as model
from app.core.validacao import cpf_cnpj_valido
from app.core.criptografa import hash_senha

from app.modules.user import userController

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

PESSOA_FIELDS = {
    "id_tipo_pessoa",
    "id_tipo_perfil",
    "senha",
    "nome_razao",
    "email",
    "cpf_cnpj",
    "ativo",
}


def _pessoa_data(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if key in PESSOA_FIELDS}


def get_pessoas(pessoa_id: int | None = None) -> list[dict[str, Any]]:
    return model.listar_pessoas(pessoa_id)


def get_tipos_perfil(tipos_perfil_id: int | None = None) -> list[dict[str, Any]]:
    return model.listar_tipos_perfil(tipos_perfil_id)

    
def post_pessoa(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("nome_razao"):
        raise HTTPException(
            status_code=400,
            detail="Campo Nome/Razão obrigatório.",
        )

    if not data.get("cpf_cnpj"):
        raise HTTPException(
            status_code=400,
            detail="Campo CPF/CNPJ obrigatório.",
        )
    else:
        data["cpf_cnpj"] = data.get("cpf_cnpj").replace(".", "").replace("-", "").replace("/", "")

    if not cpf_cnpj_valido(data.get("cpf_cnpj")):
        raise HTTPException(
            status_code=400,
            detail="Campo CPF/CNPJ esta invalido.",
        )

    if model.verifica_cpf_cnpj(data["cpf_cnpj"]):
        raise HTTPException(
            status_code=400,
            detail="CPF/CNPJ já cadastrado.",
        )
    
    if not data.get("email"):
        raise HTTPException(
            status_code=400,
            detail="Campo Email obrigatório.",
        )


    if not data.get("senha"):
        raise HTTPException(
            status_code=400,
            detail="Campo Senha obrigatório.",
        )
    
    if not data.get("confirmar_senha"):
        raise HTTPException(
            status_code=400,
            detail="Campo Confirmar Senha obrigatório.",
        )
    
    if data.get("senha") != data.get("confirmar_senha"):
        raise HTTPException(
            status_code=400,
            detail="As senhas não coincidem.",
        )

    data["senha"] = hash_senha(data.get("senha"))

    if len(data.get("cpf_cnpj")) == 11:
        data["id_tipo_pessoa"] = 1
    elif len(data.get("cpf_cnpj")) == 14:
        data["id_tipo_pessoa"] = 2
    else:
        raise HTTPException(
            status_code=400,
            detail="CPF deve ter 11 dígitos ou CNPJ 14 dígitos.",
        )

    pessoa_id = model.cadastrar_pessoa(_pessoa_data(data))
    return {
        "success": True,
        "message": "Pessoa cadastrada com sucesso.",
        "id_pessoa": pessoa_id,
    }

def update_pessoa(pessoa_id: int, data: dict[str, Any], token: str) -> dict[str, Any]:
    result = userController.autenticar(pessoa_id, token)
    if result.get('detail'):
        return result
    
    if not data.get("nome_razao"):
        raise HTTPException(
            status_code=400,
            detail="Campo Nome/Razão obrigatório.",
        )
    

    if not data.get("email"):
        raise HTTPException(
            status_code=400,
            detail="Campo Email obrigatório.",
        )
    
    
    if not data.get("senha"):
        raise HTTPException(
            status_code=400,
            detail="Campo Senha obrigatório.",
        )
        
    if not data.get("confirmar_senha"):
        raise HTTPException(
            status_code=400,
            detail="Campo Confirmar Senha obrigatório.",
        )
        
    if data.get("senha") != data.get("confirmar_senha"):
        raise HTTPException(
            status_code=400,
            detail="As senhas não coincidem.",
        )
    
    data["senha"] = hash_senha(data.get("senha"))
        
    if not model.atualizar_pessoa(pessoa_id, _pessoa_data(data)):
        raise HTTPException(
            status_code=404, 
            detail="Pessoa não encontrada."
        )
    
    return {
        "success": True, 
        "message": "Pessoa atualizada com sucesso."
    }


def delete_pessoa(pessoa_id: int) -> dict[str, Any]:
    if not model.deletar_pessoa(pessoa_id):
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")
    return {"success": True, "message": "Pessoa excluída com sucesso."}
