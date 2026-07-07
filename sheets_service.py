import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
SECRET = os.getenv("SHEETS_SECRET")

# ATENÇÃO:
# VERIFY_SSL=false é usado apenas em desenvolvimento local por causa de erro SSL no Windows.
# Em produção, usar obrigatoriamente:
# APP_ENV=production
# VERIFY_SSL=true

APP_ENV = os.getenv("APP_ENV", "development")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"


# Segurança: nunca permitir produção com SSL desligado
if APP_ENV == "production" and VERIFY_SSL is False:
    raise RuntimeError(
        "Configuração insegura: VERIFY_SSL=false não pode ser usado em produção."
    )


# Apenas no ambiente local, enquanto seu Python está com problema de certificado
if VERIFY_SSL is False:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def enviar_inscricao_para_planilha(dados):
    dados["secret"] = SECRET

    resposta = requests.post(
        APPS_SCRIPT_URL,
        json=dados,
        timeout=20,
        verify=VERIFY_SSL
    )

    resposta.raise_for_status()

    return resposta.json()

def atualizar_pagamento_na_planilha(
    id_inscricao,
    status_pagamento,
    payment_id,
    payment_status_detail,
    data_pagamento
):
    """
    Atualiza os dados de pagamento de uma inscrição
    já existente no Google Sheets.
    """

    dados = {
        "secret": SECRET,
        "acao": "atualizar_pagamento",
        "id": id_inscricao,
        "status_pagamento": status_pagamento,
        "payment_id": payment_id,
        "payment_status_detail": payment_status_detail,
        "data_pagamento": data_pagamento
    }

    resposta = requests.post(
        APPS_SCRIPT_URL,
        json=dados,
        timeout=20,
        verify=VERIFY_SSL
    )

    resposta.raise_for_status()

    resultado = resposta.json()

    if not resultado.get("ok"):
        raise RuntimeError(
            "Erro ao atualizar Google Sheets: "
            f"{resultado}"
        )

    return resultado