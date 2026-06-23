import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inscricoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome_completo TEXT NOT NULL,
    email TEXT NOT NULL,
    nome_social TEXT NOT NULL,
    idade INTEGER NOT NULL,
    genero TEXT NOT NULL,

    casa_espirita TEXT NOT NULL,
    ceu TEXT NOT NULL,
    outro_ceu TEXT,

    telefone TEXT NOT NULL,

    alimentacao TEXT NOT NULL,

    possui_alergia TEXT NOT NULL,
    qual_alergia TEXT,

    usa_medicamento TEXT NOT NULL,
    qual_medicamento TEXT,

    possui_convenio TEXT NOT NULL,
    qual_convenio TEXT,

    contato_emergencia_nome TEXT NOT NULL,
    contato_emergencia_telefone TEXT NOT NULL,

    participou_emeerj TEXT NOT NULL,

    possui_deficiencia TEXT NOT NULL,
    qual_deficiencia TEXT,

    tipo_participacao TEXT NOT NULL,
    area_trabalho TEXT,

    quer_camisa TEXT NOT NULL,
    tamanho_camisa TEXT,

    valor_inscricao REAL NOT NULL,
    valor_camisa REAL NOT NULL,
    valor_total REAL NOT NULL,

    status_pagamento TEXT NOT NULL DEFAULT 'PENDENTE',

    data_inscricao TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")