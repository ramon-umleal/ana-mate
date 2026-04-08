# run.py - Ponto de entrada principal para o projeto ANA-MATE

import os
import socket
from app import app, db  # Importa a aplicação Flask e o banco de dados do app.py
from config import Config  # Importa as configurações do config.py

# Função para obter o endereço IP da máquina para acesso via rede

def get_network_ip():
    try:
        # Cria um socket para obter o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Conecta a um servidor externo para obter o IP
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Aviso: Não foi possível obter o IP da rede. Erro: {e}")
        return 'Não disponível'

# Função principal para inicializar e executar a aplicação

def main():
    # Detecta o ambiente: usa FLASK_ENV ou padrão 'development'
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"Ambiente detectado: {env}")
    
    # Aplica as configurações baseadas no ambiente
    app.config.from_object(Config)
    
    # Inicializa o banco de dados
    try:
        with app.app_context():
            db.create_all()
        db_status = "Banco de dados inicializado com sucesso."
    except Exception as e:
        db_status = f"Erro ao inicializar o banco de dados: {e}"
        print(f"Erro: {db_status}")
    
    # Exibe o banner/logo do ANA-MATE
    print("""
    █████╗ ███╗   ██╗ █████╗     ███╗   ███╗ █████╗ ████████╗███████╗
    ██╔══██╗████╗  ██║██╔══██╗    ████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
    ███████║██╔██╗ ██║███████║    ██╔████╔██║███████║   ██║   █████╗  
    ██╔══██║██║╚██╗██║██╔══██║    ██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
    ██║  ██║██║ ╚████║██║  ██║    ██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
    ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
    
    Bem-vindo ao ANA-MATE - Seu assistente inteligente!
    """)
    
    # Exibe informações de inicialização
    print(f"Ambiente em uso: {env}")
    print("URL local: http://127.0.0.1:5000")
    network_ip = get_network_ip()
    if network_ip != 'Não disponível':
        print(f"URL da rede (para acesso do celular): http://{network_ip}:5000")
    else:
        print("URL da rede: Não disponível")
    print(f"Status do banco de dados: {db_status}")
    print("\nIniciando o servidor...")
    
    # Executa a aplicação Flask
    app.run(host='0.0.0.0', port=5000, debug=(env == 'development'))

# Executa a função principal se o script for chamado diretamente
if __name__ == '__main__':
    main()