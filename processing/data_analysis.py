import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

def load_data(file_path):
    """Carrega os dados do arquivo CSV."""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        print(f"Arquivo não encontrado: {file_path}")
        return None

def calculate_null_zero_percentage(df):
    """Calcula o percentual de valores nulos e zeros."""
    if df is None:
        return None, None
    total_values = df.size
    null_values = df.isnull().sum().sum()
    zero_values = (df == 0).sum().sum()
    null_percentage = (null_values / total_values) * 100
    zero_percentage = (zero_values / total_values) * 100
    return null_percentage, zero_percentage

def plot_missing_values(df):
    """Gera um gráfico de barras mostrando valores nulos por coluna."""
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]

    if not missing_values.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=missing_values.index, y=missing_values.values, ax=ax, palette="Reds")
        ax.set_title("Valores Nulos por Coluna")
        ax.set_ylabel("Quantidade")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.write("Nenhuma coluna contém valores nulos!")

def plot_numeric_distribution(df):
    """Exibe a distribuição das variáveis numéricas."""
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        fig, ax = plt.subplots(len(numeric_cols), 1, figsize=(10, len(numeric_cols) * 3))

        for i, col in enumerate(numeric_cols):
            sns.histplot(df[col].dropna(), bins=20, kde=True, ax=ax[i], color="blue")
            ax[i].set_title(f"Distribuição de {col}")

        st.pyplot(fig)
    else:
        st.write("Nenhuma coluna numérica disponível para análise!")
