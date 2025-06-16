import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os
import statsmodels.api as sm

def load_data(file_path, max_rows=10000):
    df = pd.read_csv(file_path, nrows=max_rows)
    # Se veio com índice extra
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    # normalize colunas
    df.columns = df.columns.str.lower()
    # trending_date é yy.dd.mm → converte para datetime
    df['trending_date'] = pd.to_datetime(
        df['trending_date'], format='%y.%d.%m', errors='coerce'
    )
    # publish_time: remove Z e parse
    if 'publish_time' in df.columns:
        df['publish_time'] = pd.to_datetime(
            df['publish_time'].str.rstrip('Z'), errors='coerce'
        )
    return df

    
def load_category_mapping(csv_file):
    json_file = os.path.join("data", f"{csv_file[:2]}_category_id.json")
    print(json_file)
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        category_mapping = {item["id"]: item["snippet"]["title"] for item in data.get("items", [])}
        return category_mapping
    else:
        print(f"Arquivo JSON de categorias não encontrado: {json_file}")
        return {}

def merge_categories(df, csv_file):
    # Ex: 'USvideos.csv' → data/US_category_id.json
    prefix = os.path.basename(csv_file).split('videos')[0]
    mapping_file = os.path.join('data', f'{prefix}_category_id.json')
    with open(mapping_file, 'r', encoding='utf-8') as f:
        items = json.load(f).get('items', [])
    cmap = {int(i['id']): i['snippet']['title'] for i in items}

    df['category_id'] = df['category_id'].astype(int)
    df['category_name'] = df['category_id'].map(cmap).fillna('Desconhecido')
    return df


def calculate_null_zero_percentage(df):
    #Calcula o percentual de valores nulos e zeros.
    if df is None:
        return None, None
    total_values = df.size
    null_values = df.isnull().sum().sum()
    zero_values = (df == 0).sum().sum()
    null_percentage = (null_values / total_values) * 100
    zero_percentage = (zero_values / total_values) * 100
    return null_percentage, zero_percentage

def plot_missing_values(df):
    #Gera um gráfico de barras mostrando valores nulos por coluna.
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]

    if not missing_values.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=missing_values.index, y=missing_values.values, ax=ax, hue=missing_values.index, palette="Reds")
        st.write(f"### Valores Nulos por Coluna")
        ax.set_ylabel("Quantidade")
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)
    else:
        st.write(f"### Valores Nulos por Coluna")
        st.write("Nenhuma coluna contém valores nulos!")

def plot_numeric_distribution(df):
    #Exibe a distribuição das variáveis numéricas.
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        fig, ax = plt.subplots(len(numeric_cols), 1, figsize=(10, len(numeric_cols) * 5))

        for i, col in enumerate(numeric_cols):
            sns.histplot(df[col].dropna(), bins=20, kde=True, ax=ax[i], color="blue")
            ax[i].set_title(f"Distribuição de {col}")

        st.pyplot(fig)
    else:
        st.write("Nenhuma coluna numérica disponível para análise!")
        
def plot_regression_likes_views(df):
    #Realiza uma regressão linear entre views e likes e exibe o gráfico com a reta ajustada.
    if "views" in df.columns and "likes" in df.columns:
        df_filtered = df[(df["views"] > 0) & (df["likes"] > 0)].copy()
        #df_filtered = df_filtered.sample(min(5000, len(df_filtered)))  # Amostra para melhorar performance
        
        X = sm.add_constant(df_filtered["views"])
        y = df_filtered["likes"]
        model = sm.OLS(y, X).fit()
        
        intercept, slope = model.params
        r_squared = model.rsquared

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.regplot(x=df_filtered["views"], y=df_filtered["likes"], ax=ax, scatter_kws={"s": 10}, line_kws={"color": "red"})
        ax.set_xlabel("Views")
        ax.set_ylabel("Likes")

        st.write(f"### Regressão Linear: Likes vs Views (R² = {r_squared:.4f})")
        st.pyplot(fig)

        st.write(f"**Equação da regressão:** Likes = {intercept:.2f} + {slope:.6f} × Views")
        st.write(f"**Coeficiente de determinação (R²):** {r_squared:.4f}")
    else:
        st.write("Erro: As colunas 'views' e 'likes' são necessárias para essa análise.")
        
def plot_regression_like_rate_vs_views(df):
    #Realiza uma regressão linear entre views e taxa de likes (likes/views)
    if "views" in df.columns and "likes" in df.columns:
        df_filtered = df[(df["views"] > 0) & (df["likes"] > 0)].copy()
        
        df_filtered["like_rate"] = df_filtered["likes"] / df_filtered["views"]

        # Remover outliers (taxas muito altas, acima de 0.2 = 20%)
        df_filtered = df_filtered[df_filtered["like_rate"] < 0.2]

        X = sm.add_constant(df_filtered["views"])
        y = df_filtered["like_rate"]
        model = sm.OLS(y, X).fit()
        
        intercept, slope = model.params
        r_squared = model.rsquared

        # Plot da regressão
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.regplot(x=df_filtered["views"], y=df_filtered["like_rate"], ax=ax, scatter_kws={"s": 10}, line_kws={"color": "red"})
        ax.set_xlabel("Views")
        ax.set_ylabel("Taxa de Likes (Likes / Views)")

        st.write(f"### Regressão Linear: Taxa de Likes vs Views (R² = {r_squared:.4f})")
        st.pyplot(fig)

        st.write(f"**Equação da regressão:** Taxa de Likes = {intercept:.6f} + {slope:.12f} × Views")
        st.write(f"**Coeficiente de determinação (R²):** {r_squared:.4f}")
    else:
        st.write("Erro: As colunas 'views' e 'likes' são necessárias para essa análise.")
        
def plot_views_vs_likes(df, num_bins=10):
    #Agrupa views em faixas e exibe a média de likes para cada faixa.
    if "views" in df.columns and "likes" in df.columns:
        df_filtered = df[df["views"] > 0]  # Remover possíveis valores zero/nulos
        df_filtered["view_bins"] = pd.qcut(df_filtered["views"], num_bins, duplicates="drop")

        grouped_data = df_filtered.groupby("view_bins")["likes"].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=grouped_data["view_bins"].astype(str), y=grouped_data["likes"], ax=ax, palette="Purples_r")
        st.write(f"### Média de Likes por Faixa de Views")
        ax.set_xlabel("Faixa de Views")
        ax.set_ylabel("Média de Likes")
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)
    else:
        st.write("As colunas 'views' e 'likes' são necessárias para esse gráfico.")

        
def plot_views_by_category(df):
    if 'category_name' not in df.columns:
        st.error("Rode primeiro merge_categories para criar 'category_name'.")
        return
    agg = df.groupby('category_name')['views'].mean().sort_values(ascending=False)
    st.write("### Média de Views por Categoria")
    st.bar_chart(agg)  # Mais leve que seaborn para muitas categorias


def show_top_videos(df, top_n=10):
    if "title" in df.columns and "views" in df.columns:
        top_videos = df.nlargest(top_n, "views")[["title", "views"]]
        st.write(f"### Top {top_n} Vídeos Mais Populares")
        st.dataframe(top_videos)
    else:
        st.write("Erro nas colunas 'title' e 'views' para análise.")


