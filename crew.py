from crewai import Agent, Task, Crew


# ==============================
# RELATÓRIO PARA A SUSTENTAÇÃO
# (dados FORA da especificação)
# ==============================

def _gerar_relatorio_sustentacao(alturas, estatisticas):

    analista = Agent(
        role="Analista Técnico de Sustentação",

        goal="""
        Identificar situações de vegetação fora do padrão de
        segurança próxima a rodovias e alertar a equipe de
        sustentação sobre a necessidade de intervenção.
        """,

        backstory="""
        Você é responsável por dar suporte técnico à equipe de
        sustentação/manutenção. Você recebe medições de altura
        de vegetação coletadas por um sensor instalado próximo
        à rodovia e precisa transformar isso em um alerta claro,
        objetivo e acionável para quem vai até o local resolver
        o problema.

        Seu público é técnico: quer saber o que está errado,
        o quão grave é, e o que fazer a respeito.
        """,

        verbose=True
    )

    tarefa = Task(
        description=f"""
        Foram coletadas {estatisticas["quantidade"]} medições de
        altura de vegetação (em cm) próximas a uma rodovia.

        Alturas coletadas:
        {alturas}

        Limite de especificação: {estatisticas["limite_especificacao"]} cm
        (acima disso é considerado FORA da especificação)

        Estatísticas:
        - Altura mínima: {estatisticas["minima"]} cm
        - Altura máxima: {estatisticas["maxima"]} cm
        - Altura média: {estatisticas["media"]} cm
        - Mediana: {estatisticas["mediana"]} cm
        - Medições DENTRO da especificação: {estatisticas["qtd_dentro_espec"]}
        - Medições FORA da especificação: {estatisticas["qtd_fora_espec"]}
        - Percentual fora da especificação: {estatisticas["percentual_fora"]}%

        A análise em Python já identificou que este lote está
        FORA da especificação (percentual de medições acima do
        limite superou o tolerado). Portanto, este relatório deve
        ser direcionado à EQUIPE DE SUSTENTAÇÃO.

        Com base nesses dados:

        1. Apresente a situação identificada de forma clara e direta.
        2. Explique a gravidade com base nos números (percentual fora,
           altura máxima atingida, quantas medições ultrapassaram o limite).
        3. Classifique a urgência como: Baixa, Média ou Alta.
        4. Recomende ações corretivas objetivas (ex: poda, inspeção,
           reforço de manutenção na área).
        5. Produza um resumo final para quem for até o local resolver.

        IMPORTANTE:
        - Utilize somente os dados fornecidos.
        - Não invente medições nem informações sobre a área.
        - O tom deve ser técnico e direto, focado em ação.
        """,

        expected_output="""
        Relatório estruturado contendo:

        SITUAÇÃO IDENTIFICADA

        DADOS QUE FUNDAMENTAM O ALERTA

        NÍVEL DE URGÊNCIA

        AÇÕES RECOMENDADAS

        RESUMO PARA A EQUIPE DE SUSTENTAÇÃO
        """,

        agent=analista
    )

    crew = Crew(
        agents=[analista],
        tasks=[tarefa],
        verbose=True
    )

    resultado = crew.kickoff()

    return str(resultado)


# ==============================
# RELATÓRIO PARA A DIREÇÃO
# (dados DENTRO da especificação)
# ==============================

def _gerar_relatorio_direcao(alturas, estatisticas):

    analista = Agent(
        role="Analista de Performance Operacional",

        goal="""
        Traduzir os dados de monitoramento de vegetação em um
        relatório executivo para a direção, destacando os
        impactos positivos da operação dentro do padrão.
        """,

        backstory="""
        Você prepara relatórios executivos para a diretoria da
        empresa. Seu público não é técnico: quer entender, de
        forma resumida, que a operação está sob controle e quais
        são os ganhos/benefícios de manter os indicadores dentro
        da especificação (segurança, custo evitado, eficiência).

        Você também pode citar pontos de atenção pontuais, mas
        sempre no contexto de que a situação geral está sob
        controle.
        """,

        verbose=True
    )

    tarefa = Task(
        description=f"""
        Foram coletadas {estatisticas["quantidade"]} medições de
        altura de vegetação (em cm) próximas a uma rodovia.

        Alturas coletadas:
        {alturas}

        Limite de especificação: {estatisticas["limite_especificacao"]} cm
        (acima disso é considerado fora da especificação)

        Estatísticas:
        - Altura mínima: {estatisticas["minima"]} cm
        - Altura máxima: {estatisticas["maxima"]} cm
        - Altura média: {estatisticas["media"]} cm
        - Mediana: {estatisticas["mediana"]} cm
        - Medições dentro da especificação: {estatisticas["qtd_dentro_espec"]}
        - Medições fora da especificação: {estatisticas["qtd_fora_espec"]}
        - Percentual fora da especificação: {estatisticas["percentual_fora"]}%

        A análise em Python já identificou que este lote está
        DENTRO da especificação (percentual de medições acima do
        limite ficou dentro do tolerado). Portanto, este relatório
        deve ser direcionado à DIREÇÃO, destacando os impactos
        positivos.

        Com base nesses dados:

        1. Apresente um resumo executivo da situação (curto e claro).
        2. Destaque os impactos positivos: segurança da via,
           redução de risco, custo evitado com manutenção corretiva,
           eficiência do monitoramento automatizado.
        3. Caso existam medições fora da especificação (mesmo que
           poucas), mencione como um ponto de atenção/alerta leve,
           sem alarmismo, já que o quadro geral está sob controle.
        4. Produza um resumo final objetivo, em tom executivo.

        IMPORTANTE:
        - Utilize somente os dados fornecidos.
        - Não invente medições nem informações sobre a área.
        - O tom deve ser executivo, direto e positivo, sem jargão técnico.
        """,

        expected_output="""
        Relatório estruturado contendo:

        RESUMO EXECUTIVO

        IMPACTOS POSITIVOS

        INDICADORES

        PONTOS DE ATENÇÃO (se houver)

        RESUMO PARA A DIREÇÃO
        """,

        agent=analista
    )

    crew = Crew(
        agents=[analista],
        tasks=[tarefa],
        verbose=True
    )

    resultado = crew.kickoff()

    return str(resultado)


# ==============================
# FUNÇÃO PRINCIPAL (usada pelo mqtt.py)
# ==============================

def gerar_relatorio(alturas, estatisticas):

    destino = estatisticas.get("destino", "direcao")

    if destino == "sustentacao":
        return _gerar_relatorio_sustentacao(alturas, estatisticas)

    return _gerar_relatorio_direcao(alturas, estatisticas)