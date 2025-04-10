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
    merge_categories,
    plot_regression_likes_views,
    plot_regression_like_rate_vs_views,
)
from data.kaggle_service import download_dataset
from config.settings import load_kaggle_credentials
from config.logger import logger
from adapters.pycaret_adapter import PyCaretAdapter

def main():
    st.title("Análise de Dados Kaggle")
    
    mode = st.sidebar.radio("Selecione a operação:", 
                            ["Análise Exploratória", "Treinamento do Modelo", "Avaliação e Aplicação do Modelo"])
    
    df = None
    if load_kaggle_credentials():
        dataset_name = st.text_input("Digite o nome do dataset:", "datasnaek/youtube-new")
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
            st.write(f"**Você selecionou:** {selected_file}")
            max_rows = st.slider("Selecione o número máximo de linhas:", 
                                 min_value=1000, max_value=100000, value=30000, step=100)
            df = load_data(file_path, max_rows)

    if mode == "Análise Exploratória":
        if df is not None:
            st.write("### Informações do Dataset")
            st.dataframe(df)
            logger.info("Exibindo informações básicas do dataset.")

            st.write("### Estatísticas Gerais")
            st.write(df.describe())

            show_top_videos(df)
            plot_missing_values(df)
            null_percentage, zero_percentage = calculate_null_zero_percentage(df)
            st.write(f"Percentual de valores nulos: {null_percentage:.2f}%")
            st.write(f"Percentual de valores zero: {zero_percentage:.2f}%")
            logger.info(f"Percentual de valores nulos: {null_percentage:.2f}%")
            logger.info(f"Percentual de valores zero: {zero_percentage:.2f}%")

            st.write("### Distribuição das Variáveis Numéricas")
            plot_numeric_distribution(df)
            plot_regression_likes_views(df)
            plot_regression_like_rate_vs_views(df)
            plot_views_vs_likes(df)
            df = merge_categories(df, selected_file)
            plot_views_by_category(df)
        else:
            logger.error("Erro ao baixar dataset")
            st.error("Erro ao carregar os dados.")
    
    elif mode == "Treinamento do Modelo":
        st.header("Treinamento do Modelo")
        if df is not None:
            st.write("### Visualização dos Dados para Treinamento")
            st.dataframe(df.head())
            # Seleção da coluna alvo e tipo de tarefa
            columns = df.columns.tolist()
            target_col = st.selectbox("Selecione a coluna alvo:", columns)
            task_type = st.selectbox("Selecione o tipo de tarefa:", 
                                     ["classification", "regression", "clustering"])
            if st.button("Treinar Modelo"):
                pycaret_adapter = PyCaretAdapter()
                with st.spinner("Treinando modelo..."):
                    model = pycaret_adapter.train_model(df, target_col, task_type)
                st.success("Treinamento concluído!")
                st.write("Modelo treinado:")
                st.write(model)
                # Armazena o modelo na sessão para uso posterior
                st.session_state.trained_model = model
                st.session_state.task_type = task_type
        else:
            st.error("Carregue um dataset para treinamento.")
            
    elif mode == "Avaliação e Aplicação do Modelo":
        st.header("Avaliação e Aplicação do Modelo")
        if df is not None:
            st.write("### Dados para Avaliação")
            st.dataframe(df.head())
            if "trained_model" in st.session_state:
                model = st.session_state.trained_model
                task_type = st.session_state.get("task_type", "classification")
                st.write("### Avaliação do Modelo")
                if st.button("Avaliar Modelo"):
                    with st.spinner("Avaliando modelo..."):
                        # Dependendo do tipo de tarefa, utilize a função predict_model do PyCaret
                        if task_type == "classification":
                            from pycaret.classification import predict_model
                        elif task_type == "regression":
                            from pycaret.regression import predict_model
                        elif task_type == "clustering":
                            from pycaret.clustering import predict_model
                        else:
                            st.error("Tipo de tarefa inválido.")
                            return
                        
                        # Gera predições e coleta as métricas
                        predictions = predict_model(model, data=df)
                        st.write("### Resultados da Avaliação e Predição")
                        st.dataframe(predictions)
                        st.success("Avaliação concluída!")
            else:
                st.error("Nenhum modelo treinado disponível. Por favor, treine um modelo primeiro.")
        else:
            st.error("Carregue um dataset para avaliação.")

if __name__ == "__main__":
    main()
