import os
import pyodbc

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQL_SERVER = 'localhost'
    SQL_DATABASE = 'CorretoraSegurosDB'
    # Usando Windows Authentication ao invés de SQL Authentication
    SQL_USERNAME = None
    SQL_PASSWORD = None
    SQL_DRIVER = 'ODBC Driver 17 for SQL Server'
    USE_WINDOWS_AUTH = True
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://@{SQL_SERVER}/{SQL_DATABASE}?driver={SQL_DRIVER.replace(' ', '+')}&trusted_connection=yes"
    )

# Configuração legacy para compatibilidade com test_sistema.py
DATABASE_CONFIG = {
    'server': Config.SQL_SERVER,
    'database': Config.SQL_DATABASE,
    'driver': Config.SQL_DRIVER,
    'use_windows_auth': Config.USE_WINDOWS_AUTH,
    'username': Config.SQL_USERNAME,
    'password': Config.SQL_PASSWORD
}

def get_connection():
    """Função para obter conexão com o banco de dados (compatibilidade com test_sistema.py)"""
    if Config.USE_WINDOWS_AUTH:
        conn_str = (
            f"DRIVER={{{Config.SQL_DRIVER}}};"
            f"SERVER={Config.SQL_SERVER};"
            f"DATABASE={Config.SQL_DATABASE};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes"
        )
    else:
        conn_str = (
            f"DRIVER={{{Config.SQL_DRIVER}}};"
            f"SERVER={Config.SQL_SERVER};"
            f"DATABASE={Config.SQL_DATABASE};"
            f"UID={Config.SQL_USERNAME};"
            f"PWD={Config.SQL_PASSWORD};"
            f"TrustServerCertificate=yes"
        )
    
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Erro na conexão com banco de dados: {e}")
        return None
