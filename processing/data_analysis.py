import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

def load_data(file_path):
    #evitar sobrecarga
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        if len(df) > 100000:
            df = df.head(100000)
            
        df.columns = df.columns.str.lower()
        
        return df
    else:
        print(f"Arquivo não encontrado: {file_path}")
        return None

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
    if "keyword" in df.columns and "views" in df.columns:
        category_views = df.groupby("keyword")["views"].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(25, 10))
        sns.barplot(x=category_views.index, y=category_views.values, ax=ax, palette="Blues_r")
        st.write(f"### Média de Views por Tipo de Vídeo")
        ax.set_xlabel("Categoria (keyword)")
        ax.set_ylabel("Média de Views")
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)
    else:
        st.write("Erro nas colunas 'keyword' e 'views' para análise.")

def show_top_videos(df, top_n=10):
    if "title" in df.columns and "views" in df.columns:
        top_videos = df.nlargest(top_n, "views")[["title", "views"]]
        st.write(f"### Top {top_n} Vídeos Mais Populares")
        st.dataframe(top_videos)
    else:
        st.write("Erro nas colunas 'title' e 'views' para análise.")


