from kaggle.api.kaggle_api_extended import KaggleApi
import os


def download_dataset(dataset_name, download_path="./data"):
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    try:
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(dataset_name, path=download_path, unzip=True)
        print(" Dataset baixado com sucesso!")
        return True
    except Exception as e:
        print(f" Erro ao baixar o dataset: {e}")
        return False
