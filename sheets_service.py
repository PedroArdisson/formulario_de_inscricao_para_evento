import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
SECRET = os.getenv("SHEETS_SECRET")


def enviar_inscricao_para_planilha(dados):
    dados["secret"] = SECRET

    resposta = requests.post(
        APPS_SCRIPT_URL,
        json=dados,
        timeout=20,
        verify=False
    )

    resposta.raise_for_status()

    return resposta.json()