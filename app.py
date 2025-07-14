import streamlit as st

# ==============================================================================
# LÓGICA DO JOGO - Esta função é exatamente a mesma da versão anterior.
# ==============================================================================
def determinar_ranking_ajustado(jogadores_info):
    jogadores = [{"nome": j["nome"], "sequencia": j["sequencia"], "rank": None, "rodada_rank": None} for j in jogadores_info]
    relatorio_estruturado = []
    proximo_rank, rodada_atual, ultimo_rankeado = 1, 0, None

    while proximo_rank <= len(jogadores) and rodada_atual < 10:
        relatorio_estruturado.append({'type': 'round_header', 'text': f"--- Rodada {rodada_atual + 1} ---"})
        
        jogadores_na_disputa = [j for j in jogadores if j['rank'] is None]
        if not jogadores_na_disputa: break
        if len(jogadores_na_disputa) == 1:
            jogador = jogadores_na_disputa[0]
            jogador['rank'], jogador['rodada_rank'] = proximo_rank, rodada_atual + 1
            relatorio_estruturado.append({'type': 'analysis', 'text': f"Análise: {jogador['nome']} foi o último restante, ficando em {proximo_rank}º lugar."})
            break
        
        grupo_de_comparacao = list(jogadores_na_disputa)
        texto_referencia = ""
        if len(jogadores_na_disputa) == 2 and ultimo_rankeado:
            grupo_de_comparacao.append(ultimo_rankeado)
            texto_referencia = f" (com {ultimo_rankeado['nome']} como referência)"
        
        relatorio_estruturado.append({'type': 'info', 'text': f"Jogadores na disputa: {[j['nome'] for j in jogadores_na_disputa]}"})
        relatorio_estruturado.append({'type': 'info', 'text': f"Grupo de comparação: {[j['nome'] for j in grupo_de_comparacao]}{texto_referencia}"})
        jogadas = {j['nome']: j['sequencia'][rodada_atual] for j in grupo_de_comparacao}
        relatorio_estruturado.append({'type': 'info', 'text': f"Jogadas: {jogadas}"})

        contagem_zeros, contagem_uns = list(jogadas.values()).count('0'), list(jogadas.values()).count('1')
        jogada_minoritaria = None
        if contagem_zeros > 0 and contagem_uns > 0:
            if contagem_zeros < contagem_uns: jogada_minoritaria = '0'
            elif contagem_uns < contagem_zeros: jogada_minoritaria = '1'
        
        if jogada_minoritaria:
            relatorio_estruturado.append({'type': 'analysis', 'text': f"Análise: A jogada '{jogada_minoritaria}' foi a minoria no grupo de comparação."})
            jogadores_rankeados_rodada = []
            for jogador in jogadores_na_disputa:
                if jogador['sequencia'][rodada_atual] == jogada_minoritaria:
                    jogador['rank'], jogador['rodada_rank'] = proximo_rank, rodada_atual + 1
                    jogadores_rankeados_rodada.append(jogador)
            if jogadores_rankeados_rodada:
                nomes = " e ".join([j['nome'] for j in jogadores_rankeados_rodada])
                relatorio_estruturado.append({'type': 'winner', 'text': f"🏅 {nomes} conquistou o {proximo_rank}º lugar!"})
                ultimo_rankeado = jogadores_rankeados_rodada[0] if len(jogadores_rankeados_rodada) == 1 else None
                proximo_rank += len(jogadores_rankeados_rodada)
            else:
                 relatorio_estruturado.append({'type': 'analysis', 'text': "Análise: A minoria era o jogador de referência. Ninguém da disputa foi classificado."})
        else:
            relatorio_estruturado.append({'type': 'tie', 'text': "Análise: Empate na rodada. Nenhuma posição definida."})
        rodada_atual += 1

    jogadores_restantes = [j for j in jogadores if j['rank'] is None]
    if jogadores_restantes:
        relatorio_estruturado.append({'type': 'round_header', 'text': "--- Empate Irredutível ---"})
        for jogador in jogadores_restantes:
            jogador['rank'], jogador['rodada_rank'] = proximo_rank, "Empate Final"
    
    ranking_final = sorted([j for j in jogadores if j['rank'] is not None], key=lambda x: x['rank'])
    return ranking_final, relatorio_estruturado

# ==============================================================================
# INTERFACE DA APLICAÇÃO WEB COM STREAMLIT (COM VALIDAÇÃO MELHORADA)
# ==============================================================================

# Função auxiliar para validar uma única sequência
def validar_sequencia(sequencia):
    """Retorna uma mensagem de erro se a sequência for inválida, senão retorna None."""
    if not sequencia: # Ainda não foi preenchido
        return None
    if len(sequencia) > 10:
        return f"A sequência tem {len(sequencia)} dígitos. O máximo é 10."
    if not all(c in '01' for c in sequencia):
        return "A sequência deve conter apenas os números 0 e 1."
    return None

st.set_page_config(page_title="Rankeador Zero ou Um", page_icon="🏆", layout="centered")

st.title("🏆 Rankeador 'Zero ou Um'")
st.markdown("Insira os nomes e as sequências de 10 dígitos (0 ou 1) para cada jogador.")

if 'resultado' not in st.session_state:
    st.session_state.resultado = None

# Formulário para agrupar os campos e o botão de submit
with st.form("form_jogadores"):
    jogadores_input = []
    col1, col2 = st.columns(2)

    for i in range(4):
        col = col1 if i < 2 else col2
        with col:
            with st.container(border=True):
                nome = st.text_input(f"Nome do Jogador {i+1}", key=f"nome_{i}")
                
                # O campo de texto para a sequência agora não tem max_chars para podermos mostrar o erro de comprimento
                sequencia = st.text_input(f"Sequência para {nome or f'Jogador {i+1}'}", key=f"seq_{i}", placeholder="0101010101")
                
                # Feedback visual e instantâneo
                erro_msg = validar_sequencia(sequencia)
                if erro_msg:
                    st.caption(f"⚠️ {erro_msg}") # Mostra um aviso abaixo do campo

                jogadores_input.append({'nome': nome, 'sequencia': sequencia})

    submitted = st.form_submit_button("Determinar Ranking", type="primary", use_container_width=True)


if submitted:
    erros_finais = []
    jogadores_validos = []

    # Validação final antes de executar o jogo
    for i, j in enumerate(jogadores_input):
        nome = j['nome'] if j['nome'] else f"Jogador {i+1}"
        sequencia = j['sequencia']
        
        if len(sequencia) != 10:
            erros_finais.append(f"A sequência para '{nome}' deve ter exatamente 10 dígitos.")
        elif not all(c in '01' for c in sequencia):
             erros_finais.append(f"A sequência para '{nome}' contém caracteres inválidos.")
        else:
            jogadores_validos.append({'nome': nome, 'sequencia': j['sequencia']})

    if erros_finais:
        # Mostra todos os erros de uma vez
        for erro in erros_finais:
            st.error(f"❌ {erro}", icon="🚨")
        st.session_state.resultado = None # Limpa resultados antigos se houver erro
    else:
        # Se tudo estiver correto, executa a lógica do jogo
        ranking, relatorio = determinar_ranking_ajustado(jogadores_validos)
        st.session_state.resultado = {'ranking': ranking, 'relatorio': relatorio}


# Exibe os resultados se eles existirem no estado da sessão
if st.session_state.resultado:
    st.divider()
    st.subheader("🎉 Ranking Final 🎉")
    
    for jogador in st.session_state.resultado['ranking']:
        st.markdown(f"#### 🏅 **{jogador['rank']}º Lugar:** {jogador['nome']} `(Definido na Rodada {jogador['rodada_rank']})`")

    with st.expander("Clique aqui para ver o relatório detalhado do jogo"):
        for entrada in st.session_state.resultado['relatorio']:
            tipo = entrada.get('type')
            texto = entrada.get('text')
            
            if tipo == 'round_header': st.markdown(f"**{texto}**")
            elif tipo == 'winner': st.success(texto, icon="🏅")
            elif tipo == 'analysis': st.markdown(f"> *{texto}*")
            elif tipo == 'tie': st.warning(texto, icon="🤝")
            else: st.text(texto)