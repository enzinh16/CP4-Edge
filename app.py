from dotenv import load_dotenv

# Precisa vir ANTES do "import mqtt", pois mqtt.py importa crew.py,
# que usa a OPENAI_API_KEY assim que o CrewAI é chamado.
load_dotenv()

from flask import Flask, render_template, jsonify
import mqtt


app = Flask(__name__)


@app.route("/")
def home():

    return render_template(
        "relatorio.html",
        alturas=mqtt.ultimas_alturas,
        estatisticas=mqtt.estatisticas,
        relatorio=mqtt.ultimo_relatorio
    )


@app.route("/api/alturas")
def api_alturas():

    return jsonify({
        "alturas": mqtt.ultimas_alturas
    })


@app.route("/api/relatorio")
def api_relatorio():

    return jsonify({
        "estatisticas": mqtt.estatisticas,
        "relatorio": mqtt.ultimo_relatorio
    })


if __name__ == "__main__":

    print(
        "Iniciando aplicação...",
        flush=True
    )

    mqtt.iniciar_thread_mqtt()

    print(
        "MQTT iniciado!",
        flush=True
    )

    print(
        "Iniciando Flask...",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=5000
    )