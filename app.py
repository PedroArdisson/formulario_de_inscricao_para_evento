from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def pagina_inicial():
    return render_template("index.html")


@app.route("/inscricao", methods=["POST"])
def receber_inscricao():
    dados = {
        "nome_completo": request.form.get("nome_completo"),
        "email": request.form.get("email"),
        "nome_social": request.form.get("nome_social"),
        "idade": request.form.get("idade"),
        "genero": request.form.get("genero"),
        "casa_espirita": request.form.get("casa_espirita"),
        "ceu": request.form.get("ceu"),
        "outro_ceu": request.form.get("outro_ceu"),
        "telefone": request.form.get("telefone"),

        # Checkbox pode vir com mais de uma opção marcada
        "alimentacao": request.form.getlist("alimentacao"),

        "possui_alergia": request.form.get("possui_alergia"),
        "qual_alergia": request.form.get("qual_alergia"),

        "usa_medicamento": request.form.get("usa_medicamento"),
        "qual_medicamento": request.form.get("qual_medicamento"),

        "possui_convenio": request.form.get("possui_convenio"),
        "qual_convenio": request.form.get("qual_convenio"),

        "contato_emergencia_nome": request.form.get("contato_emergencia_nome"),
        "contato_emergencia_telefone": request.form.get("contato_emergencia_telefone"),

        "participou_emeerj": request.form.get("participou_emeerj"),

        "possui_deficiencia": request.form.get("possui_deficiencia"),
        "qual_deficiencia": request.form.get("qual_deficiencia"),

        "tipo_participacao": request.form.get("tipo_participacao"),
        "area_trabalho": request.form.get("area_trabalho"),

        "quer_camisa": request.form.get("quer_camisa"),
        "tamanho_camisa": request.form.get("tamanho_camisa"),
    }

    print("\n--- NOVA INSCRIÇÃO RECEBIDA ---")
    print(dados)
    print("--------------------------------\n")

    return """
        <h1>Inscrição recebida com sucesso!</h1>
        <p>Os dados chegaram no Flask.</p>
        <a href="/">Voltar</a>
    """


if __name__ == "__main__":
    app.run(debug=True)