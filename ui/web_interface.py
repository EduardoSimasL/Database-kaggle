import streamlit as st
from processing.data_analysis import (
    load_data, 
    calculate_null_zero_percentage, 
    plot_missing_values, 
    plot_numeric_distribution
)
from data.kaggle_service import download_dataset
from config.settings import load_kaggle_credentials

def main():
    st.title("📊 Análise de Dados Kaggle")

    # Configurar credenciais do Kaggle
    if load_kaggle_credentials():
        dataset_name = "advaypatil/youtube-statistics"
        download_path = "./data"
        
        if st.button("Baixar Dataset"):
            if download_dataset(dataset_name, download_path):
                st.success("Dataset baixado com sucesso!")

    file_path = f"{download_path}/videos-stats.csv"
    df = load_data(file_path)

    if df is not None:
        st.write("### Informações do Dataset")
        st.dataframe(df.head())

        # Exibir estatísticas básicas
        st.write("### Estatísticas Gerais")
        st.write(df.describe())

        # Exibir valores nulos e zeros
        null_percentage, zero_percentage = calculate_null_zero_percentage(df)
        st.write(f"Percentual de valores nulos: {null_percentage:.2f}%")
        st.write(f"Percentual de valores zero: {zero_percentage:.2f}%")

        # Mostrar gráficos
        st.write("### Valores Nulos por Coluna")
        plot_missing_values(df)

        st.write("### Distribuição das Variáveis Numéricas")
        plot_numeric_distribution(df)
    else:
        st.error("Erro ao carregar os dados.")

if __name__ == "__main__":
    main()
