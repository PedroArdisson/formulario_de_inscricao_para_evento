import re


def normalizar_cpf(cpf):
    """
    Remove pontos, traço, espaços e qualquer caractere
    que não seja número.
    """

    return re.sub(r"\D", "", cpf or "")


def cpf_valido(cpf):
    """
    Valida os 11 dígitos e os dois dígitos verificadores.
    """

    cpf = normalizar_cpf(cpf)

    if len(cpf) != 11:
        return False

    # Rejeita CPFs como:
    # 000.000.000-00
    # 111.111.111-11
    # etc.
    if len(set(cpf)) == 1:
        return False

    numeros = [int(digito) for digito in cpf]

    # Primeiro dígito verificador
    soma = sum(
        numeros[i] * (10 - i)
        for i in range(9)
    )

    resultado = (soma * 10) % 11

    if resultado == 10:
        resultado = 0

    if resultado != numeros[9]:
        return False

    # Segundo dígito verificador
    soma = sum(
        numeros[i] * (11 - i)
        for i in range(10)
    )

    resultado = (soma * 10) % 11

    if resultado == 10:
        resultado = 0

    return resultado == numeros[10]


def mascarar_cpf(cpf):
    """
    Retorna:
    ***.456.789-**
    """

    cpf = normalizar_cpf(cpf)

    if len(cpf) != 11:
        return ""

    return (
        f"***.{cpf[3:6]}."
        f"{cpf[6:9]}-**"
    )