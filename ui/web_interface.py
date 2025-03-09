import os
import streamlit as st
from processing.data_analysis import (
    load_data, 
    calculate_null_zero_percentage, 
    plot_missing_values, 
    plot_numeric_distribution,
    plot_views_vs_likes,
    plot_views_by_category,
    show_top_videos,
    merge_categories
)
from data.kaggle_service import download_dataset
from config.settings import load_kaggle_credentials
from config.logger import logger

def main():
    st.title("Análise de Dados Kaggle")
    df = None
    if load_kaggle_credentials():
        dataset_name = st.text_input("Digite o nome do dataset:", "advaypatil/youtube-statistics")
        download_path = "./data"

        if st.button("Baixar Dataset"):
            if download_dataset(dataset_name, download_path):
                logger.info(f"Dataset '{dataset_name}' baixado com sucesso em {download_path}")
                st.success(f"Dataset '{dataset_name}' baixado com sucesso!")
            else:
                st.error(f"Erro ao baixar o dataset '{dataset_name}'")

        csv_files = [f for f in os.listdir(download_path) if f.endswith('.csv')]
        
        if csv_files:
            selected_file = st.selectbox("Escolha o arquivo CSV para análise:", csv_files)
            file_path = os.path.join(download_path, selected_file)
            st.write(f"Você selecionou: {selected_file}")
            df = load_data(file_path)

    if df is not None:
        st.write("### Informações do Dataset")
        st.dataframe(df) #df.head() para 5
        logger.info("Exibindo informacoes basicas do dataset.")

        st.write("### Estatísticas Gerais")
        st.write(df.describe())

        show_top_videos(df)
        # Mostrar gráficos
        plot_missing_values(df)
        null_percentage, zero_percentage = calculate_null_zero_percentage(df)
        st.write(f"Percentual de valores nulos: {null_percentage:.2f}%")
        st.write(f"Percentual de valores zero: {zero_percentage:.2f}%")
        logger.info(f"Percentual de valores nulos: {null_percentage:.2f}%")
        logger.info(f"Percentual de valores zeros: {zero_percentage:.2f}%")

        st.write("### Distribuição das Variáveis Numéricas")
        plot_numeric_distribution(df)
        
        plot_views_vs_likes(df)
        df = merge_categories(df, selected_file)
        plot_views_by_category(df)
        
        
    else:
        logger.error(f"Erro ao baixar dataset")
        st.error("Erro ao carregar os dados.")

if __name__ == "__main__":
    main()
