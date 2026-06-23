import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbym5Gpvhofrzh471HX---q2PH8Ul-TKtFMnJQNwp_aHxIEUQKiusAacgI1TtE9w-20/exec"
SECRET = "emeerj-2026-chave-teste"


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