import pandas as pd
import requests


def extrair_dados_wb(indicador, nome_coluna, anos="2010:2024"):
    """Faz a requisição para a API do Banco Mundial e retorna um DataFrame."""
    url = f"http://api.worldbank.org/v2/country/all/indicator/{indicador}"
    params = {"date": anos, "format": "json", "per_page": 20000}

    resposta = requests.get(url, params=params)

    if resposta.status_code == 200:
        dados_json = response_data = resposta.json()
        if len(dados_json) > 1:
            registros = dados_json[1]
            lista_dados = []
            for reg in registros:
                lista_dados.append(
                    {
                        "pais_id": reg["country"]["id"],
                        "pais": reg["country"]["value"],
                        "ano": int(reg["date"]),
                        nome_coluna: reg["value"],
                    }
                )
            return pd.DataFrame(lista_dados)
    return pd.DataFrame()


def gerar_base_local():
    print("Iniciando coleta de dados da API do Banco Mundial...")

    # Extraindo os indicadores cruciais
    df_gdp = extrair_dados_wb("NY.GDP.PCAP.CD", "pib_per_capita")
    df_edu = extrair_dados_wb("SE.XPD.TOTL.GD.ZS", "investimento_educacao")

    if not df_gdp.empty and not df_edu.empty:
        # Unindo as tabelas com base no país e ano
        df_final = pd.merge(df_gdp, df_edu, on=["pais_id", "pais", "ano"])

        print("Limpando e filtrando dados...")

        # 1. Remove linhas onde os valores principais são nulos ao mesmo tempo
        df_final = df_final.dropna(
            subset=["pib_per_capita", "investimento_educacao"], how="all"
        )

        # 2. Lista de termos que o Banco Mundial usa para agregados regionais/econômicos
        termos_regioes = [
            "total",
            "aggregates",
            "world",
            "africa",
            "america",
            "asia",
            "euro",
            "income",
            "demographic",
            "east",
            "west",
            "south",
            "north",
            "central",
            "caribbean",
            "pacific",
        ]

        # Filtra mantendo apenas o que NÃO contém esses termos no nome do país
        for termo in termos_regioes:
            df_final = df_final[
                ~df_final["pais"].str.contains(termo, case=False, na=False)
            ]

        # Salvando localmente
        df_final.to_csv("dados/dados_banco_mundial.csv", index=False)
        print(f"Sucesso! {len(df_final)} linhas de dados foram salvas.")
    else:
        print("Erro: Não foi possível obter dados da API.")


if __name__ == "__main__":
    gerar_base_local()