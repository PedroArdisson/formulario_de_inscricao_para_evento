document.addEventListener("DOMContentLoaded", function () {

    const campoCpf = document.getElementById("cpf");

if (campoCpf) {
    campoCpf.addEventListener("input", () => {
        let valor = campoCpf.value
            .replace(/\D/g, "")
            .slice(0, 11);

        if (valor.length > 9) {
            valor = valor.replace(
                /(\d{3})(\d{3})(\d{3})(\d{1,2})/,
                "$1.$2.$3-$4"
            );
        } else if (valor.length > 6) {
            valor = valor.replace(
                /(\d{3})(\d{3})(\d{1,3})/,
                "$1.$2.$3"
            );
        } else if (valor.length > 3) {
            valor = valor.replace(
                /(\d{3})(\d{1,3})/,
                "$1.$2"
            );
        }

        campoCpf.value = valor;
    });
}

    // ==============================
    // CAMPOS CONDICIONAIS SIM / NÃO
    // ==============================

    function configurarCampoCondicional(nomeRadio, valorEsperado, containerId, inputId = null) {
        const radios = document.querySelectorAll(`input[name="${nomeRadio}"]`);
        const container = document.getElementById(containerId);
        const input = inputId ? document.getElementById(inputId) : null;

        if (!container) {
            console.warn(`Container não encontrado: ${containerId}`);
            return;
        }

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


    // ==============================
    // CAMPO OUTRO CEU
    // ==============================

    const ceu = document.getElementById("ceu");
    const outroCeuContainer = document.getElementById("outroCeuContainer");
    const outroCeu = document.getElementById("outroCeu");

    if (ceu && outroCeuContainer && outroCeu) {
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
    }


    // ==============================
    // TIPO DE PARTICIPAÇÃO
    // ==============================

    const radiosParticipacao = document.querySelectorAll(
        'input[name="tipo_participacao"]'
    );

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


    // ==============================
    // ALIMENTAÇÃO
    // ==============================

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


    // ==============================
    // CAMISA E VALOR TOTAL
    // ==============================

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

        if (querCamisa === "Sim") {
            valorCamisa = VALOR_CAMISA;
        }

        const valorTotal = VALOR_INSCRICAO + valorCamisa;

        if (valorCamisaTexto) {
            valorCamisaTexto.textContent =
                `R$ ${valorCamisa.toFixed(2).replace(".", ",")}`;
        }

        if (valorTotalTexto) {
            valorTotalTexto.textContent =
                `R$ ${valorTotal.toFixed(2).replace(".", ",")}`;
        }
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


    // ==============================
    // VALIDAÇÃO FINAL DO FORMULÁRIO
    // ==============================

    const formInscricao = document.getElementById("formInscricao");

    formInscricao.addEventListener("submit", function (event) {
        const alimentacoesMarcadas = document.querySelectorAll(
            'input[name="alimentacao"]:checked'
        );

        if (alimentacoesMarcadas.length === 0) {
            event.preventDefault();
            alert("Selecione pelo menos uma opção de alimentação.");
            return;
        }
    });

});