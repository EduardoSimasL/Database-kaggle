import pandas as pd
from ports.training_port import TrainingPort

# PyCaret tasks + imports para análise de modelo
from pycaret.classification import (
    setup as class_setup,
    compare_models as class_compare,
    plot_model as clf_plot
)
from pycaret.regression import (
    setup as reg_setup,
    compare_models as reg_compare,
    plot_model as reg_plot
)
from pycaret.clustering import (
    setup as clus_setup,
    create_model as clus_create,
    plot_model as clus_plot
)

class PyCaretAdapter(TrainingPort):
    def train_model(
        self,
        df: pd.DataFrame,
        target: str,
        task_type: str,
        cv_folds: int = 5,
        train_size: float = 0.8,
        stratify: bool = True
    ):
        if task_type == "classification":
            # Classificação com CV e controle de estratificação
            class_setup(
                data=df,
                target=target,
                session_id=123,
                html=False,
                fold=cv_folds,
                train_size=train_size,
                train_test_split_stratify=stratify
            )
            best_model = class_compare()
            print("Best Classification Model:", best_model)
            return best_model

        elif task_type == "regression":
            # Regressão com CV
            reg_setup(
                data=df,
                target=target,
                session_id=123,
                html=False,
                fold=cv_folds,
                train_size=train_size
            )
            best_model = reg_compare()
            print("Best Regression Model:", best_model)
            return best_model

        elif task_type == "clustering":
            # Clusterização padrão (KMeans)
            clus_setup(
                data=df,
                session_id=123,
                html=False
            )
            best_model = clus_create("kmeans")
            print("Clustering Model:", best_model)
            return best_model

        else:
            raise ValueError("task_type deve ser 'classification', 'regression' ou 'clustering'")

    def analyze_model(self, model, task_type: str):
        """
        Exibe gráficos de avaliação do modelo no Streamlit usando plot_model().
        """
        if task_type == "classification":
            clf_plot(model, plot="confusion_matrix", display_format="streamlit")
            clf_plot(model, plot="auc", display_format="streamlit")

        elif task_type == "regression":
            reg_plot(model, plot="residuals", display_format="streamlit")
            reg_plot(model, plot="error", display_format="streamlit")

        else:  # clustering
            clus_plot(model, plot="elbow", display_format="streamlit")
            clus_plot(model, plot="cluster", display_format="streamlit")
