from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

def hash_senha(senha: str) -> str:
    ph = PasswordHasher()
    return ph.hash(senha)

def valida_senha(senha_digitada: str, senha_hash_do_banco: str) -> bool:
    ph = PasswordHasher()

    try:
        ph.verify(senha_hash_do_banco, senha_digitada)
        return True
    except (InvalidHashError, VerifyMismatchError):
        return False 

def hash_token(chave_secreta: str, chave_banco: str) -> str:
    ph = PasswordHasher()
    return ph.hash(chave_secreta + chave_banco)

def valida_token(chave_secreta: str, chave_banco: str, token: str) -> bool:
    ph = PasswordHasher()

    try:
        chave = chave_secreta + chave_banco
        ph.verify(token, chave)
        return True
    except (InvalidHashError, VerifyMismatchError):
        return False 