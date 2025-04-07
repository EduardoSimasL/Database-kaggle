# Database_kaggle

Comando: streamlit run main.py

Arquivo .csv e Dataset padrão para análise: CAvideos.csv - datasnaek/youtube-new

arquitetura hexagonal

projeto/
│── main.py                   # Ponto de entrada da aplicação (CLI ou outro tipo de interface)
│── ui/                       # Interface do usuário (UI)
│   ├── __init__.py  
│   ├── web_interface.py      # Exibe a interface (por exemplo, com Streamlit)
│── processing/               # Regras de negócio / lógica da aplicação
│   ├── __init__.py  
│   ├── services.py          # Casos de uso que orquestram as operações, chamando os ports
│── data/                     # Acesso a dados (Database, API) – pode conter os repositórios
│   ├── __init__.py  
│   ├── repositories.py      # Implementação concreta (adapter) para acesso aos dados
│── config/                   # Configurações gerais
│   ├── __init__.py  
│   ├── settings.py          # Variáveis e configurações do ambiente
│── adapters/         # Implementações concretas dos ports
│   ├── __init__.py  
│   ├── pycaret_adapter.py 
│── ports/            # Contratos (interfaces) para interação com componentes externos
│   ├── __init__.py  
│   ├── dataset_port.py  
│   ├── dtale_port.py  
│   ├── profiling_port.py  
│   └── training_port.py  