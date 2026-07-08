import getpass
import json

import requests


# O token é digitado sem aparecer na tela
access_token = getpass.getpass(
    "Cole o Access Token de PRODUÇÃO: "
).strip()


if not access_token:
    raise RuntimeError(
        "Nenhum Access Token foi informado."
    )


resposta = requests.get(
    "https://api.mercadopago.com/v1/payment_methods",
    headers={
        "Authorization": f"Bearer {access_token}"
    },
    timeout=20
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

        print("\nPIX ENCONTRADO NA PRODUÇÃO:")

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
        "PARA A CREDENCIAL DE PRODUÇÃO."
    )