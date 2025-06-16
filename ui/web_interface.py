import os
import pandas as pd
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

# Página configurada
st.set_page_config(
    page_title="SIAMD - Sistema Inteligente de Análise e Modelagem",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    # Sidebar
    st.sidebar.title("SIAMD 🌐")
    st.sidebar.markdown("_Sistema Inteligente de Análise e Modelagem de Dados_")

    # Upload local e Kaggle
    uploaded_file = st.sidebar.file_uploader(
        "📂 Carregar CSV/Excel local", type=["csv", "xlsx"]
    )
    kaggle_ok = load_kaggle_credentials()
    if kaggle_ok:
        st.sidebar.markdown("---")
        dataset_name = st.sidebar.text_input(
            "🔗 Dataset Kaggle:", "datasnaek/youtube-new"
        )
        download_path = "./data"
        if st.sidebar.button("⬇️ Baixar do Kaggle"):
            success = download_dataset(dataset_name, download_path)
            st.sidebar.success(
                "✅ Dataset baixado!" if success else "❌ Falha ao baixar."
            )
            logger.info(f"Download Kaggle: {dataset_name}")
        csv_files = (
            [f for f in os.listdir(download_path) if f.endswith(".csv")]
            if os.path.exists(download_path)
            else []
        )
        if csv_files:
            selected_file = st.sidebar.selectbox("CSV disponível:", csv_files)
            max_rows = st.sidebar.slider("Linhas Máx.", 100, 100000, 30000, step=100)
            file_path = os.path.join(download_path, selected_file)
    else:
        st.sidebar.warning("⚠️ Configure credenciais Kaggle no .env para download.")

    # Carregamento do DataFrame
    df = None
    if uploaded_file:
        df = (
            pd.read_csv(uploaded_file)
            if uploaded_file.name.endswith(".csv")
            else pd.read_excel(uploaded_file)
        )
        df.columns = df.columns.str.lower()
    elif kaggle_ok and "file_path" in locals():
        df = load_data(file_path, max_rows)

    # Títulos e Tabs
    st.title("SIAMD - Sistema de Análise e Modelagem")
    tab1, tab2, tab3 = st.tabs(
        [
            "🔍 Análise Exploratória",
            "🤖 Treinamento de Modelo",
            "📊 Avaliação & Previsão",
        ]
    )

    # Tab 1: EDA
    with tab1:
        if df is None:
            st.warning("📥 Carregue ou baixe um dataset para começar.")
        else:
            st.header("Informações Gerais")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("Visão dos Dados")
                st.dataframe(df.head(), height=300)
            with c2:
                st.metric("Linhas", df.shape[0])
                st.metric("Colunas", df.shape[1])
                null_pct, zero_pct = calculate_null_zero_percentage(df)
                st.metric("Nulos (%)", f"{null_pct:.2f}%")
                st.metric("Zeros (%)", f"{zero_pct:.2f}%")
            st.markdown("---")
            st.subheader("Distribuições")
            plot_numeric_distribution(df)
            plot_missing_values(df)
            st.markdown("---")
            st.subheader("Tendências")
            plot_regression_likes_views(df)
            plot_regression_like_rate_vs_views(df)
            plot_views_vs_likes(df)
            st.markdown("---")
            st.subheader("Categorias")
            if 'category_id' in df.columns:
                df_cat = merge_categories(df, selected_file)
                plot_views_by_category(df_cat)
            else:
                st.info("Coluna 'category_id' não encontrada; análise de categorias pulada.")
            show_top_videos(df)

    # Tab 2: Model Training
    with tab2:
        st.header("Configuração e Treinamento")
        if df is None:
            st.warning("📥 Carregue um dataset antes de treinar.")
        else:
            with st.expander("📋 Parâmetros do Modelo", expanded=True):
                cols = df.columns.tolist()
                target_col = st.selectbox("Coluna Alvo:", cols)
                feature_cols = st.multiselect(
                    "Features:",
                    [c for c in cols if c != target_col],
                    default=[c for c in cols if c != target_col],
                )
                task_type = st.selectbox(
                    "Tipo de Tarefa:", ["classification", "regression", "clustering"]
                )
                cv_folds = st.slider("Folds CV:", 2, 10, 5)
                train_size = st.slider("Tamanho do Treino:", 0.5, 0.9, 0.8)

            if st.button("🚀 Treinar Modelo"):
                if not feature_cols:
                    st.error("Selecione ao menos uma feature.")
                else:
                    df_train = df[feature_cols + [target_col]]
                    stratify_flag = True

                    # Se for classificação, verifica test_size vs n_classes
                    if task_type == "classification":
                        test_n = int((1 - train_size) * len(df_train))
                        n_classes = df_train[target_col].nunique()
                        if test_n < n_classes:
                            st.warning(
                                f"⚠️ Test size ({test_n}) menor que número de classes ({n_classes}).\n"
                                "Estratificação desabilitada automaticamente."
                            )
                            stratify_flag = False

                    # Treina passando o flag de stratify
                    pyc = PyCaretAdapter()
                    with st.spinner("Treinando modelo..."):
                        model = pyc.train_model(
                            df_train,
                            target_col,
                            task_type,
                            cv_folds=cv_folds,
                            train_size=train_size,
                            stratify=stratify_flag
                        )


                    st.success("✅ Treinamento concluído!")
                    st.session_state.trained_model = model
                    st.session_state.task_type = task_type
                    st.session_state.feature_cols = feature_cols
                    st.write("**Melhor modelo:**", model)

    # Tab 3: Evaluation & Prediction
    with tab3:
        st.header("Avaliação e Previsão")
        if "trained_model" not in st.session_state:
            st.warning("🤖 Treine um modelo antes de usar esta aba.")
        else:
            model = st.session_state.trained_model
            task_type = st.session_state.task_type
            features = st.session_state.feature_cols
            c1, c2 = st.columns([1, 1])
            # Avaliação
            with c1:
                if st.button("🔍 Analisar Modelo"):
                    pc = PyCaretAdapter()
                    with st.spinner("Gerando gráficos..."):
                        pc.analyze_model(model, task_type)
            # Previsão
            with c2:
                st.subheader("Novo Registro")
                with st.form("form_previsao", clear_on_submit=True):
                    new_data = {}
                    for f in features:
                        if pd.api.types.is_datetime64_any_dtype(df[f]):
                            # date_input já devolve um datetime.date
                            new_data[f] = st.date_input(
                                f,
                                value=df[f].dt.date.mode().iloc[0]
                            )
                        elif pd.api.types.is_numeric_dtype(df[f]):
                            new_data[f] = st.number_input(f, value=float(df[f].mean()))
                        else:
                            new_data[f] = st.text_input(f, value="")

                    if st.form_submit_button("📊 Prever"):
                        new_df = pd.DataFrame([new_data])
                        for f in features:
                            if pd.api.types.is_datetime64_any_dtype(df[f]):
                                new_df[f] = pd.to_datetime(new_df[f])
                        if task_type == "classification":
                            from pycaret.classification import predict_model as pred
                        elif task_type == "regression":
                            from pycaret.regression import predict_model as pred
                        else:
                            from pycaret.clustering import predict_model as pred
                        result = pred(model, data=new_df)
                        st.subheader("Resultado da Previsão")
                        st.dataframe(result)


if __name__ == "__main__":
    main()
