# atualizar_senhas.py
from app import app, db, Student
from sqlalchemy import func

# Lista com as novas senhas (corrigido 'name' para 'nome' no Ramon)
alunos_para_atualizar = [ 
    {'nome': 'Ana Beatriz', 'senha': '0412'}, 
    {'nome': 'Liz', 'senha': '9078'}, 
    {'nome': 'Maria Santos', 'senha': '5678'}, 
    {'nome': 'Ramon', 'senha': '@admin1'} 
]

def atualizar_senhas():
    # Precisamos do contexto da aplicação para mexer no banco
    with app.app_context():
        print("Iniciando a atualização de senhas...")
        
        for dados in alunos_para_atualizar:
            # Busca o aluno ignorando maiúsculas/minúsculas (ex: "ana beatriz" acha "Ana Beatriz")
            aluno = Student.query.filter(func.lower(Student.nome) == func.lower(dados['nome'])).first()
            
            if aluno:
                # O método set_password (definido no seu app.py) criptografa a nova senha
                aluno.set_password(dados['senha'])
                print(f"✅ Senha do aluno '{aluno.nome}' atualizada com sucesso!")
            else:
                print(f"⚠️ Aluno '{dados['nome']}' não encontrado no banco de dados.")
        
        # Salva todas as alterações no banco
        db.session.commit()
        print("\n🎉 Processo de atualização finalizado!")

if __name__ == '__main__':
    atualizar_senhas()
