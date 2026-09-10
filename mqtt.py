import paho.mqtt.client as mqtt
import threading
import statistics

from crew import gerar_relatorio


BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO = "grupo-11/cp4"

# ==============================
# REGRAS DE ESPECIFICAÇÃO
# ==============================
# Altura acima deste valor é considerada FORA da especificação
ALTURA_LIMITE_CM = 30

# Se o percentual de medições fora da especificação for maior que
# este valor, o relatório é direcionado para a SUSTENTAÇÃO.
# Caso contrário, é direcionado para a DIREÇÃO.
PERCENTUAL_LIMITE = 30

alturas = []
ultimas_alturas = []

estatisticas = {}
ultimo_relatorio = None


def ao_conectar(client, userdata, flags, rc):

    if rc == 0:
        print("Conectado ao broker MQTT!", flush=True)

        client.subscribe(TOPICO)

        print(
            f"Inscrito no tópico: {TOPICO}",
            flush=True
        )

    else:
        print(
            f"Erro ao conectar. Código: {rc}",
            flush=True
        )


def ao_receber(client, userdata, msg):

    global alturas
    global ultimas_alturas
    global estatisticas
    global ultimo_relatorio

    dados = msg.payload.decode("utf-8")

    try:

        altura = float(dados)

        alturas.append(altura)

        print(
            f"Altura recebida: {altura} cm "
            f"({len(alturas)}/50)",
            flush=True
        )

        if len(alturas) >= 50:

            print("\n==============================")
            print("50 ALTURAS RECEBIDAS!")
            print("==============================")

            # Guarda as 50 alturas
            ultimas_alturas = alturas.copy()

            # Estatísticas
            minima = min(ultimas_alturas)
            maxima = max(ultimas_alturas)
            media = statistics.mean(ultimas_alturas)
            mediana = statistics.median(ultimas_alturas)

            # ==============================
            # CLASSIFICAÇÃO DENTRO/FORA DA ESPECIFICAÇÃO
            # (feita em Python, antes de enviar ao CrewAI)
            # ==============================

            dentro_espec = [
                altura
                for altura in ultimas_alturas
                if altura <= ALTURA_LIMITE_CM
            ]

            fora_espec = [
                altura
                for altura in ultimas_alturas
                if altura > ALTURA_LIMITE_CM
            ]

            qtd_fora = len(fora_espec)
            percentual_fora = round(
                (qtd_fora / len(ultimas_alturas)) * 100,
                2
            )

            if percentual_fora > PERCENTUAL_LIMITE:
                destino = "sustentacao"
            else:
                destino = "direcao"

            estatisticas = {
                "quantidade": len(ultimas_alturas),
                "minima": round(minima, 2),
                "maxima": round(maxima, 2),
                "media": round(media, 2),
                "mediana": round(mediana, 2),
                "limite_especificacao": ALTURA_LIMITE_CM,
                "qtd_dentro_espec": len(dentro_espec),
                "qtd_fora_espec": qtd_fora,
                "percentual_fora": percentual_fora,
                "destino": destino
            }

            print("\nEstatísticas:")
            print(estatisticas)

            print(
                f"\nClassificação: {percentual_fora}% fora da "
                f"especificação (limite: {PERCENTUAL_LIMITE}%)"
            )
            print(f"Relatório será direcionado para: {destino.upper()}")

            # ==============================
            # GERAR RELATÓRIO COM CREWAI
            # ==============================

            print("\nGerando relatório com CrewAI...", flush=True)

            try:

                ultimo_relatorio = gerar_relatorio(
                    ultimas_alturas,
                    estatisticas
                )

                ultimo_relatorio = str(ultimo_relatorio)

                print(
                    "\nRelatório gerado com sucesso!",
                    flush=True
                )

                print("\n==============================")
                print("RELATÓRIO")
                print("==============================")
                print(ultimo_relatorio)
                print("==============================\n")

            except Exception as erro:

                print(
                    f"ERRO AO GERAR RELATÓRIO: {erro}",
                    flush=True
                )

                ultimo_relatorio = (
                    "Não foi possível gerar o relatório "
                    f"com a IA: {erro}"
                )

            # Limpa para começar nova coleta
            alturas.clear()

    except ValueError:

        print(
            f"Valor inválido recebido: {dados}",
            flush=True
        )


def iniciar_mqtt():

    print("Iniciando MQTT...", flush=True)

    try:
        cliente = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1
        )

    except AttributeError:
        cliente = mqtt.Client()

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber

    print("Conectando ao broker...", flush=True)

    try:

        cliente.connect(
            BROKER,
            PORTA,
            60
        )

        print(
            "Conectado ao servidor MQTT.",
            flush=True
        )

    except Exception as erro:

        print(
            f"Erro ao conectar ao MQTT: {erro}",
            flush=True
        )

        return

    print(
        "Iniciando loop MQTT...",
        flush=True
    )

    cliente.loop_forever()


def iniciar_thread_mqtt():

    thread = threading.Thread(
        target=iniciar_mqtt,
        daemon=True
    )

    thread.start()

    return thread