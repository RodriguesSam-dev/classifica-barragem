import streamlit as st
import pandas as pd
import random

# Configuração da página
st.set_page_config(page_title="Ranking de Barragens", layout="centered")

st.title("Avaliação e Ranking de Barragens")
st.write("Ajude-nos a classificar o nível de risco dessas estruturas usando seu senso comum.")

# 1. Base de dados simulada (No mundo real, você leria do Excel ou Google Sheets)
# Usamos o st.cache_data para não recriar a base toda vez que a tela atualizar
@st.cache_data
def carregar_dados():
    return pd.read_csv("dados_barragens.csv")

df_barragens = carregar_dados()

# 2. Gerenciamento de Estado (Para não perder o sorteio se a pessoa clicar na tela)
if 'sorteio_realizado' not in st.session_state:
    st.session_state.sorteio_realizado = False
    st.session_state.barragens_sorteadas = pd.DataFrame()

# ==========================================
# PASSO A: ESCOLHA DA QUANTIDADE E SORTEIO
# ==========================================
st.divider()
st.subheader("1. Quantas barragens você quer avaliar?")
qtd = st.number_input("Escolha um número (máximo 10):", min_value=2, max_value=10, value=3)

if st.button("Sortear Minhas Barragens"):
    # Faz o sorteio aleatório
    st.session_state.barragens_sorteadas = df_barragens.sample(n=qtd).reset_index(drop=True)
    st.session_state.sorteio_realizado = True

# ==========================================
# PASSO B: EXIBIÇÃO E RANKING (Só aparece após o sorteio)
# ==========================================
if st.session_state.sorteio_realizado:
    st.success(f"{qtd} Barragens sorteadas com sucesso!")
    
    st.subheader("2. Material de Apoio e Fichas")
    st.markdown("[📘 **Clique aqui para ler o Manual de Classificação**](https://drive.google.com/file/d/10p8Z2BRxSa1o03oPqhKkvScYju3kmAY5/view?usp=drive_link)")
    st.write("Abaixo estão as fichas das barragens sorteadas para você. Abra os links para analisar:")
    
    # Exibe as barragens sorteadas e seus links
    for index, row in st.session_state.barragens_sorteadas.iterrows():
        st.write(f"- **{row['ID_Barragem']}**: [Abrir Ficha Técnica]({row['Link_Ficha']})")

    st.divider()
    
    st.subheader("3. Monte o seu Ranking")
    st.write("Selecione as barragens abaixo, **da MAIS perigosa para a MENOS perigosa**.")
    st.caption("A primeira que você clicar será a 1ª do ranking (Mais perigosa).")
    
    ids_sorteados = st.session_state.barragens_sorteadas['ID_Barragem'].tolist()
    
    # O multiselect do Streamlit retorna a lista na ordem em que o usuário clicou
    ranking = st.multiselect(
        "Selecione a ordem de periculosidade:",
        options=ids_sorteados,
        max_selections=qtd
    )
    
    # Mostrar visualmente o ranking sendo formado em tempo real
    if ranking:
        st.write("**Seu ranking atual:**")
        for i, nome_barragem in enumerate(ranking):
            if i == 0:
                st.error(f"1º - {nome_barragem} (Mais Perigosa)")
            elif i == len(ids_sorteados) - 1 and len(ranking) == qtd:
                st.success(f"{i+1}º - {nome_barragem} (Menos Perigosa)")
            else:
                st.warning(f"{i+1}º - {nome_barragem}")

    # ==========================================
    # PASSO C: ENVIO DOS DADOS
    # ==========================================
    # Só libera o botão de envio se o usuário ranqueou todas as barragens sorteadas
    if len(ranking) == qtd:
        if st.button("Enviar Avaliação", type="primary"):
            # Aqui entraria a lógica para salvar no Google Sheets ou Banco de Dados
            # Ex: salvar_no_banco(usuario, ranking)
            
            st.balloons()
            st.success("Avaliação enviada com sucesso! Muito obrigado pela ajuda.")
            
            # Limpa o estado para permitir uma nova avaliação
            st.session_state.sorteio_realizado = False