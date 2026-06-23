function configurarCampoCondicional(nomeRadio, valorEsperado, containerId, inputId = null) {
    const radios = document.querySelectorAll(`input[name="${nomeRadio}"]`);
    const container = document.getElementById(containerId);
    const input = inputId ? document.getElementById(inputId) : null;

    radios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.checked && radio.value === valorEsperado) {
                container.classList.remove("hidden");

                if (input) {
                    input.required = true;
                }
            } else if (radio.checked) {
                container.classList.add("hidden");

                if (input) {
                    input.required = false;
                    input.value = "";
                }
            }
        });
    });
}

configurarCampoCondicional(
    "possui_alergia",
    "Sim",
    "alergiaContainer",
    "qualAlergia"
);

configurarCampoCondicional(
    "usa_medicamento",
    "Sim",
    "medicamentoContainer",
    "qualMedicamento"
);

configurarCampoCondicional(
    "possui_convenio",
    "Sim",
    "convenioContainer",
    "qualConvenio"
);

configurarCampoCondicional(
    "possui_deficiencia",
    "Sim",
    "deficienciaContainer",
    "qualDeficiencia"
);

const ceu = document.getElementById("ceu");
const outroCeuContainer = document.getElementById("outroCeuContainer");
const outroCeu = document.getElementById("outroCeu");

ceu.addEventListener("change", () => {
    if (ceu.value === "Outro") {
        outroCeuContainer.classList.remove("hidden");
        outroCeu.required = true;
    } else {
        outroCeuContainer.classList.add("hidden");
        outroCeu.required = false;
        outroCeu.value = "";
    }
});

const radiosParticipacao = document.querySelectorAll('input[name="tipo_participacao"]');
const trabalhoContainer = document.getElementById("trabalhoContainer");
const areaTrabalho = document.getElementById("areaTrabalho");

radiosParticipacao.forEach(radio => {
    radio.addEventListener("change", () => {
        if (radio.checked && radio.value === "Trabalhador") {
            trabalhoContainer.classList.remove("hidden");
            areaTrabalho.required = true;
        } else if (radio.checked) {
            trabalhoContainer.classList.add("hidden");
            areaTrabalho.required = false;
            areaTrabalho.value = "";
        }
    });
});

const alimentacaoComum = document.getElementById("alimentacaoComum");
const alimentacoes = document.querySelectorAll('input[name="alimentacao"]');

alimentacoes.forEach(opcao => {
    opcao.addEventListener("change", () => {
        if (opcao === alimentacaoComum && opcao.checked) {
            alimentacoes.forEach(item => {
                if (item !== alimentacaoComum) {
                    item.checked = false;
                }
            });
        }

        if (opcao !== alimentacaoComum && opcao.checked) {
            alimentacaoComum.checked = false;
        }
    });
});

const VALOR_INSCRICAO = 25;
const VALOR_CAMISA = 40; // Valor provisório

const radiosCamisa = document.querySelectorAll('input[name="quer_camisa"]');
const camisaContainer = document.getElementById("camisaContainer");
const tamanhoCamisa = document.getElementById("tamanhoCamisa");

const valorCamisaTexto = document.getElementById("valorCamisaTexto");
const valorTotalTexto = document.getElementById("valorTotalTexto");

function atualizarResumoPagamento() {
    const querCamisa = document.querySelector(
        'input[name="quer_camisa"]:checked'
    )?.value;

    let valorCamisa = 0;
    let valorTotal = VALOR_INSCRICAO;

    if (querCamisa === "Sim") {
        valorCamisa = VALOR_CAMISA;
        valorTotal = VALOR_INSCRICAO + VALOR_CAMISA;
    }

    valorCamisaTexto.textContent = `R$ ${valorCamisa.toFixed(2).replace(".", ",")}`;
    valorTotalTexto.textContent = `R$ ${valorTotal.toFixed(2).replace(".", ",")}`;
}

radiosCamisa.forEach(radio => {
    radio.addEventListener("change", () => {
        if (radio.checked && radio.value === "Sim") {
            camisaContainer.classList.remove("hidden");
            tamanhoCamisa.required = true;
        }

        if (radio.checked && radio.value === "Não") {
            camisaContainer.classList.add("hidden");
            tamanhoCamisa.required = false;
            tamanhoCamisa.value = "";
        }

        atualizarResumoPagamento();
    });
});

atualizarResumoPagamento();

const formInscricao = document.getElementById("formInscricao");

formInscricao.addEventListener("submit", (event) => {
    const alimentacoesMarcadas = document.querySelectorAll(
        'input[name="alimentacao"]:checked'
    );

    if (alimentacoesMarcadas.length === 0) {
        event.preventDefault();
        alert("Selecione pelo menos uma opção de alimentação.");
        return;
    }
});

formInscricao.addEventListener("submit", async (event) => {
    event.preventDefault();

    const alimentacoesMarcadas = document.querySelectorAll(
        'input[name="alimentacao"]:checked'
    );

    if (alimentacoesMarcadas.length === 0) {
        alert("Selecione pelo menos uma opção de alimentação.");
        return;
    }

    const dados = {
        nome_completo: document.getElementById("nomeCompleto").value,
        email: document.getElementById("email").value,
        nome_social: document.getElementById("nomeSocial").value,
        idade: document.getElementById("idade").value,
        genero: document.getElementById("genero").value,
        casa_espirita: document.getElementById("casaEspirita").value,
        ceu: document.getElementById("ceu").value,
        outro_ceu: document.getElementById("outroCeu").value,
        telefone: document.getElementById("telefone").value,

        alimentacao: Array.from(alimentacoesMarcadas).map(
            item => item.value
        ),

        possui_alergia: document.querySelector(
            'input[name="possui_alergia"]:checked'
        )?.value,

        qual_alergia: document.getElementById("qualAlergia").value,

        usa_medicamento: document.querySelector(
            'input[name="usa_medicamento"]:checked'
        )?.value,

        qual_medicamento: document.getElementById("qualMedicamento").value,

        possui_convenio: document.querySelector(
            'input[name="possui_convenio"]:checked'
        )?.value,

        qual_convenio: document.getElementById("qualConvenio").value,

        contato_emergencia_nome: document.getElementById(
            "contatoEmergenciaNome"
        ).value,

        contato_emergencia_telefone: document.getElementById(
            "contatoEmergenciaTelefone"
        ).value,

        participou_emeerj: document.querySelector(
            'input[name="participou_emeerj"]:checked'
        )?.value,

        possui_deficiencia: document.querySelector(
            'input[name="possui_deficiencia"]:checked'
        )?.value,

        qual_deficiencia: document.getElementById("qualDeficiencia").value,

        tipo_participacao: document.querySelector(
            'input[name="tipo_participacao"]:checked'
        )?.value,

        area_trabalho: document.getElementById("areaTrabalho").value,

        quer_camisa: document.querySelector(
            'input[name="quer_camisa"]:checked'
        )?.value,

        tamanho_camisa: document.getElementById("tamanhoCamisa").value
    };

    const resultado = await resposta.json();

    alert(resultado.mensagem);
});


formInscricao.addEventListener("submit", function(event) {
    event.preventDefault();

    alert("O JavaScript interceptou o formulário!");
});