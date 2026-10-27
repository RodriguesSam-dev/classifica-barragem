import streamlit as st
import pandas as pd
import random
import requests

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
    st.info("💡 **Nota:** As informações contendo 'valor provável' e 'categoria mais provável' eram desconhecidas e foram obtidas por ajuste.")
    
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
    st.divider()
    st.subheader("4. Finalizar e Enviar")

    # Só libera o botão de envio quando a pessoa ranquear TODAS as barragens sorteadas
    if len(ranking) == qtd:
        if st.button("Enviar Avaliação", type="primary"):
            
            # 1. Prepara o texto do ranking (Ex: 1º 24206 | 2º 35208)
            texto_ranking = " | ".join([f"{i+1}º {b}" for i, b in enumerate(ranking)])
            
            # 2. Configura a URL e os Dados do Formulário (Envia "Anônimo" no campo de nome)
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSfjKdWMmwLk4Z_P6fWFghLngJgs_cIOpot4jdFGZrF43dg_Hw/formResponse"
            
            dados = {
                "entry.461828907": "Anônimo",
                "entry.1313851568": texto_ranking
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            
            # 3. Envia os dados silenciosamente
            try:
                # O parâmetro allow_redirects=True garante que o Python segue a confirmação do Forms
                resposta = requests.post(url_form, data=dados, headers=headers, allow_redirects=True)
                
                # Códigos 200 (OK) e 302 (Redirecionamento) indicam sucesso no envio do Google Forms
                if resposta.status_code in [200, 302]:
                    st.balloons()
                    st.success("Avaliação enviada com sucesso! Muito obrigado pela ajuda.")
                    st.session_state.sorteio_realizado = False
                else:
                    st.error(f"Erro ao salvar dados (Código: {resposta.status_code}).")
                
            except Exception as e:
                st.error(f"Houve um erro de conexão: {e}")
    else:
        st.info("Selecione todas as barragens no ranking acima para liberar o botão de envio.")
