import re


def cpf_valido(valor: str) -> bool:
    cpf = re.sub(r"\D", "", valor)

    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    digitos = [int(numero) for numero in cpf]

    soma = sum(numero * peso for numero, peso in zip(digitos[:9], range(10, 1, -1)))
    primeiro = (soma * 10) % 11
    if primeiro == 10:
        primeiro = 0

    soma = sum(
        numero * peso
        for numero, peso in zip(digitos[:9] + [primeiro], range(11, 1, -1))
    )
    segundo = (soma * 10) % 11
    if segundo == 10:
        segundo = 0

    return digitos[9] == primeiro and digitos[10] == segundo


def cnpj_valido(valor: str) -> bool:
    cnpj = re.sub(r"[^0-9A-Z]", "", valor.upper())

    if (
        len(cnpj) != 14
        or not re.fullmatch(r"[A-Z0-9]{12}\d{2}", cnpj)
        or len(set(cnpj)) == 1
    ):
        return False

    valores = [ord(caractere) - 48 for caractere in cnpj]
    pesos_primeiro = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    soma = sum(
        valor * peso for valor, peso in zip(valores[:12], pesos_primeiro)
    )
    resto = soma % 11
    primeiro = 0 if resto < 2 else 11 - resto

    pesos_segundo = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    soma = sum(
        valor * peso
        for valor, peso in zip(valores[:12] + [primeiro], pesos_segundo)
    )
    resto = soma % 11
    segundo = 0 if resto < 2 else 11 - resto

    return valores[12] == primeiro and valores[13] == segundo


def cpf_cnpj_valido(valor: str) -> bool:
    documento = re.sub(r"[^0-9A-Z]", "", valor.upper())

    if len(documento) == 11 and documento.isdigit():
        return cpf_valido(documento)
    if len(documento) == 14:
        return cnpj_valido(documento)
    return False
