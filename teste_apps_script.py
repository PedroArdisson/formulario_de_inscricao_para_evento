import os

import requests
from dotenv import load_dotenv


load_dotenv()

APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
SHEETS_SECRET = os.getenv("SHEETS_SECRET")


url = "https://script.google.com/macros/s/AKfycbym5Gpvhofrzh471HX---q2PH8Ul-TKtFMnJQNwp_aHxIEUQKiusAacgI1TtE9w-20/exec"

dados_teste = {
    "secret": SHEETS_SECRET,
    "id": 999,
    "data_inscricao": "23/06/2026 14:00:00",
    "nome_completo": "Teste Google Sheets",
    "email": "teste@email.com",
    "nome_social": "Teste",
    "idade": 21,
    "genero": "Masculino CIS",
    "casa_espirita": "Casa Teste",
    "ceu": "2º - Nilópolis",
    "outro_ceu": "",
    "telefone": "21999999999",
    "alimentacao": "Comum",
    "possui_alergia": "Não",
    "qual_alergia": "",
    "usa_medicamento": "Não",
    "qual_medicamento": "",
    "possui_convenio": "Não",
    "qual_convenio": "",
    "contato_emergencia_nome": "Contato Teste",
    "contato_emergencia_telefone": "21988888888",
    "participou_emeerj": "Não",
    "possui_deficiencia": "Não",
    "qual_deficiencia": "",
    "tipo_participacao": "Confraternista",
    "area_trabalho": "",
    "quer_camisa": "Não",
    "tamanho_camisa": "",
    "valor_inscricao": 25,
    "valor_camisa": 0,
    "valor_total": 25,
    "status_pagamento": "PENDENTE"
}

try:
    resposta = requests.post(
        url,
        json=dados_teste,
        timeout=20,
        verify=False
    )

    print("Status:", resposta.status_code)
    print("Resposta:")
    print(resposta.text)

except Exception as erro:
    print("Erro:")
    print(erro)