
import os
from datetime import datetime
from flask.cli import load_dotenv
from app.modules.user import userModel as model
from typing import Any
from fastapi import HTTPException
from pathlib import Path
from app.core.criptografa import valida_token, hash_token, valida_senha


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

def autenticar(pessoa_id:int, token:str) -> dict[str, Any]:
    result = model.listar_login({"id_pessoa": pessoa_id})

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Pessoa não encontrada."
        )
    
    if not valida_token(os.getenv("LOGIN_SECRET_KEY", ""), result[0].get("chave"), token):
        raise HTTPException(
            status_code=400,
            detail="Token inválido."
        )
    
    return {}
    
def post_autenticacao(pessoa_id:int, token:str) -> dict[str, Any]:
    result = autenticar(pessoa_id, token)
    if result.get('detail'):
        return result
    
    return {
        "success" : True, 
        "message": "usuario autenticado."
    }

def post_login(data: dict[str, Any]) -> dict[str, Any]:
    momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result_rate_limit = model.listar_rate_limits_excedidos(5)
    if result_rate_limit:
        model.cadastrar_rate_limit("LOGIN", momento, data.get("email"))
        raise HTTPException(
            status_code=404,
            detail="Numeros de tentativcas excedidos, tente novamente após 10 minutos."
        )
    
    result = model.listar_login({'email': data.get("email")})
    if not result:
        model.cadastrar_rate_limit("LOGIN", momento, data.get("email"))
        raise HTTPException(
            status_code=404,
            detail="E-mail não encontrado ou não existe em nosso cadastro."
        )
    
    if not valida_senha(data.get("senha"), result[0].get("senha")):
        model.cadastrar_rate_limit("LOGIN", momento, data.get("email"))
        raise HTTPException(
            status_code=400,
            detail="Senha incorreta."
        )

    token = hash_token(os.getenv("LOGIN_SECRET_KEY", ""), result[0].get("chave"))

    return {
        "success" : True, 
        "message": "Seja bem-vindo A Rede Atipic.",
        "token": token,
        "id_pessoa": result[0].get("id_pessoa"),
        "nome_razao": result[0].get("nome_razao")
    }
