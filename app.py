import os
from decimal import Decimal
from datetime import datetime

from uuid import uuid4

from validacoes import (
    normalizar_cpf,
    cpf_valido,
    mascarar_cpf
)

from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv

from mercadopago.webhook import (
    WebhookSignatureValidator,
    InvalidWebhookSignatureError
)

from mercado_pago_service import (
    criar_pagamento_pix,
    consultar_pagamento
)

from sheets_service import (
    enviar_inscricao_para_planilha,
    atualizar_pagamento_na_planilha
)
from database import conectar_banco, inicializar_banco


load_dotenv()

app = Flask(__name__)

inicializar_banco()

VALOR_INSCRICAO = 25

def extrair_dados_pix(pagamento):
    """
    Extrai o QR Code e o Pix Copia e Cola
    de um pagamento consultado no Mercado Pago.
    """

    ponto_interacao = (
        pagamento.get("point_of_interaction")
        or {}
    )

    dados_transacao = (
        ponto_interacao.get("transaction_data")
        or {}
    )

    return {
        "qr_code": dados_transacao.get("qr_code"),

        "qr_code_base64": dados_transacao.get(
            "qr_code_base64"
        )
    }


@app.route("/")
def pagina_inicial():
    return render_template("index.html")


@app.route("/inscricao", methods=["POST"])
def receber_inscricao():
    # Dados básicos
    nome_completo = request.form.get("nome_completo")
    email = request.form.get("email")
    cpf = normalizar_cpf(request.form.get("cpf", ""))
    if not cpf_valido(cpf):
        return (
            "CPF inválido. "
            "Volte e informe um CPF válido.",
            400
        )

    # =====================================
    # VERIFICAR INSCRIÇÃO JÁ EXISTENTE
    # =====================================

    with conectar_banco() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                nome_social,
                email,
                status_pagamento,
                link_pagamento
            FROM inscricoes
            WHERE cpf = ?
            """,
            (cpf,)
        )

        inscricao_existente = cursor.fetchone()

    if inscricao_existente:
        (
            nome_social_existente,
            email_existente,
            status_existente,
            link_pagamento_existente
        ) = inscricao_existente

        email_informado = email.strip().lower()

        email_cadastrado = (
            email_existente
            .strip()
            .lower()
        )

        # O CPF existe, mas o e-mail não corresponde.
        if email_informado != email_cadastrado:
            return render_template(
                "inscricao_existente.html",
                erro=(
                    "Já existe uma inscrição vinculada "
                    "a este CPF, mas o e-mail informado "
                    "não corresponde ao e-mail cadastrado."
                )
            ), 409

        # CPF e e-mail correspondem.
        return render_template(
            "inscricao_existente.html",
            erro=None,
            nome_social=nome_social_existente,
            status_pagamento=status_existente,
            cpf=cpf,
            email=email_existente
        )
    nome_social = request.form.get("nome_social")
    idade = request.form.get("idade")
    genero = request.form.get("genero")

    # Casa espírita e CEU
    casa_espirita = request.form.get("casa_espirita")
    ceu = request.form.get("ceu")
    outro_ceu = request.form.get("outro_ceu")

    # Contato
    telefone = request.form.get("telefone")

    # Alimentação pode ter mais de uma opção marcada
    alimentacao_lista = request.form.getlist("alimentacao")
    alimentacao = ", ".join(alimentacao_lista)

    # Saúde
    possui_alergia = request.form.get("possui_alergia")
    qual_alergia = request.form.get("qual_alergia")

    usa_medicamento = request.form.get("usa_medicamento")
    qual_medicamento = request.form.get("qual_medicamento")

    possui_convenio = request.form.get("possui_convenio")
    qual_convenio = request.form.get("qual_convenio")

    contato_emergencia_nome = request.form.get("contato_emergencia_nome")
    contato_emergencia_telefone = request.form.get("contato_emergencia_telefone")

    participou_emeerj = request.form.get("participou_emeerj")

    possui_deficiencia = request.form.get("possui_deficiencia")
    qual_deficiencia = request.form.get("qual_deficiencia")

    # Participação
    tipo_participacao = request.form.get("tipo_participacao")
    area_trabalho = request.form.get("area_trabalho")

    # Interesse na camisa
    quer_camisa = request.form.get("quer_camisa")
    tamanho_camisa = request.form.get("tamanho_camisa")

    # A camisa é apenas uma pesquisa de interesse.
    # Ela não é vendida nem cobrada neste formulário.
    if quer_camisa != "Sim":
        tamanho_camisa = None

    valor_camisa = 0
    valor_total = VALOR_INSCRICAO
    
    status_pagamento = "PENDENTE"

    data_inscricao = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    
    # Termo LGPD
    termo_lgpd = request.form.get("termo_lgpd")

    # Salva no SQLite
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inscricoes (
            nome_completo,
            email,
            cpf,
            nome_social,
            idade,
            genero,

            casa_espirita,
            ceu,
            outro_ceu,

            telefone,
            alimentacao,

            possui_alergia,
            qual_alergia,

            usa_medicamento,
            qual_medicamento,

            possui_convenio,
            qual_convenio,

            contato_emergencia_nome,
            contato_emergencia_telefone,

            participou_emeerj,

            possui_deficiencia,
            qual_deficiencia,

            tipo_participacao,
            area_trabalho,

            quer_camisa,
            tamanho_camisa,

            valor_inscricao,
            valor_camisa,
            valor_total,

            status_pagamento,
            termo_lgpd,
            data_inscricao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome_completo,
        email,
        cpf,
        nome_social,
        idade,
        genero,

        casa_espirita,
        ceu,
        outro_ceu,

        telefone,
        alimentacao,

        possui_alergia,
        qual_alergia,

        usa_medicamento,
        qual_medicamento,

        possui_convenio,
        qual_convenio,

        contato_emergencia_nome,
        contato_emergencia_telefone,

        participou_emeerj,

        possui_deficiencia,
        qual_deficiencia,

        tipo_participacao,
        area_trabalho,

        quer_camisa,
        tamanho_camisa,

        VALOR_INSCRICAO,
        valor_camisa,
        valor_total,

        status_pagamento,
        termo_lgpd,
        data_inscricao
    ))

    id_inscricao = cursor.lastrowid

    conn.commit()
    conn.close()

    # Dados que serão enviados para o Google Sheets
    dados_planilha = {
        "id": id_inscricao,
        "data_inscricao": data_inscricao,
        "nome_completo": nome_completo,
        "email": email,
        "cpf_mascarado": mascarar_cpf(cpf),
        "nome_social": nome_social,
        "idade": idade,
        "genero": genero,
        "casa_espirita": casa_espirita,
        "ceu": ceu,
        "outro_ceu": outro_ceu,
        "telefone": telefone,
        "alimentacao": alimentacao,
        "possui_alergia": possui_alergia,
        "qual_alergia": qual_alergia,
        "usa_medicamento": usa_medicamento,
        "qual_medicamento": qual_medicamento,
        "possui_convenio": possui_convenio,
        "qual_convenio": qual_convenio,
        "contato_emergencia_nome": contato_emergencia_nome,
        "contato_emergencia_telefone": contato_emergencia_telefone,
        "participou_emeerj": participou_emeerj,
        "possui_deficiencia": possui_deficiencia,
        "qual_deficiencia": qual_deficiencia,
        "tipo_participacao": tipo_participacao,
        "area_trabalho": area_trabalho,
        "quer_camisa": quer_camisa,
        "tamanho_camisa": tamanho_camisa,
        "valor_inscricao": VALOR_INSCRICAO,
        "valor_camisa": valor_camisa,
        "valor_total": valor_total,
        "status_pagamento": status_pagamento,
        "termo_lgpd": termo_lgpd
    }

    try:
        resposta_planilha = enviar_inscricao_para_planilha(dados_planilha)
        print("Enviado para Google Sheets:")
        print(resposta_planilha)
    except Exception as erro:
        print("Erro ao enviar para Google Sheets:")
        print(erro)

    print("\n--- INSCRIÇÃO SALVA NO BANCO ---")
    print(f"ID: {id_inscricao}")
    print(f"Nome: {nome_completo}")
    print(f"E-mail: {email}")
    print(f"Valor total: R$ {valor_total}")
    print("--------------------------------\n")

    try:
        # A primeira tentativa de Pix usa uma chave
        # fixa ligada ao ID da inscrição.
        idempotency_key = (
            f"emeerj-{id_inscricao}-pix-inicial"
        )

        pagamento = criar_pagamento_pix(
            id_inscricao=id_inscricao,
            email=email,
            cpf=cpf,
            valor_inscricao=VALOR_INSCRICAO,
            idempotency_key=idempotency_key
        )

        payment_id = str(
            pagamento["payment_id"]
        )

        # Salva os dados principais do Pix.
        with conectar_banco() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE inscricoes
                SET
                    payment_id = ?,
                    payment_status_detail = ?,
                    status_pagamento = ?
                WHERE id = ?
                """,
                (
                    payment_id,
                    pagamento["status_detail"],
                    "PENDENTE",
                    id_inscricao
                )
            )

            conn.commit()

        return render_template(
            "pagamento_pix.html",

            nome_social=nome_social,

            valor_total=(
                f"{VALOR_INSCRICAO:.2f}"
                .replace(".", ",")
            ),

            payment_id=payment_id,

            qr_code=pagamento["qr_code"],

            qr_code_base64=(
                pagamento["qr_code_base64"]
            )
        )

    except Exception as erro:
        print(
            "Erro ao criar pagamento Pix:",
            repr(erro)
        )

        return render_template(
            "inscricao_existente.html",
            erro=(
                "Sua inscrição foi salva, mas não "
                "foi possível gerar o Pix agora. "
                "Use a opção de consultar inscrição "
                "para tentar novamente."
            )
        ), 500

    except Exception as erro:
        print("Erro ao criar pagamento no Mercado Pago:")
        print(erro)

    valor_total_formatado = f"{valor_total:.2f}".replace(".", ",")

    return render_template(
        "sucesso.html",
        nome_social=nome_social,
        valor_total=valor_total_formatado,
        status_pagamento="PENDENTE - ERRO AO GERAR PAGAMENTO"
    )


def exibir_resultado_pagamento(status_padrao):
    """
    Monta a página exibida depois que o usuário
    volta do Mercado Pago.

    Quando existe um payment_id, consulta o pagamento
    diretamente na API do Mercado Pago.
    """

    payment_id = (
        request.args.get("payment_id")
        or request.args.get("collection_id")
    )

    external_reference = request.args.get(
        "external_reference"
    )

    status_local = status_padrao

    # Se o Mercado Pago enviou um payment_id,
    # consultamos o pagamento real na API.
    if payment_id:
        try:
            pagamento = consultar_pagamento(
                payment_id
            )

            status_mp = pagamento.get("status")

            external_reference = pagamento.get(
                "external_reference"
            )

            mapa_status = {
                "approved": "APROVADO",
                "pending": "PENDENTE",
                "in_process": "PENDENTE",
                "authorized": "PENDENTE",
                "rejected": "PENDENTE",
                "cancelled": "PENDENTE",
                "canceled": "PENDENTE",
                "expired": "PENDENTE",
                "refunded": "PENDENTE",
                "charged_back": "PENDENTE"
            }

            status_local = mapa_status.get(
                status_mp,
                str(status_mp).upper()
            )

        except Exception as erro:
            print(
                "Erro ao consultar pagamento "
                "na página de retorno:",
                repr(erro)
            )

    nome_social = "Participante"
    valor_total = None

    # Busca os dados da inscrição no SQLite.
    if external_reference:
        try:
            id_inscricao = int(
                external_reference
            )

            with conectar_banco() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT
                        nome_social,
                        valor_total,
                        status_pagamento
                    FROM inscricoes
                    WHERE id = ?
                    """,
                    (id_inscricao,)
                )

                inscricao = cursor.fetchone()

            if inscricao:
                nome_social = inscricao[0]

                valor_total = (
                    f"{inscricao[1]:.2f}"
                    .replace(".", ",")
                )

                status_banco = inscricao[2]

                # Se não veio payment_id válido do Mercado Pago,
                # o site deve confiar no status salvo no banco.
                if not payment_id:
                    status_local = status_banco

        except (TypeError, ValueError):
            print(
                "external_reference inválida:",
                external_reference
            )

    return render_template(
        "sucesso.html",
        nome_social=nome_social,
        status_pagamento=status_local,
        valor_total=valor_total
    )

@app.route("/pagamento/sucesso")
def pagamento_sucesso():
    return exibir_resultado_pagamento(
        "PENDENTE"
    )

@app.route("/pagamento/falha")
def pagamento_falha():
    return exibir_resultado_pagamento(
        "RECUSADO"
    )

@app.route("/pagamento/pendente")
def pagamento_pendente():
    return exibir_resultado_pagamento(
        "PENDENTE"
    )

# ==============================
# WEBHOOK MERCADO PAGO
# ==============================

@app.route("/webhook/mercadopago", methods=["POST"])
def webhook_mercado_pago():
    """
    Recebe notificações de pagamento do Mercado Pago.

    Fluxo:
    1. Valida a assinatura do webhook.
    2. Consulta o pagamento na API oficial.
    3. Localiza a inscrição pela external_reference.
    4. Confere o valor do pagamento.
    5. Atualiza o SQLite.
    """

    webhook_secret = os.getenv("MP_WEBHOOK_SECRET")

    if not webhook_secret:
        print("ERRO: MP_WEBHOOK_SECRET não configurado.")
        return "", 500

    # Dados usados para validar a assinatura
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")
    data_id = request.args.get("data.id")

    if not x_signature or not x_request_id or not data_id:
        print("Webhook recebido sem dados de assinatura completos.")
        return "", 400

    # ==============================
    # 1. VALIDAR ASSINATURA
    # ==============================

    try:
        WebhookSignatureValidator.validate(
            x_signature,
            x_request_id,
            data_id,
            webhook_secret
        )

    except InvalidWebhookSignatureError:
        print("Webhook rejeitado: assinatura inválida.")
        return "", 401

    # ==============================
    # 2. LER TIPO DA NOTIFICAÇÃO
    # ==============================

    dados = request.get_json(silent=True) or {}

    tipo = (
        request.args.get("type")
        or dados.get("type")
    )

    if tipo != "payment":
        print(f"Notificação ignorada. Tipo: {tipo}")
        return "", 200

    payment_id = str(data_id)

    try:
        # ==============================
        # 3. CONSULTAR PAGAMENTO REAL
        # ==============================

        pagamento = consultar_pagamento(payment_id)

        status_mp = pagamento.get("status")
        status_detail = pagamento.get("status_detail")
        external_reference = pagamento.get("external_reference")
        data_aprovacao = pagamento.get("date_approved")
        valor_pago = pagamento.get("transaction_amount")

        print(
            f"Pagamento consultado: "
            f"id={payment_id}, "
            f"status={status_mp}, "
            f"inscricao={external_reference}"
        )

        # ==============================
        # 4. VALIDAR INSCRIÇÃO
        # ==============================

        if not external_reference:
            print(
                "Pagamento sem external_reference. "
                "Notificação ignorada."
            )
            return "", 200

        try:
            id_inscricao = int(external_reference)

        except (TypeError, ValueError):
            print(
                "external_reference inválida:",
                external_reference
            )
            return "", 200

        # ==============================
        # 5. LOCALIZAR NO BANCO
        # ==============================

        with conectar_banco() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT valor_total
                FROM inscricoes
                WHERE id = ?
                """,
                (id_inscricao,)
            )

            inscricao = cursor.fetchone()

            if not inscricao:
                print(
                    f"Inscrição {id_inscricao} "
                    "não encontrada."
                )
                return "", 200

            # ==============================
            # 6. CONFERIR O VALOR
            # ==============================

            valor_esperado = Decimal(
                str(inscricao[0])
            ).quantize(
                Decimal("0.01")
            )

            valor_recebido = Decimal(
                str(valor_pago)
            ).quantize(
                Decimal("0.01")
            )

            if valor_recebido != valor_esperado:
                print(
                    "ATENÇÃO: valor divergente.",
                    f"Esperado={valor_esperado}",
                    f"Recebido={valor_recebido}"
                )
                return "", 200

            # ==============================
            # 7. TRADUZIR STATUS
            # ==============================

            mapa_status = {
                "approved": "APROVADO",
                "pending": "PENDENTE",
                "in_process": "PENDENTE",
                "authorized": "PENDENTE",
                "rejected": "PENDENTE",
                "cancelled": "PENDENTE",
                "canceled": "PENDENTE",
                "expired": "PENDENTE",
                "refunded": "PENDENTE",
                "charged_back": "PENDENTE"
            }

            status_local = mapa_status.get(
                status_mp,
                str(status_mp).upper()
            )

            # ==============================
            # 8. ATUALIZAR INSCRIÇÃO
            # ==============================

            cursor.execute(
                """
                UPDATE inscricoes
                SET
                    status_pagamento = ?,
                    payment_id = ?,
                    payment_status_detail = ?,
                    data_pagamento = COALESCE(
                        ?,
                        data_pagamento
                    )
                WHERE id = ?
                """,
                (
                    status_local,
                    payment_id,
                    status_detail,
                    data_aprovacao,
                    id_inscricao
                )
            )

            conn.commit()

            print(
            f"Inscrição {id_inscricao} atualizada: "
            f"{status_local}"
        )

        resultado_planilha = (
            atualizar_pagamento_na_planilha(
                id_inscricao=id_inscricao,
                status_pagamento=status_local,
                payment_id=payment_id,
                payment_status_detail=status_detail,
                data_pagamento=data_aprovacao
            )
        )

        print(
            "Pagamento atualizado no Google Sheets:",
            resultado_planilha
        )

        return "", 200

    except Exception as erro:
        print(
            "ERRO AO PROCESSAR WEBHOOK:",
            repr(erro)
        )

        return "", 500
    
      # ==============================
      # 8. CONTINUA PAGAMENTO
      # ==============================
    
@app.route(
    "/continuar-pagamento",
    methods=["POST"]
)
def continuar_pagamento():

    cpf = normalizar_cpf(
        request.form.get("cpf", "")
    )

    email = (
        request.form.get("email", "")
        .strip()
        .lower()
    )

    if not cpf or not email:
        return render_template(
            "inscricao_existente.html",
            erro=(
                "Não foi possível identificar "
                "sua inscrição."
            )
        ), 400

    with conectar_banco() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome_completo,
                nome_social,
                email,
                status_pagamento,
                payment_id
            FROM inscricoes
            WHERE cpf = ?
            """,
            (cpf,)
        )

        inscricao = cursor.fetchone()

    if not inscricao:
        return render_template(
            "inscricao_existente.html",
            erro="Inscrição não encontrada."
        ), 404

    (
        id_inscricao,
        nome_completo,
        nome_social,
        email_cadastrado,
        status_pagamento,
        payment_id
    ) = inscricao

    if (
        email
        != email_cadastrado.strip().lower()
    ):
        return render_template(
            "inscricao_existente.html",
            erro=(
                "Os dados informados não "
                "correspondem a uma inscrição."
            )
        ), 403

    if status_pagamento == "APROVADO":
        return render_template(
            "inscricao_existente.html",
            erro=None,
            nome_social=nome_social,
            status_pagamento="APROVADO",
            cpf=cpf,
            email=email_cadastrado
        )
        
    # Garante que inscrições pendentes antigas
    # também usem o valor único atual de R$ 25.
    with conectar_banco() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE inscricoes
            SET
                valor_inscricao = ?,
                valor_camisa = 0,
                valor_total = ?
            WHERE id = ?
            """,
            (
                VALOR_INSCRICAO,
                VALOR_INSCRICAO,
                id_inscricao
            )
        )

        conn.commit()

        # ==============================
    # TENTAR REUTILIZAR PIX PENDENTE
    # ==============================

    if payment_id:

        try:
            pagamento_atual = consultar_pagamento(
                payment_id
            )

            status_mp = pagamento_atual.get(
                "status"
            )

            # Se ainda está aguardando,
            # tentamos mostrar o mesmo QR Code.
            if status_mp in (
                "pending",
                "in_process"
            ):

                dados_pix = extrair_dados_pix(
                    pagamento_atual
                )

                if (
                    dados_pix["qr_code"]
                    and
                    dados_pix["qr_code_base64"]
                ):

                    return render_template(
                        "pagamento_pix.html",

                        nome_social=nome_social,

                        valor_total=(
                            f"{VALOR_INSCRICAO:.2f}"
                            .replace(".", ",")
                        ),

                        payment_id=str(
                            payment_id
                        ),

                        qr_code=(
                            dados_pix["qr_code"]
                        ),

                        qr_code_base64=(
                            dados_pix[
                                "qr_code_base64"
                            ]
                        )
                    )

        except Exception as erro:
            print(
                "Não foi possível reutilizar "
                "o pagamento anterior. "
                "Um novo Pix será criado:",
                repr(erro)
            )


    # ==============================
    # CRIAR NOVO PIX
    # ==============================

    try:
        # Aqui usamos uma chave nova porque
        # esta é uma nova tentativa de pagamento.
        idempotency_key = (
            f"emeerj-{id_inscricao}-"
            f"{uuid4().hex}"
        )

        pagamento = criar_pagamento_pix(
            id_inscricao=id_inscricao,
            email=email_cadastrado,
            cpf=cpf,
            valor_inscricao=VALOR_INSCRICAO,
            idempotency_key=idempotency_key
        )

        novo_payment_id = str(
            pagamento["payment_id"]
        )

        with conectar_banco() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE inscricoes
                SET
                    payment_id = ?,
                    payment_status_detail = ?,
                    status_pagamento = ?
                WHERE id = ?
                """,
                (
                    novo_payment_id,
                    pagamento["status_detail"],
                    "PENDENTE",
                    id_inscricao
                )
            )

            conn.commit()

        return render_template(
            "pagamento_pix.html",

            nome_social=nome_social,

            valor_total=(
                f"{VALOR_INSCRICAO:.2f}"
                .replace(".", ",")
            ),

            payment_id=novo_payment_id,

            qr_code=pagamento["qr_code"],

            qr_code_base64=(
                pagamento["qr_code_base64"]
            )
        )

    except Exception as erro:
        print(
            "Erro ao criar novo Pix:",
            repr(erro)
        )

        return render_template(
            "inscricao_existente.html",
            erro=(
                "Não foi possível gerar o Pix "
                "agora. Tente novamente mais tarde."
            )
        ), 500


@app.route(
    "/consultar-inscricao",
    methods=["GET", "POST"]
)
def consultar_inscricao():

    if request.method == "GET":
        return render_template(
            "consultar_inscricao.html",
            erro=None
        )

    cpf = normalizar_cpf(
        request.form.get("cpf", "")
    )

    email = (
        request.form.get("email", "")
        .strip()
        .lower()
    )

    if not cpf_valido(cpf):
        return render_template(
            "consultar_inscricao.html",
            erro=(
                "Informe um CPF válido."
            )
        )

    if not email:
        return render_template(
            "consultar_inscricao.html",
            erro=(
                "Informe o e-mail utilizado "
                "na inscrição."
            )
        )

    with conectar_banco() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                nome_social,
                email,
                status_pagamento
            FROM inscricoes
            WHERE cpf = ?
            """,
            (cpf,)
        )

        inscricao = cursor.fetchone()

    # Resposta propositalmente genérica.
    # Não diz se o CPF ou o e-mail foi o incorreto.
    if not inscricao:
        return render_template(
            "consultar_inscricao.html",
            erro=(
                "Não encontramos uma inscrição "
                "com os dados informados."
            )
        )

    (
        nome_social,
        email_cadastrado,
        status_pagamento
    ) = inscricao

    if (
        email
        != email_cadastrado.strip().lower()
    ):
        return render_template(
            "consultar_inscricao.html",
            erro=(
                "Não encontramos uma inscrição "
                "com os dados informados."
            )
        )

    return render_template(
        "inscricao_existente.html",
        erro=None,
        nome_social=nome_social,
        status_pagamento=status_pagamento,
        cpf=cpf,
        email=email_cadastrado
    )
    
@app.route(
    "/pagamento/status/<payment_id>"
)
def consultar_status_pagamento(payment_id):

    with conectar_banco() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT status_pagamento
            FROM inscricoes
            WHERE payment_id = ?
            """,
            (payment_id,)
        )

        inscricao = cursor.fetchone()

    if not inscricao:
        return {
            "status": "NAO_ENCONTRADO"
        }, 404

    return {
        "status": inscricao[0]
    }

if __name__ == "__main__":
    app.run(debug=True)
    
    