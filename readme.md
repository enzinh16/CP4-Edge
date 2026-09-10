# CP04 – Edge com Agentes de IA

**Disciplina:** Edge Computing
**Curso:** Ciências da Computação – 2º Ano
**Turma:** [2CCPH]

## Integrantes

| RM | Nome |
|----|------|
| [563761] | [Auro Vanetti] |
| [562235] | [Bruno Soares de Santanna] |
| [564177] | [Enzo Yokokura Araujo] |
| [566434] | [Marco Antonio Ferreira Fonseca] |
| [554911] | [Renan Mano Otero] |

## Objetivo

Aplicação de Edge Computing que recebe, via **MQTT**, dados de um sensor
mockado conectado a um **ESP32**, analisa os dados com **CrewAI** e gera
automaticamente um relatório direcionado ao setor correto da empresa:

- **Fora da especificação** → relatório direcionado à **equipe de
  sustentação**, apresentando a situação identificada.
- **Dentro da especificação** → relatório direcionado à **direção**,
  informando os impactos positivos dos dados coletados.

## Sensor escolhido

**Sensor de altura de vegetação** próxima a uma rodovia (mockado no ESP32,
valores simulados entre 1 e 60 cm).

| Regra | Valor |
|---|---|
| Especificação (altura considerada adequada) | ≤ 30 cm |
| Fora da especificação | > 30 cm |
| Critério de direcionamento | Se **mais de 30%** das 50 medições do lote estiverem fora da especificação → relatório vai para a **sustentação**. Caso contrário → vai para a **direção** (com pontos de atenção, se houver). |

## Arquitetura

```
ESP32 (mockado / Wokwi-Velxio)
   │  publica altura via MQTT (a cada 1s)
   ▼
Broker público (broker.hivemq.com, tópico "grupo-11/cp4")
   │
   ▼
Aplicação Python (mqtt.py)
   │  acumula 50 leituras, calcula estatísticas
   │  classifica dentro/fora da especificação (Python puro)
   ▼
CrewAI (crew.py)
   │  gera relatório com prompt específico conforme o destino
   ▼
Flask (app.py + templates/relatorio.html)
   → Dashboard web com gráfico, estatísticas e relatório da IA
```

## Simulação do ESP32 (Wokwi / Velxio)

O firmware do ESP32 foi simulado no Velxio (compatível com Wokwi), publicando
alturas mockadas via MQTT para o mesmo broker e tópico usados pela aplicação:

🔗 https://velxio.dev/weeblyenzo/cp4-edge-computing

## Tecnologias utilizadas

- **ESP32** (simulado) + `PubSubClient` (MQTT)
- **Python 3.12**
- **Flask** – dashboard web
- **paho-mqtt** – cliente MQTT (subscriber)
- **CrewAI** – agentes de IA para geração dos relatórios
- **Chart.js** – gráfico de alturas no dashboard
- **Docker / Docker Compose** (opcional)

## Estrutura do projeto

```
docker/
├── app.py                # Aplicação Flask (dashboard + rotas da API)
├── mqtt.py                # Cliente MQTT: recebe, classifica e aciona o CrewAI
├── crew.py                # Agentes/Tasks do CrewAI (sustentação e direção)
├── requirements.txt        # Dependências Python
├── dockerfile              # Build da imagem Docker
├── docker-compose.yml      # Orquestração via Docker Compose
├── .env.example             # Modelo da variável de ambiente necessária
├── static/
│   └── style.css           # Estilos do dashboard
└── templates/
    └── relatorio.html       # Página do dashboard
```

## Como executar

### Pré-requisitos

- Uma chave de API da OpenAI (necessária para o CrewAI funcionar)

### Opção 1 — Com Docker (recomendado)

1. Crie um arquivo `.env` na raiz do projeto (mesma pasta do `dockerfile`)
   com o conteúdo:
   ```
   OPENAI_API_KEY="sua-chave-aqui"
   ```
2. Suba o container:
   ```bash
   docker compose up --build
   ```
3. Acesse o dashboard em: http://localhost:5000

### Opção 2 — Sem Docker (Python local)

1. **Instale o Python 3.12**.

2. **Crie o ambiente virtual**, dentro da pasta do projeto:
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Crie o arquivo `.env`** na raiz do projeto com:
   ```
   OPENAI_API_KEY="sua-chave-aqui"
   ```

6. **Rode a aplicação:**
   ```bash
   python app.py
   ```

7. **Acesse o dashboard** em: http://localhost:5000

> O ESP32 (simulado no Velxio, link acima) precisa estar rodando e publicando
> no tópico `grupo-11/cp4` do broker `broker.hivemq.com` para que os dados
> cheguem até a aplicação. Depois de 50 medições recebidas, o relatório é
> gerado automaticamente e exibido no dashboard.

## Fluxo de decisão (resumo)

1. O ESP32 publica uma altura mockada (1–60 cm) por segundo via MQTT.
2. A aplicação Python acumula 50 leituras e calcula estatísticas
   (mínima, máxima, média, mediana).
3. Cada leitura é classificada em Python como **dentro** (≤ 30 cm) ou
   **fora** (> 30 cm) da especificação.
4. Se **mais de 30%** das 50 leituras estiverem fora → o CrewAI gera um
   relatório técnico para a **sustentação**.
5. Caso contrário → o CrewAI gera um relatório executivo para a
   **direção**, destacando os impactos positivos.
6. O relatório é exibido no dashboard, junto com um indicador visual de
   para qual setor ele foi direcionado.