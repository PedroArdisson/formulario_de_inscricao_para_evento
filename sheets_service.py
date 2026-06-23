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