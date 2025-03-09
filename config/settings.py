import os
import json
from config.logger import logger

def load_kaggle_credentials():
    kaggle_json_path = os.path.expanduser("~/.kaggle/kaggle.json")
    try:
        with open(kaggle_json_path, 'r') as file:
            dados = json.load(file)
        os.environ['KAGGLE_USERNAME'] = dados['username']
        os.environ['KAGGLE_KEY'] = dados['key']
        logger.info("Credenciais do Kaggle carregadas com sucesso.")
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("Erro ao carregar credenciais do Kaggle!")
        return False
