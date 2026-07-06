import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


# No PC, usa "database.db".
# No servidor, usará o valor definido em DATABASE_PATH.
DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", "database.db")
)


def conectar_banco():
    """
    Abre uma conexão com o banco de dados.

    Antes de conectar, garante que a pasta do banco exista.
    Isso será importante no servidor, onde usaremos /app/data.
    """
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        str(DATABASE_PATH),
        timeout=30
    )


def inicializar_banco():
    """
    Cria a tabela de inscrições caso ela ainda não exista.
    """

    with conectar_banco() as conn:
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

                status_pagamento TEXT NOT NULL
                    DEFAULT 'PENDENTE',

                termo_lgpd TEXT NOT NULL
                    DEFAULT 'Sim',

                data_inscricao TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()