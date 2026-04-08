# cadastrar.py
from app import app, db, Student

# Lista de alunos (CORRIGIDA: todos usam 'nome')
alunos_para_cadastrar = [
    {'nome': 'Ana Beatriz', 'senha': '0412'},
    {'nome': 'Liz', 'senha': '4539'},
    {'nome': 'Maria Santos', 'senha': '5678'},
    {'nome': 'Ramon', 'senha': 'admin999'}  
]

def cadastrar_alunos():
    with app.app_context():
        print("Iniciando o cadastro de alunos...\n")
        
        for dados in alunos_para_cadastrar:
            try:
                # Verifica se o aluno já existe
                aluno_existente = Student.query.filter_by(nome=dados['nome']).first()
                
                if aluno_existente:
                    print(f"⚠️ O aluno '{dados['nome']}' já existe.")
                else:
                    # Cria um novo aluno
                    novo_aluno = Student(nome=dados['nome'])
                    novo_aluno.set_password(dados['senha'])
                    
                    db.session.add(novo_aluno)
                    print(f"✅ Aluno '{dados['nome']}' preparado para cadastro.")
            except KeyError as e:
                print(f"❌ Erro nos dados do aluno {dados}: Chave {e} não encontrada.")
        
        try:
            # Salva tudo no banco de dados de uma vez
            db.session.commit()
            print("\n🎉 Todos os cadastros foram salvos com sucesso no banco de dados!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao salvar no banco de dados: {e}")

if __name__ == '__main__':
    cadastrar_alunos()