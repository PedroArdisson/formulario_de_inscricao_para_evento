import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()


MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

VERIFY_SSL = (
    os.getenv("VERIFY_SSL", "true").lower()
    == "true"
)


if not MP_ACCESS_TOKEN:
    raise RuntimeError(
        "MP_ACCESS_TOKEN não encontrado no .env."
    )


resposta = requests.get(
    "https://api.mercadopago.com/v1/payment_methods",
    headers={
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
    },
    timeout=20,
    verify=VERIFY_SSL
)

resposta.raise_for_status()

metodos = resposta.json()


pix_encontrado = False

for metodo in metodos:
    id_metodo = str(
        metodo.get("id", "")
    ).lower()

    nome_metodo = str(
        metodo.get("name", "")
    ).lower()

    if "pix" in id_metodo or "pix" in nome_metodo:
        pix_encontrado = True

        print("\nPIX ENCONTRADO:")
        print(
            json.dumps(
                metodo,
                indent=2,
                ensure_ascii=False
            )
        )


if not pix_encontrado:
    print(
        "\nPIX NÃO FOI RETORNADO "
        "PARA ESTE ACCESS TOKEN."
    )