import os
from decimal import Decimal
from datetime import datetime

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
    criar_preferencia_pagamento,
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
VALOR_CAMISA = 40  # Valor provisório


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

    # Camisa
    quer_camisa = request.form.get("quer_camisa")
    tamanho_camisa = request.form.get("tamanho_camisa")

    valor_camisa = 0

    if quer_camisa == "Sim":
        valor_camisa = VALOR_CAMISA

    valor_total = VALOR_INSCRICAO + valor_camisa

    status_pagamento = "PENDENTE"
    data_inscricao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
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
        pagamento = criar_preferencia_pagamento(
            id_inscricao=id_inscricao,
            nome_completo=nome_completo,
            email=email,
            valor_inscricao=VALOR_INSCRICAO,
            valor_camisa=valor_camisa,
            valor_total=valor_total,
            quer_camisa=quer_camisa,
            tamanho_camisa=tamanho_camisa
        )

        print("Preferência criada no Mercado Pago:")
        print(pagamento)
        
        with conectar_banco() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE inscricoes
                SET
                    preference_id = ?,
                    link_pagamento = ?
                WHERE id = ?
                """,
                (
                    pagamento["id_preferencia"],
                    pagamento["link_pagamento"],
                    id_inscricao
                )
            )

            conn.commit()

        return redirect(pagamento["link_pagamento"])

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

@app.route("/pagamento/sucesso")
def pagamento_sucesso():
    return render_template(
        "sucesso.html",
        nome_social="Participante",
        valor_total="",
        status_pagamento="PAGAMENTO APROVADO"
    )


@app.route("/pagamento/falha")
def pagamento_falha():
    return """
        <h1>Pagamento não concluído</h1>
        <p>Não conseguimos confirmar seu pagamento.</p>
        <a href="/">Voltar para o formulário</a>
    """


@app.route("/pagamento/pendente")
def pagamento_pendente():
    return """
        <h1>Pagamento pendente</h1>
        <p>Seu pagamento ainda está aguardando confirmação.</p>
        <a href="/">Voltar para o formulário</a>
    """

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
                "authorized": "AUTORIZADO",
                "rejected": "RECUSADO",
                "cancelled": "CANCELADO",
                "refunded": "REEMBOLSADO",
                "charged_back": "ESTORNADO"
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
                nome_social,
                email,
                status_pagamento,
                link_pagamento
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
        nome_social,
        email_cadastrado,
        status_pagamento,
        link_pagamento
    ) = inscricao

    if (
        email
        != email_cadastrado.strip().lower()
    ):
        return render_template(
            "inscricao_existente.html",
            erro=(
                "Os dados informados não correspondem "
                "a uma inscrição."
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

    if not link_pagamento:
        return render_template(
            "inscricao_existente.html",
            erro=(
                "Não foi possível recuperar o link "
                "de pagamento. Tente novamente mais tarde."
            )
        ), 500

    return redirect(link_pagamento)

if __name__ == "__main__":
    app.run(debug=True)
    
    