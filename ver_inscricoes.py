import sqlite3

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM inscricoes
""")

inscricoes = cursor.fetchall()

for inscricao in inscricoes:
    print("\n--- INSCRIÇÃO ---")
    print(f"ID: {inscricao['id']}")
    print(f"Nome completo: {inscricao['nome_completo']}")
    print(f"E-mail: {inscricao['email']}")
    print(f"Nome social: {inscricao['nome_social']}")
    print(f"Idade: {inscricao['idade']}")
    print(f"Gênero: {inscricao['genero']}")
    print(f"Casa espírita: {inscricao['casa_espirita']}")
    print(f"CEU: {inscricao['ceu']}")
    print(f"Outro CEU: {inscricao['outro_ceu']}")
    print(f"Telefone: {inscricao['telefone']}")
    print(f"Alimentação: {inscricao['alimentacao']}")
    print(f"Alergia: {inscricao['possui_alergia']}")
    print(f"Qual alergia: {inscricao['qual_alergia']}")
    print(f"Medicamento: {inscricao['usa_medicamento']}")
    print(f"Qual medicamento: {inscricao['qual_medicamento']}")
    print(f"Convênio: {inscricao['possui_convenio']}")
    print(f"Qual convênio: {inscricao['qual_convenio']}")
    print(f"Contato emergência: {inscricao['contato_emergencia_nome']}")
    print(f"Telefone emergência: {inscricao['contato_emergencia_telefone']}")
    print(f"Já participou: {inscricao['participou_emeerj']}")
    print(f"Deficiência: {inscricao['possui_deficiencia']}")
    print(f"Qual deficiência: {inscricao['qual_deficiencia']}")
    print(f"Tipo participação: {inscricao['tipo_participacao']}")
    print(f"Área de trabalho: {inscricao['area_trabalho']}")
    print(f"Quer camisa: {inscricao['quer_camisa']}")
    print(f"Tamanho camisa: {inscricao['tamanho_camisa']}")
    print(f"Valor inscrição: R$ {inscricao['valor_inscricao']}")
    print(f"Valor camisa: R$ {inscricao['valor_camisa']}")
    print(f"Valor total: R$ {inscricao['valor_total']}")
    print(f"Status pagamento: {inscricao['status_pagamento']}")
    print(f"Data inscrição: {inscricao['data_inscricao']}")

conn.close()