document.addEventListener(
    "DOMContentLoaded",
    function () {

        const paginaPix =
            document.getElementById(
                "paginaPix"
            );

        const codigoPix =
            document.getElementById(
                "codigoPix"
            );

        const botaoCopiar =
            document.getElementById(
                "botaoCopiar"
            );

        const mensagemCopia =
            document.getElementById(
                "mensagemCopia"
            );

        const statusPagamento =
            document.getElementById(
                "statusPagamento"
            );


        if (!paginaPix) {
            return;
        }


        const paymentId =
            paginaPix.dataset.paymentId;


        // ==============================
        // COPIAR CÓDIGO PIX
        // ==============================

        if (
            botaoCopiar &&
            codigoPix
        ) {

            botaoCopiar.addEventListener(
                "click",
                async function () {

                    try {

                        await navigator.clipboard.writeText(
                            codigoPix.value
                        );

                        mensagemCopia.textContent =
                            "Código Pix copiado!";

                        botaoCopiar.textContent =
                            "Copiado ✓";


                        setTimeout(
                            () => {

                                botaoCopiar.textContent =
                                    "Copiar código Pix";

                                mensagemCopia.textContent =
                                    "";

                            },
                            3000
                        );

                    } catch (erro) {

                        console.error(
                            "Erro ao copiar Pix:",
                            erro
                        );


                        codigoPix.select();


                        mensagemCopia.textContent =
                            "Selecione e copie o código manualmente.";

                    }

                }
            );

        }


        // ==============================
        // CONSULTAR STATUS
        // ==============================

        let consultaEmAndamento = false;

        let pagamentoFinalizado = false;


        async function consultarStatus() {

            if (
                consultaEmAndamento ||
                pagamentoFinalizado
            ) {
                return;
            }


            consultaEmAndamento = true;


            try {

                const resposta = await fetch(
                    `/pagamento/status/${paymentId}`,
                    {
                        cache: "no-store"
                    }
                );


                if (!resposta.ok) {
                    throw new Error(
                        "Não foi possível consultar o pagamento."
                    );
                }


                const dados =
                    await resposta.json();


                const status =
                    dados.status;


                if (status === "APROVADO") {

                    pagamentoFinalizado = true;


                    statusPagamento.innerHTML = `
                        <div>
                            <strong>
                                Pagamento confirmado ✓
                            </strong>

                            <p>
                                Redirecionando para a confirmação...
                            </p>
                        </div>
                    `;


                    setTimeout(
                        () => {

                            window.location.href =
                                `/pagamento/sucesso?payment_id=${paymentId}`;

                        },
                        1000
                    );


                    return;
                }


                if (
                    status === "RECUSADO" ||
                    status === "CANCELADO"
                ) {

                    pagamentoFinalizado = true;


                    statusPagamento.innerHTML = `
                        <div>
                            <strong>
                                Pagamento não concluído
                            </strong>

                            <p>
                                Consulte sua inscrição para tentar novamente.
                            </p>
                        </div>
                    `;

                }

            } catch (erro) {

                console.error(
                    "Erro ao consultar status:",
                    erro
                );

                // Não mostramos erro para o usuário
                // a cada falha temporária.
                // A próxima consulta tentará novamente.

            } finally {

                consultaEmAndamento = false;

            }

        }


        // Primeira consulta imediata.
        consultarStatus();


        // Depois consulta a cada 3 segundos.
        setInterval(
            consultarStatus,
            3000
        );


        // Quando o usuário volta para a aba,
        // consulta imediatamente.
        document.addEventListener(
            "visibilitychange",
            function () {

                if (
                    document.visibilityState ===
                    "visible"
                ) {
                    consultarStatus();
                }

            }
        );

    }
);