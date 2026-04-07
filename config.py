import os

# Arquivo de configuração para o projeto ANA-MATE
# Este arquivo contém configurações para diferentes ambientes (desenvolvimento, produção, teste)

class Config:
    """Classe base para configurações"""
    # Configurações de Desenvolvimento
    DEBUG = False
    TESTING = False
    
    # Configurações do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-troque-em-producao'  # AVISO: Troque em produção!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///anamate.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Defina como True em produção com HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de Aplicação
    MAX_QUESTIONS_PER_SESSION = 10
    MIN_SCORE_TO_ADVANCE = 80  # Porcentagem
    STAR_VALUES = {1: 1, 2: 2, 3: 3}
    TABUADA_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Níveis de tabuada disponíveis
    ORDER_OF_OPERATIONS_LEVELS = ['basico', 'intermediario', 'avancado']  # Níveis de ordem de operações

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # HTTPS obrigatório em produção
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Deve ser definida via variável de ambiente

class TestingConfig(Config):
    """Configurações para ambiente de teste"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco em memória para testes
    WTF_CSRF_ENABLED = False  # Desabilitar CSRF para testes

# Dicionário para mapear configurações por ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}