import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Educação e Desenvolvimento Global", layout="wide"
)


# Carga dos dados locais 
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados/dados_banco_mundial.csv")
    # Limpeza básica: remove linhas onde ambos os indicadores cruciais são nulos
    df = df.dropna(subset=["pib_per_capita", "investimento_educacao"], how="all")
    return df


df = carregar_dados()

# --- TÍTULO E INTRODUÇÃO ---
st.title("📊 Educação, Pobreza e Desenvolvimento Global")
st.markdown(
    """
    Este dashboard analisa a correlação entre o **Investimento Público em Educação (% do PIB)** 
    e o **Crescimento do PIB per capita**, focado em entender se o aporte em educação se traduz em 
    desenvolvimento econômico direto.
    
    *Dados obtidos via API pública do Banco Mundial.*
    """
)
st.sidebar.header("Filtros de Análise")

# --- TRATAMENTO PARA PAÍSES PADRÕES (Top 5 PIB no ano mais recente) ---
# Encontra o ano mais recente que possui dados de PIB para definir os países padrões
ano_max_dados = df.dropna(subset=["pib_per_capita"])["ano"].max()
df_ano_recente = df[df["ano"] == ano_max_dados]

# Seleciona os 4 países com maior PIB per capita naquele ano
top_4_paises = (
    df_ano_recente.nlargest(4, "pib_per_capita")["pais"].unique().tolist()
)

# Caso a lista venha vazia por algum motivo, definimos um fallback seguro
if not top_4_paises:
    top_4_paises = ["Brazil", "United States", "Finland"]

# --- ELEMENTOS INTERATIVOS ---

# Elemento Interativo 1: Seleção de Países (Multi-select)
paises_disponiveis = sorted(df["pais"].unique())

# Lista de padrões fixa e segura com nomes exatos da base do Banco Mundial
paises_padrao = ["Brazil", "United States", "Germany"]

# Uma validação simples para garantir que os nomes exatos existem na base
# Uma validação simples para garantir que os nomes exatos existem na base
paises_padrao_validados = [
    p for p in paises_padrao if p in paises_disponiveis
]
if not paises_padrao_validados:
    paises_padrao_validados = [paises_disponiveis[0]] if paises_disponiveis else []

paises_selecionados = st.sidebar.multiselect(
    "Selecione os Países para Comparação:",
    options=paises_disponiveis,
    default=paises_padrao_validados,  # Inicia com Brasil, EUA e Alemanha
)

# Elemento Interativo 2: Slider de Anos (Forçando o limite até 2025)
ano_min = int(df["ano"].min())
ano_max_limite = 2025  # Definido o teto em 2025

anos_selecionados = st.sidebar.slider(
    "Selecione o Intervalo de Anos:",
    min_value=ano_min,
    max_value=ano_max_limite,
    value=(2015, 2020),  # Começa pré-selecionado de 2015 até 2020
)

# Filtrando o DataFrame com as regras finais
df_filtrado = df[
    (df["pais"].isin(paises_selecionados))
    & (df["ano"] >= anos_selecionados[0])
    & (df["ano"] <= anos_selecionados[1])
]

# --- LAYOUT E MÉTRICAS (KPIs)  ---
st.subheader("📌 Métricas Gerais no Período Selecionado")
col1, col2, col3 = st.columns(3)

with col1:
    pib_medio = df_filtrado["pib_per_capita"].mean()
    st.metric(
        label="PIB per Capita Médio (USD)", value=f"${pib_medio:,.2f}"
    )

with col2:
    edu_media = df_filtrado["investimento_educacao"].mean()
    st.metric(
        label="Investimento Médio em Educação", value=f"{edu_media:.2f}% do PIB"
    )

with col3:
    st.metric(
        label="Total de Países Analisados", value=len(paises_selecionados)
    )

st.write("---")

# --- ANÁLISE EXPLORATÓRIA E VISUALIZAÇÃO ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📈 Tendência de Investimento em Educação")
    st.caption("Evolução do percentual do PIB investido em educação ao longo do tempo.")
    fig_linha = px.line(
        df_filtrado,
        x="ano",
        y="investimento_educacao",
        color="pais",
        labels={
            "ano": "Ano",
            "investimento_educacao": "Inves. em Educação (% do PIB)",
        },
        markers=True,
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with col_graf2:
    st.subheader("🔍 Correlação: Educação vs PIB per Capita")
    st.caption("O gráfico de dispersão ajuda a visualizar se mais investimentos geram maior riqueza.")
    fig_disp = px.scatter(
        df_filtrado,
        x="investimento_educacao",
        y="pib_per_capita",
        color="pais",
        hover_name="ano",
        labels={
            "investimento_educacao": "Investimento em Educação (% do PIB)",
            "pib_per_capita": "PIB per Capita (USD)",
        },
        trendline="ols",  # Adiciona linha de tendência para responder à pergunta-chave
    )
    st.plotly_chart(fig_disp, use_container_width=True)

# --- INSIGHTS ---
st.subheader("💡 Insights Analíticos")
# Exemplo de cálculo de correlação via Pandas 
if len(df_filtrado) > 5:
    correlacao = df_filtrado["investimento_educacao"].corr(
        df_filtrado["pib_per_capita"]
    )
    st.write(
        f"A correlação estatística de Pearson entre as duas variáveis para o grupo selecionado é de: **{correlacao:.2f}**"
    )
    if correlacao > 0.6:
        st.success(
            "Existe uma forte correlação positiva! Países que investem mais em educação tendem a apresentar maior PIB per capita no grupo selecionado."
        )
    elif correlacao < -0.6:
        st.warning(
            "Existe uma correlação negativa inesperada para este grupo de países."
        )
    else:
        st.info(
            "A correlação é fraca ou moderada. Isso indica que o crescimento do PIB per capita depende de um ecossistema de fatores mais amplo além do investimento isolado em educação (ou que o retorno desse investimento ocorre a longo prazo)."
        )
else:
    st.info("Selecione mais dados ou países para calcular a correlação estatística.")