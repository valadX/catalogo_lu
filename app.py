import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Lanbele Decorações", layout="wide", page_icon="🎈")

# ==========================================
# --- PERSONALIZAÇÃO VISUAL (CSS) ---
# ==========================================
st.markdown("""
    <style>
    /* 1. Cor de Fundo Principal (Roxo) e Texto Base (Branco) */
    .stApp {
        background-color: #5e2d79; 
        color: #ffffff; 
    }
    
    /* 2. Ajustes para Caixas e Botões */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: #ffffff30 !important; 
        background-color: #ffffff10; 
    }
    input[type="text"] {
        color: #31333F !important; 
    }
    /* Cor dos textos dos filtros */
    label {
        color: #ffffff !important;
        font-weight: bold;
    }
    h1, h2, h3, p, h4 {
        color: #ffffff !important;
    }
    /* Cor dos links e ícones da sidebar */
    .st-emotion-cache-6qob1r, .st-emotion-cache-10trblm {
        color: #ffffff !important;
    }
    /* Estilo do botão de download */
    .stDownloadButton button {
        background-color: #ffffff20;
        color: white;
        border: 1px solid white;
    }
    .stDownloadButton button:hover {
        background-color: white;
        color: #5e2d79;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# --- LOGO CENTRALIZADO ---
# ==========================================
logo_url = "https://lanbele.com.br/wp-content/uploads/2025/09/IMG-20250920-WA0029-1024x585.png"

col_esq, col_centro, col_dir = st.columns([1, 4, 1])

with col_centro:
    try:
        st.image(logo_url, use_container_width=True)
    except:
        st.error("Não foi possível carregar o logo.")
        st.title("Catálogo Lanbele")

st.write("") 

# ==========================================
# --- LÓGICA DO APP ---
# ==========================================

def salvar_alteracoes(df_novo, nome_arquivo):
    df_novo.to_csv(nome_arquivo, index=False)
    st.toast("✅ Alterações salvas!", icon="💾")

# --- CARREGAMENTO ---
arquivo_csv = 'base_dados_inteligente.csv'
if not os.path.exists(arquivo_csv):
    arquivo_csv = 'base_dados.csv'

if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
    
    if 'oculto' not in df.columns:
        df['oculto'] = False
        df.to_csv(arquivo_csv, index=False)

    df['legenda'] = df['legenda'].fillna("") 

    # --- BARRA LATERAL ---
    st.sidebar.title("⚙️ Filtros & Ajustes")
    
    # 1. Filtro de Cor (Voltou para a lateral)
    filtro_cor = "Todas"
    if 'cor_predominante' in df.columns:
        lista_cores = sorted([c for c in df['cor_predominante'].unique() if isinstance(c, str)])
        cores_disponiveis = ["Todas"] + lista_cores
        filtro_cor = st.sidebar.selectbox("🎨 Filtrar por Cor", cores_disponiveis)
    
    st.sidebar.divider()
    
    # 2. Configurações
    modo_edicao = st.sidebar.toggle("✏️ Modo Edição", value=False)
    mostrar_sem_legenda = st.sidebar.checkbox("⚠️ Sem legenda", value=False)
    ver_lixeira = st.sidebar.checkbox("🗑️ Lixeira", value=False)

    # ==========================================
    # --- ÁREA DE BUSCA (PRINCIPAL - LIMPA) ---
    # ==========================================
    
    with st.container():
        st.markdown("### 🔍 O que você procura hoje?")
        # Apenas a barra de busca agora
        busca = st.text_input("Digite o tema (ex: Sereia, Heróis)", placeholder="Pesquise aqui...")

    st.divider()

    # --- FILTRAGEM ---
    resultados = df.copy()

    if ver_lixeira:
        resultados = resultados[resultados['oculto'] == True]
        st.markdown("""
            <div style='padding: 10px; background-color: #ff4b4b; color: white; border-radius: 5px; margin-bottom: 10px;'>
            🗑️ <b>LIXEIRA:</b> Esses itens estão ocultos do cliente.
            </div>
        """, unsafe_allow_html=True)
    else:
        resultados = resultados[resultados['oculto'] == False]

    if not ver_lixeira and mostrar_sem_legenda:
        resultados = resultados[resultados['legenda'].astype(str).str.len() < 3]
    
    if not mostrar_sem_legenda:
        if busca:
            resultados = resultados[resultados['legenda'].astype(str).str.contains(busca, case=False, na=False)]
        if filtro_cor != "Todas":
            resultados = resultados[resultados['cor_predominante'] == filtro_cor]

    resultados['existe'] = resultados['caminho_imagem'].apply(os.path.exists)
    resultados = resultados[resultados['existe'] == True]

    # --- GALERIA ---
    
    # CONTADOR
    qtd = len(resultados)
    if qtd > 0:
        st.markdown(f"##### 🎉 Encontramos **{qtd}** opções")
    else:
        st.info("Nenhuma decoração encontrada com esses filtros.")

    if qtd > 0:
        cols = st.columns(3)
        
        for index_real, row in resultados.iterrows():
            col_atual = cols[index_real % 3]
            
            with col_atual:
                with st.container(): 
                    st.markdown('<div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
                    
                    try:
                        st.image(row['caminho_imagem'], use_container_width=True)
                        
                        legenda_atual = str(row['legenda'])
                        
                        if modo_edicao:
                            # --- MODO EDIÇÃO ---
                            st.markdown("📝 **Editar:**")
                            nova_legenda = st.text_input("Nome", value=legenda_atual, key=f"input_{index_real}", label_visibility="collapsed")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("💾 Salvar", key=f"save_{index_real}"):
                                    df.at[index_real, 'legenda'] = nova_legenda
                                    salvar_alteracoes(df, arquivo_csv)
                                    st.rerun()
                            with c2:
                                if ver_lixeira:
                                    if st.button("♻️ Restaurar", key=f"rest_{index_real}"):
                                        df.at[index_real, 'oculto'] = False
                                        salvar_alteracoes(df, arquivo_csv)
                                        st.rerun()
                                else:
                                    if st.button("🗑️ Ocultar", key=f"del_{index_real}", type="primary"):
                                        df.at[index_real, 'oculto'] = True
                                        salvar_alteracoes(df, arquivo_csv)
                                        st.rerun()
                        else:
                            # --- MODO CLIENTE ---
                            if len(legenda_atual) < 3:
                                st.error("⚠️ SEM NOME")
                            else:
                                st.markdown(f"<h4 style='color: white; margin-top: 10px;'>{legenda_atual}</h4>", unsafe_allow_html=True)
                            
                            if 'cor_predominante' in row:
                                st.caption(f"🎨 {row['cor_predominante']}")
                            
                            # Botões
                            b1, b2 = st.columns([1, 1])
                            with b1:
                                if pd.notna(row['url_instagram']):
                                    st.link_button("Ver no Insta 🔗", row['url_instagram'])
                            with b2:
                                with open(row['caminho_imagem'], "rb") as file:
                                    btn = st.download_button(
                                        label="⬇️ Baixar",
                                        data=file,
                                        file_name=os.path.basename(row['caminho_imagem']),
                                        mime="image/jpeg",
                                        key=f"dl_{index_real}"
                                    )

                    except Exception as e:
                        st.error(f"Erro: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Arquivo de dados não encontrado.")