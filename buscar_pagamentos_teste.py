import os

import requests
from dotenv import load_dotenv


load_dotenv()


MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
VERIFY_SSL = os.getenv(
    "VERIFY_SSL",
    "true"
).lower() == "true"


if not MP_ACCESS_TOKEN:
    raise RuntimeError(
        "MP_ACCESS_TOKEN não configurado no .env."
    )


# IDs das inscrições que apareceram nos seus últimos logs.
ids_inscricoes = ["7"]


for id_inscricao in ids_inscricoes:
    print()
    print("=" * 50)
    print(f"Buscando pagamento da inscrição {id_inscricao}")
    print("=" * 50)

    resposta = requests.get(
        "https://api.mercadopago.com/v1/payments/search",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
        },
        params={
            "external_reference": id_inscricao,
            "sort": "id",
            "criteria": "desc",
            "limit": 10
        },
        timeout=20,
        verify=VERIFY_SSL
    )

    if not resposta.ok:
        print(
            "Erro:",
            resposta.status_code,
            resposta.text
        )
        continue

    dados = resposta.json()
    pagamentos = dados.get("results", [])

    if not pagamentos:
        print("Nenhum pagamento encontrado.")
        continue

    for pagamento in pagamentos:
        print()
        print("PAYMENT ID:", pagamento.get("id"))
        print("Status:", pagamento.get("status"))
        print(
            "Detalhe:",
            pagamento.get("status_detail")
        )
        print(
            "External reference:",
            pagamento.get("external_reference")
        )
        print(
            "Valor:",
            pagamento.get("transaction_amount")
        )
        print(
            "Data:",
            pagamento.get("date_created")
        )