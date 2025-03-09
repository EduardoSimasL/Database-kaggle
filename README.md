# Database_kaggle

N-tier architecture

projeto/
│── main.py  
│── ui/       # Interface do usuário (UI)
│   ├── __init__.py  
│   ├── web_interface.py  
│── processing/           # Regras de negócio
│   ├── __init__.py  
│   ├── services.py  
│── data/               # Acesso a dados (Database, API)
│   ├── __init__.py  
│   ├── repositories.py  
│── config/             # Configurações gerais
│   ├── __init__.py  
│   ├── settings.py  
