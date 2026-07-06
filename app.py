from flask import Flask, render_template, request, redirect
from datetime import datetime

from mercado_pago_service import criar_preferencia_pagamento
from sheets_service import enviar_inscricao_para_planilha
from database import conectar_banco, inicializar_banco

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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome_completo,
        email,
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
    dados = request.get_json(silent=True) or {}

    print("\n--- WEBHOOK MERCADO PAGO RECEBIDO ---")
    print("Query params:", request.args.to_dict())
    print("Dados:", dados)
    print("-------------------------------------\n")

    return "", 200

if __name__ == "__main__":
    app.run(debug=True)