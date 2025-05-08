import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import pandas as pd
import fitz  # PyMuPDF
from datetime import datetime

# ========== CONFIGURAÇÕES INICIAIS ==========

# Defina diretamente a chave da API aqui:
groq_api_key = "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"

st.set_page_config(page_title="Assistente de Sustentabilidade", layout="wide")
st.title("🌱 Assistente de Sustentabilidade")
st.markdown("**Explicações técnicas, sustentáveis e organizadas com IA.**")

# ========== TEMPLATE DO ASSISTENTE ========== 
ASSISTENTE_PROMPT = """
Você é um assistente técnico em sustentabilidade. Sua função é organizar, resumir e transformar explicações
em orientações objetivas e úteis. Elabore com clareza e precisão.
Base fornecida:
{entrada}
Assistente:
"""

# ========== CARREGAR MODELO ========== 
@st.cache_resource
def carregar_modelo(model_name="llama-3.3-70b-versatile"):
    return ChatGroq(api_key=groq_api_key, model_name=model_name)

modelo = carregar_modelo()
prompt_template = PromptTemplate(input_variables=["entrada"], template=ASSISTENTE_PROMPT.strip())

# ========== HISTÓRICO ========== 
if "historico" not in st.session_state:
    st.session_state.historico = []

# ========== UPLOAD DE ARQUIVOS ========== 
st.sidebar.markdown("### 📎 Upload de arquivos (PDF ou CSV)")
uploaded_file = st.sidebar.file_uploader("Envie um arquivo", type=["pdf", "csv"])
conteudo_arquivo = ""

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        conteudo_arquivo = "\n".join([page.get_text() for page in doc])
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        conteudo_arquivo = df.to_string(index=False)
    st.sidebar.success("Arquivo carregado com sucesso!")

# ========== ENTRADA DO USUÁRIO ========== 
user_input = st.text_area("Digite sua dúvida ou tema sobre sustentabilidade:", height=200)

entrada_completa = user_input
if conteudo_arquivo:
    entrada_completa += f"\n\nBase do arquivo:\n{conteudo_arquivo}"

# ========== EXECUÇÃO ========== 
if st.button("🔎 Obter Resposta"):
    if not user_input.strip():
        st.warning("Digite uma pergunta ou tema antes de continuar.")
    else:
        with st.spinner("Analisando com inteligência sustentável..."):
            prompt = prompt_template.format(entrada=entrada_completa)
            resposta = modelo.invoke(prompt).content.strip()

            # Mostrar resposta
            st.success("Resposta do Assistente:")
            st.markdown(resposta)

            # Salvar histórico
            horario = datetime.now().strftime("%d/%m %H:%M")
            st.session_state.historico.append((horario, user_input, resposta))

# ========== EXPORTAR COMO .TXT ========== 
st.sidebar.markdown("### 💾 Exportar como .txt")
if st.sidebar.button("Exportar Histórico"):
    if st.session_state.historico:
        conteudo_txt = "\n\n".join(
            [f"[{hora}] PERGUNTA:\n{pergunta}\n\nRESPOSTA:\n{resposta}" for hora, pergunta, resposta in st.session_state.historico]
        )
        st.sidebar.download_button("📥 Baixar .txt", conteudo_txt, file_name="historico_sustentabilidade.txt")
    else:
        st.sidebar.warning("Nenhum histórico encontrado para exportar.")

# ========== VISUALIZAR HISTÓRICO ========== 
st.sidebar.markdown("### 🕓 Histórico da Sessão")
for hora, pergunta, resposta in reversed(st.session_state.historico[-5:]):
    st.sidebar.markdown(f"**{hora}**")
    st.sidebar.markdown(f"📌 {pergunta[:80]}...")
