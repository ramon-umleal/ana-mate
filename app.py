from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Substitua por uma chave segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anamate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos do Banco de Dados
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    total_estrelas = db.Column(db.Integer, default=0)
    nivel_tabuada = db.Column(db.String(10), default='A1')  # A1 a B10
    nivel_chuva_numeros = db.Column(db.Integer, default=1)  # Níveis para chuva de números

class Tentativa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    pergunta = db.Column(db.String(200), nullable=False)
    resposta_correta = db.Column(db.String(50), nullable=False)
    resposta_aluno = db.Column(db.String(50), nullable=False)
    acertou = db.Column(db.Boolean, nullable=False)
    estrelas = db.Column(db.Integer, nullable=False)
    tentativa_numero = db.Column(db.Integer, nullable=False)  # Número da tentativa para a pergunta
    jogo_tipo = db.Column(db.String(50), nullable=False)  # 'tabuada', 'chuva_numeros', etc.

class QuestaoErrada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    pergunta = db.Column(db.String(200), nullable=False)
    resposta_correta = db.Column(db.String(50), nullable=False)

# Funções Auxiliares

def calcular_estrelas(tentativa_numero):
    if tentativa_numero == 1:
        return 3
    elif tentativa_numero == 2:
        return 2
    else:
        return 1

def gerar_questao_tabuada(nivel):
    # Níveis A1-A10: multiplicação simples, B1-B10: mais avançado
    if nivel.startswith('A'):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        pergunta = f'{num1} x {num2}'
        resposta = str(num1 * num2)
    else:
        # B: divisões ou multiplicações maiores
        num1 = random.randint(10, 20)
        num2 = random.randint(1, 10)
        pergunta = f'{num1} x {num2}'
        resposta = str(num1 * num2)
    return pergunta, resposta

def gerar_questao_chuva(nivel):
    # Tabuada ou raiz quadrada
    tipo = random.choice(['tabuada', 'raiz'])
    if tipo == 'tabuada':
        num1 = random.randint(1, 10 + nivel)
        num2 = random.randint(1, 10)
        pergunta = f'{num1} x {num2}'
        resposta = str(num1 * num2)
    else:
        num = random.randint(1, 10 + nivel)
        pergunta = f'√{num**2}'
        resposta = str(num)
    return pergunta, resposta

# Rotas
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        if not nome:
            flash('Nome é obrigatório.', 'error')
            return render_template('login.html')
        aluno = Aluno.query.filter_by(nome=nome).first()
        if not aluno:
            aluno = Aluno(nome=nome)
            db.session.add(aluno)
            db.session.commit()
        session['aluno_id'] = aluno.id
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))
    aluno = Aluno.query.get(session['aluno_id'])
    return render_template('menu.html', aluno=aluno)

@app.route('/iniciar_exercicio')
def iniciar_exercicio():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))
    aluno = Aluno.query.get(session['aluno_id'])
    # Lógica para iniciar exercício de tabuada baseado no nível
    return render_template('iniciar_exercicio.html', aluno=aluno)

@app.route('/exercicio', methods=['GET', 'POST'])
def exercicio():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))
    aluno = Aluno.query.get(session['aluno_id'])
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')
        resposta_aluno = request.form.get('resposta')
        resposta_correta = request.form.get('resposta_correta')
        tentativa_numero = int(request.form.get('tentativa_numero', 1))
        acertou = resposta_aluno.strip() == resposta_correta
        estrelas = calcular_estrelas(tentativa_numero) if acertou else 0
        tentativa = Tentativa(
            aluno_id=aluno.id,
            pergunta=pergunta,
            resposta_correta=resposta_correta,
            resposta_aluno=resposta_aluno,
            acertou=acertou,
            estrelas=estrelas,
            tentativa_numero=tentativa_numero,
            jogo_tipo='tabuada'
        )
        db.session.add(tentativa)
        if acertou:
            aluno.total_estrelas += estrelas
            # Avançar nível se necessário
            if aluno.nivel_tabuada != 'B10':
                # Lógica simples para avançar
                pass  # Implementar lógica de avanço
        else:
            # Adicionar à fila de repetição
            questao_errada = QuestaoErrada(
                aluno_id=aluno.id,
                pergunta=pergunta,
                resposta_correta=resposta_correta
            )
            db.session.add(questao_errada)
        db.session.commit()
        return jsonify({'acertou': acertou, 'estrelas': estrelas})
    # GET: gerar nova questão
    pergunta, resposta = gerar_questao_tabuada(aluno.nivel_tabuada)
    return render_template('exercicio.html', pergunta=pergunta, resposta_correta=resposta, tentativa_numero=1)

@app.route('/ordem_operacoes')
def ordem_operacoes():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))
    # Página para ordem das operações
    return render_template('ordem_operacoes.html')

@app.route('/chuva_numeros')
def chuva_numeros():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))
    return render_template('chuva_numeros.html')

@app.route('/api/questao_chuva', methods=['POST'])
def api_questao_chuva():
    if 'aluno_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    aluno = Aluno.query.get(session['aluno_id'])
    pergunta, resposta = gerar_questao_chuva(aluno.nivel_chuva_numeros)
    return jsonify({'pergunta': pergunta, 'resposta_correta': resposta})

@app.route('/api/validar_chuva', methods=['POST'])
def api_validar_chuva():
    if 'aluno_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    data = request.get_json()
    resposta_aluno = data.get('resposta')
    resposta_correta = data.get('resposta_correta')
    tentativa_numero = data.get('tentativa_numero', 1)
    acertou = resposta_aluno.strip() == resposta_correta
    estrelas = calcular_estrelas(tentativa_numero) if acertou else 0
    return jsonify({'acertou': acertou, 'estrelas': estrelas})

@app.route('/api/salvar_chuva', methods=['POST'])
def api_salvar_chuva():
    if 'aluno_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    data = request.get_json()
    aluno_id = session['aluno_id']
    tentativa = Tentativa(
        aluno_id=aluno_id,
        pergunta=data['pergunta'],
        resposta_correta=data['resposta_correta'],
        resposta_aluno=data['resposta_aluno'],
        acertou=data['acertou'],
        estrelas=data['estrelas'],
        tentativa_numero=data['tentativa_numero'],
        jogo_tipo='chuva_numeros'
    )
    db.session.add(tentativa)
    aluno = Aluno.query.get(aluno_id)
    if data['acertou']:
        aluno.total_estrelas += data['estrelas']
        # Avançar nível
    else:
        questao_errada = QuestaoErrada(
            aluno_id=aluno_id,
            pergunta=data['pergunta'],
            resposta_correta=data['resposta_correta']
        )
        db.session.add(questao_errada)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/progresso_aluno')
def api_progresso_aluno():
    if 'aluno_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    aluno = Aluno.query.get(session['aluno_id'])
    return jsonify({
        'nome': aluno.nome,
        'total_estrelas': aluno.total_estrelas,
        'nivel_tabuada': aluno.nivel_tabuada,
        'nivel_chuva_numeros': aluno.nivel_chuva_numeros
    })

@app.route('/api/questoes_erradas')
def api_questoes_erradas():
    if 'aluno_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    questoes = QuestaoErrada.query.filter_by(aluno_id=session['aluno_id']).all()
    return jsonify([{
        'pergunta': q.pergunta,
        'resposta_correta': q.resposta_correta
    } for q in questoes])

@app.route('/logout')
def logout():
    session.pop('aluno_id', None)
    return redirect(url_for('login'))


# Inicialização do banco de dados
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print(f"🚀 Tabuada Master rodando!")
    print(f"→ Local:    http://127.0.0.1:5000")
    print(f"→ Rede:     http://{ip}:5000   (teste no celular!)")
    
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

