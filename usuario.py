# usuario.py
from app import app, Student

def listar_usuarios():
    with app.app_context():
        print("\n--- USUÁRIOS NO BANCO DE DADOS ---")
        
        # Busca todos os alunos no banco
        alunos = Student.query.all()
        
        if not alunos:
            print("Nenhum usuário cadastrado ainda.")
        else:
            for aluno in alunos:
                status = "Ativo" if aluno.ativo else "Inativo"
                print(f"ID: {aluno.id} | Nome: {aluno.nome} | Nível Tabuada: {aluno.nivel_tabuada} | Status: {status}")
        
        print("----------------------------------\n")

if __name__ == '__main__':
    listar_usuarios()