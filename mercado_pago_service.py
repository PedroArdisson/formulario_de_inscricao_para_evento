import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:5000")

APP_ENV = os.getenv("APP_ENV", "development")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"


# Impede produção com SSL desativado
if APP_ENV == "production" and VERIFY_SSL is False:
    raise RuntimeError(
        "Configuração insegura: VERIFY_SSL=false não pode ser usado em produção."
    )


# Apenas para seu ambiente local atual
if VERIFY_SSL is False:
    urllib3.disable_warnings(
        urllib3.exceptions.InsecureRequestWarning
    )


def criar_preferencia_pagamento(
    id_inscricao,
    nome_completo,
    email,
    valor_inscricao
):
    if not MP_ACCESS_TOKEN:
        raise RuntimeError(
            "MP_ACCESS_TOKEN não configurado no arquivo .env"
        )

    # ==============================
    # ITENS DO PAGAMENTO
    # ==============================

    # O Checkout cobra apenas a inscrição.
    # O interesse na camisa é somente uma pesquisa
    # e não faz parte do pagamento.
    itens = [
        {
            "title": "Inscrição EMEERJ 2026",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(valor_inscricao)
        }
    ]


    # ==============================
    # DADOS DA PREFERÊNCIA
    # ==============================

    dados = {
        "items": itens,

        "payer": {
            "name": nome_completo,
            "email": email
        },

        # Liga o pagamento à inscrição no SQLite
        "external_reference": str(id_inscricao)
    }


    # URLs de retorno somente quando o site tiver HTTPS
    if SITE_URL.startswith("https://"):
        dados["back_urls"] = {
            "success": f"{SITE_URL}/pagamento/sucesso",
            "failure": f"{SITE_URL}/pagamento/falha",
            "pending": f"{SITE_URL}/pagamento/pendente"
        }

        dados["auto_return"] = "approved"


    # ==============================
    # REQUISIÇÃO AO MERCADO PAGO
    # ==============================

    resposta = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json=dados,
        timeout=20,
        verify=VERIFY_SSL
    )


    # Mostra a resposta completa caso dê erro
    if not resposta.ok:
        print("\n--- ERRO MERCADO PAGO ---")
        print("Status:", resposta.status_code)
        print("Resposta:", resposta.text)
        print("---------------------------\n")

    resposta.raise_for_status()


    # ==============================
    # LINK DO CHECKOUT
    # ==============================

    resposta_json = resposta.json()

    link_pagamento = resposta_json.get("init_point")

    if not link_pagamento:
        raise RuntimeError(
            "Mercado Pago não retornou o link de pagamento."
        )

    print("\n--- MERCADO PAGO ---")
    print("Preferência:", resposta_json.get("id"))
    print("Link do checkout:", link_pagamento)
    print("--------------------\n")


    return {
        "id_preferencia": resposta_json.get("id"),
        "link_pagamento": link_pagamento
    }
    
    
def criar_pagamento_pix(
    id_inscricao,
    email,
    cpf,
    valor_inscricao,
    idempotency_key
):
    """
    Cria uma cobrança Pix diretamente pela API
    do Mercado Pago.

    Retorna os dados necessários para mostrar:
    - QR Code
    - Pix Copia e Cola
    - status do pagamento
    """

    if not MP_ACCESS_TOKEN:
        raise RuntimeError(
            "MP_ACCESS_TOKEN não configurado."
        )

    dados = {
        "transaction_amount": float(
            valor_inscricao
        ),

        "description": "Inscrição EMEERJ 2026",

        "payment_method_id": "pix",

        # Liga o pagamento à inscrição no SQLite.
        "external_reference": str(
            id_inscricao
        ),

        "payer": {
            "email": email,

            "identification": {
                "type": "CPF",
                "number": cpf
            }
        }
    }


    resposta = requests.post(
        "https://api.mercadopago.com/v1/payments",

        headers={
            "Authorization":
                f"Bearer {MP_ACCESS_TOKEN}",

            "Content-Type":
                "application/json",

            "X-Idempotency-Key":
                idempotency_key
        },

        json=dados,

        timeout=20,

        verify=VERIFY_SSL
    )


    if not resposta.ok:
        print("\n--- ERRO AO CRIAR PIX ---")
        print("Status:", resposta.status_code)
        print("Resposta:", resposta.text)
        print("--------------------------\n")


    resposta.raise_for_status()


    pagamento = resposta.json()


    # ==============================
    # DADOS DO PIX
    # ==============================

    ponto_interacao = (
        pagamento.get(
            "point_of_interaction"
        )
        or {}
    )

    dados_transacao = (
        ponto_interacao.get(
            "transaction_data"
        )
        or {}
    )

    qr_code = dados_transacao.get(
        "qr_code"
    )

    qr_code_base64 = dados_transacao.get(
        "qr_code_base64"
    )

    ticket_url = dados_transacao.get(
        "ticket_url"
    )


    if not qr_code or not qr_code_base64:
        raise RuntimeError(
            "Mercado Pago criou o pagamento, "
            "mas não retornou os dados do Pix."
        )


    print("\n--- PIX CRIADO ---")
    print("Payment ID:", pagamento.get("id"))
    print("Status:", pagamento.get("status"))
    print(
        "Inscrição:",
        pagamento.get("external_reference")
    )
    print("------------------\n")


    return {
        "payment_id": pagamento.get("id"),

        "status": pagamento.get("status"),

        "status_detail": pagamento.get(
            "status_detail"
        ),

        "qr_code": qr_code,

        "qr_code_base64": qr_code_base64,

        "ticket_url": ticket_url
    }
    
    
def consultar_pagamento(payment_id):
    """
    Consulta o pagamento diretamente na API do Mercado Pago.

    O webhook apenas avisa que algo mudou.
    A informação confiável sobre o pagamento vem desta consulta.
    """

    if not MP_ACCESS_TOKEN:
        raise RuntimeError(
            "MP_ACCESS_TOKEN não configurado."
        )

    resposta = requests.get(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers={
            "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        timeout=15,
        verify=VERIFY_SSL
    )

    if not resposta.ok:
        print(
            "Erro ao consultar pagamento:",
            resposta.status_code,
            resposta.text
        )

    resposta.raise_for_status()

    return resposta.json()