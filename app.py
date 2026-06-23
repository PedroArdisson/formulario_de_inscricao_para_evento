from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

from sheets_service import enviar_inscricao_para_planilha

app = Flask(__name__)

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

    # Salva no SQLite
    conn = sqlite3.connect("database.db")
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
            data_inscricao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        "status_pagamento": status_pagamento
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

    return f"""
        <h1>Inscrição recebida com sucesso!</h1>
        <p>Obrigado, {nome_social}.</p>
        <p>Valor total: R$ {valor_total:.2f}</p>
        <p>Status do pagamento: {status_pagamento}</p>
        <a href="/">Voltar para o formulário</a>
    """


if __name__ == "__main__":
    app.run(debug=True)