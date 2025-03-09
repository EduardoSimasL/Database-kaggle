import os
import json

def load_kaggle_credentials():
    kaggle_json_path = os.path.expanduser("~/.kaggle/kaggle.json")
    try:
        with open(kaggle_json_path, 'r') as file:
            dados = json.load(file)
        os.environ['KAGGLE_USERNAME'] = dados['username']
        os.environ['KAGGLE_KEY'] = dados['key']
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        print("Erro ao carregar credenciais do Kaggle!")
        return False
