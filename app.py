import os
import logging
import random
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ==========================================
# 1. CONFIGURAÇÃO DO FLASK
# ==========================================
app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave_padrao_segura_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ana_mate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

app.config['SESSION_COOKIE_SECURE'] = not app.config['DEBUG']
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Inicialização das extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para acessar."
login_manager.login_message_category = "error"
csrf = CSRFProtect(app)

# ==========================================
# 2. MODELOS DO BANCO DE DADOS
# ==========================================
class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    total_estrelas = db.Column(db.Integer, default=0)
    nivel_tabuada = db.Column(db.String(10), default='A1')
    nivel_ordem_operacoes = db.Column(db.String(10), default='O1')
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)


# Lista de missões (temas da 5ª série)
MISSOES = {
    'operacoes_basicas': 'Operações Básicas',
    'fracoes_decimais': 'Frações e Decimais',
    'geometria': 'Geometria',
    'problemas_logica': 'Problemas de Lógica'
}

# Gerador de questões estilo Colégio Militar
def gerar_questao(missao):
    questoes = {
        'operacoes_basicas': [
            {'pergunta': 'Soldado, calcule: 15 + 27 = ?', 'resposta': 42},
            {'pergunta': 'Atirador de elite, subtraia: 100 - 34 = ?', 'resposta': 66},
            {'pergunta': 'Multiplique como um verdadeiro militar: 8 * 9 = ?', 'resposta': 72},
            {'pergunta': 'Divida com precisão: 144 / 12 = ?', 'resposta': 12}
        ],
        'fracoes_decimais': [
            {'pergunta': 'Soldado, converta 0.5 para fração: ?', 'resposta': '1/2'},
            {'pergunta': 'Some as frações: 1/2 + 1/4 = ?', 'resposta': '3/4'},
            {'pergunta': 'Multiplique decimais: 0.3 * 0.4 = ?', 'resposta': 0.12},
            {'pergunta': 'Divida frações: 3/4 ÷ 1/2 = ?', 'resposta': '3/2'}
        ],
        'geometria': [
            {'pergunta': 'Soldado, qual é a área de um quadrado de lado 5?', 'resposta': 25},
            {'pergunta': 'Calcule o perímetro de um retângulo 4x6.', 'resposta': 20},
            {'pergunta': 'Qual é o volume de um cubo de aresta 3?', 'resposta': 27},
            {'pergunta': 'Ângulo reto mede quantos graus?', 'resposta': 90}
        ],
        'problemas_logica': [
            {'pergunta': 'Soldado, se todos os militares são corajosos e João é militar, João é corajoso?', 'resposta': 'Sim'},
            {'pergunta': 'Há 3 maçãs e você come 2, quantas restam?', 'resposta': 1},
            {'pergunta': 'Qual é o próximo número: 2, 4, 6, 8, ...?', 'resposta': 10},
            {'pergunta': 'Se A é maior que B e B é maior que C, quem é o maior?', 'resposta': 'A'}
        ]
    }
    if missao in questoes:
        return random.choice(questoes[missao])
    return {'pergunta': 'Missão desconhecida, soldado!', 'resposta': 'N/A'}


# ==========================================
# 3. FUNÇÕES DE SUPORTE
# ==========================================
@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


# --- FUNÇÃO PARA GERAR QUESTÕES DO SIMULADO CMB ---
def gerar_questao_cmb():
    """Gera uma questão de múltipla escolha estilo Colégio Militar (5º ano)."""
    tipo_questao = random.choice(['aritmetica', 'logica_simples'])
    
    if tipo_questao == 'aritmetica':
        num1 = random.randint(10, 50)
        num2 = random.randint(2, 12)
        operador = random.choice(['+', '-', 'x', '/'])
        
        pergunta_texto = ""
        resposta_correta = 0
        
        if operador == '+':
            pergunta_texto = f"Soldado, qual é o resultado da soma: {num1} + {num2}?"
            resposta_correta = num1 + num2
        elif operador == '-':
            # Garante que não dê negativo
            if num1 < num2: num1, num2 = num2, num1
            pergunta_texto = f"Atenção na subtração: {num1} - {num2} = ?"
            resposta_correta = num1 - num2
        elif operador == 'x':
            num1 = random.randint(5, 15) # Números menores para multiplicação
            pergunta_texto = f"Calcule rápido: {num1} x {num2} = ?"
            resposta_correta = num1 * num2
        elif operador == '/':
            # Garante divisão exata
            resposta_correta = num1
            num1 = num1 * num2 
            pergunta_texto = f"Divida as tropas: {num1} ÷ {num2} = ?"
            
        opcoes = [resposta_correta]
        # Gera 3 opções erradas (distratores)
        while len(opcoes) < 4:
            distrator = resposta_correta + random.choice([-10, -5, -2, -1, 1, 2, 5, 10])
            if distrator > 0 and distrator not in opcoes:
                opcoes.append(distrator)
        random.shuffle(opcoes)
        
        return {
            'pergunta_texto': pergunta_texto,
            'correto': str(resposta_correta), 
            'opcoes': [str(o) for o in opcoes]
        }
    
    elif tipo_questao == 'logica_simples':
        questoes_logica = [
            {"pergunta": "Um pelotão tem 4 fileiras com 8 soldados cada. Quantos soldados há no total?", "resposta": "32", "opcoes": ["24", "30", "32", "36"]},
            {"pergunta": "Se ontem foi terça-feira, que dia será amanhã?", "resposta": "Quinta-feira", "opcoes": ["Quarta-feira", "Quinta-feira", "Sexta-feira", "Segunda-feira"]},
            {"pergunta": "João tinha 50 reais. Comprou um livro por 25 e um lanche por 10. Quanto sobrou?", "resposta": "15", "opcoes": ["10", "15", "20", "25"]},
            {"pergunta": "Qual é o próximo número da sequência militar: 5, 10, 15, 20, ...?", "resposta": "25", "opcoes": ["21", "25", "30", "35"]}
        ]
        questao = random.choice(questoes_logica)
        # Embaralha as opções
        opcoes = questao['opcoes'].copy()
        random.shuffle(opcoes)
        
        return {
            'pergunta_texto': questao['pergunta'],
            'correto': questao['resposta'],
            'opcoes': opcoes
        }

# --- ROTA PRINCIPAL DO SIMULADO CMB ---
@app.route('/simulado_cmb', methods=['GET', 'POST'])
@login_required
def simulado_cmb():
    game_type = 'simulado_cmb'
    
    # Inicializa o simulado na sessão se for a primeira vez
    if 'simulado_state' not in session:
        session['simulado_state'] = {
            'questao_atual': 1,
            'total_questoes': 10,
            'acertos': 0
        }
        # Gera a primeira questão
        session['questao_cmb'] = gerar_questao_cmb()

    state = session['simulado_state']
    questao = session.get('questao_cmb')

    if request.method == 'POST':
        resposta_aluno = request.form.get('resposta')
        
        if not resposta_aluno:
            flash('Soldado, você precisa escolher uma alternativa!', 'warning')
            return redirect(url_for('simulado_cmb'))

        is_correct = (resposta_aluno == questao['correto'])
        
        if is_correct:
            state['acertos'] += 1
            flash('✅ Afirmativo! Resposta correta.', 'success')
        else:
            flash(f'❌ Negativo! A resposta correta era: {questao["correto"]}', 'error')
        
        # Salva a tentativa no banco
        attempt = Attempt(
            student_id=current_user.id,
            game_type=game_type,
            question_text=questao['pergunta_texto'],
            correct_answer=questao['correto'],
            user_answer=resposta_aluno,
            is_correct=is_correct,
            stars_earned=0 # Estrelas só no final
        )
        db.session.add(attempt)
        db.session.commit()

        # Avança para a próxima questão
        state['questao_atual'] += 1
        
        # Verifica se o simulado acabou
        if state['questao_atual'] > state['total_questoes']:
            # FIM DO SIMULADO: Calcula estrelas (1 estrela a cada 2 acertos)
            estrelas_ganhas = state['acertos'] // 2
            current_user.total_estrelas += estrelas_ganhas
            db.session.commit()
            
            mensagem_final = f"Simulado Concluído! Você acertou {state['acertos']} de {state['total_questoes']} e ganhou {estrelas_ganhas} estrelas! ⭐"
            flash(mensagem_final, 'success')
            
            # Limpa a sessão
            session.pop('simulado_state', None)
            session.pop('questao_cmb', None)
            return redirect(url_for('dashboard'))
            
        # Gera nova questão se o simulado continuar
        session['questao_cmb'] = gerar_questao_cmb()
        session['simulado_state'] = state
        return redirect(url_for('simulado_cmb'))

    # Se for GET, apenas renderiza a página
    return render_template('simulado_cmb.html', 
                           questao=questao, 
                           state=state, 
                           student=current_user)

@app.route('/cmb_hub')
def cmb_hub():
    return jsonify({
        'mensagem': 'Bem-vindo ao Preparatório CMB, soldado! Escolha sua missão:',
        'missoes': list(MISSOES.values())
    })

@app.route('/cmb_simulado/<missao>')
def cmb_simulado(missao):
    questao = gerar_questao(missao)
    return jsonify({
        'mensagem': f'Missão {MISSOES.get(missao, "Desconhecida")} ativada! Responda com honra, soldado!',
        'questao': questao['pergunta'],
        'resposta_correta': questao['resposta']  # Em produção, não expor resposta
    })


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

def seed_database():
    with app.app_context():
        if Student.query.count() == 0:
            users_data = [
                {'nome': 'João Silva', 'senha': '1234'}
            ]
            for data in users_data:
                student = Student(nome=data['nome'])
                student.set_password(data['senha'])
                db.session.add(student)
            db.session.commit()

# ==========================================
# 4. ROTAS
# ==========================================
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se já estiver logado, vai direto para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Só processa os dados se o formulário for enviado (POST)
    if request.method == 'POST':
        # .strip() remove espaços em branco acidentais no início e no fim do texto
        nome_digitado = request.form.get('nome', '').strip()
        senha = request.form.get('senha', '').strip()

        # Validação de campos vazios
        if not nome_digitado or not senha:
            flash('Nome e senha são obrigatórios.', 'error')
            return render_template('login.html')

        # CORREÇÃO AQUI: Usa func.lower() para ignorar maiúsculas/minúsculas na busca
        # Assim "Ana beatriz", "ANA BEATRIZ" ou "ana beatriz" vão encontrar o mesmo usuário
        student = Student.query.filter(
            func.lower(Student.nome) == func.lower(nome_digitado), 
            Student.ativo == True
        ).first()

        # Verifica se achou o aluno e se a senha bate com o hash
        if student and student.check_password(senha):
            login_user(student, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Nome de usuário ou senha incorretos.', 'error')
            return render_template('login.html')
    
    # Se for GET (apenas acessando a página), mostra o formulário vazio
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', student=current_user)

@app.route('/ranking')
@login_required
def ranking():
    # Busca os top 10 alunos com mais estrelas, em ordem decrescente
    top_alunos = Student.query.filter_by(ativo=True).order_by(Student.total_estrelas.desc()).limit(10).all()
    
    return render_template('ranking.html', top_alunos=top_alunos, student=current_user)

@app.route('/chuva_numeros')
@login_required
def chuva_numeros():
    return render_template('falling.html')

@app.route('/tabuada', methods=['GET', 'POST'])
@login_required
def tabuada():
    # Se for a primeira vez acessando a rota ou se não houver questão na sessão, cria uma nova
    if request.method == 'GET' or 'questao_atual' not in session:
        # Gera números aleatórios de 1 a 9 para a tabuada
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        
        # Salva a questão na sessão para podermos verificar depois
        session['questao_atual'] = {
            'a': a,
            'b': b,
            'correto': a * b,
            'pergunta_texto': f"{a} x {b}"
        }
        session['tentativas_atuais'] = 0

    questao = session['questao_atual']

    if request.method == 'POST':
        try:
            resposta_aluno = int(request.form.get('resposta', '').strip())
        except ValueError:
            flash('Por favor, digite um número válido.', 'error')
            return render_template('exercicio.html', 
                                   questao=questao, 
                                   indice=1, 
                                   nivel=current_user.nivel_tabuada, 
                                   total_estrelas=current_user.total_estrelas)

        session['tentativas_atuais'] += 1
        tentativas = session['tentativas_atuais']

        if resposta_aluno == questao['correto']:
            # Calcula estrelas (3 na primeira, 2 na segunda, 1 na terceira)
            estrelas = 3 if tentativas == 1 else (2 if tentativas == 2 else 1)
            current_user.total_estrelas += estrelas
            db.session.commit()
            
            flash(f'🎉 Correto! Você ganhou {estrelas} estrelas!', 'success')
            
            # Limpa a questão atual para gerar uma nova no próximo GET
            session.pop('questao_atual', None)
            return redirect(url_for('tabuada'))
        else:
            if tentativas >= 3:
                flash(f'❌ A resposta correta era {questao["correto"]}. Vamos para a próxima!', 'error')
                session.pop('questao_atual', None)
                return redirect(url_for('tabuada'))
            else:
                flash('❌ Errado! Tente novamente.', 'error')

    # Renderiza a página enviando todas as variáveis que o HTML precisa
    return render_template('exercicio.html', 
                           questao=questao, 
                           indice=1, # Aqui você pode implementar a lógica de 1 a 10 depois
                           nivel=current_user.nivel_tabuada, 
                           total_estrelas=current_user.total_estrelas)

@app.route('/ordem_operacoes')
@login_required
def ordem_operacoes():
    return render_template('ordem_operacoes.html', student=current_user)

def gerar_expressao_ordem():
    """Gera uma expressão matemática simples de ordem das operações"""
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    c = random.randint(2, 10)
    # Exemplo: 5 + 3 x 4
    expressao = f"{a} + {b} x {c}"
    resultado = a + (b * c) # A multiplicação ocorre primeiro
    return expressao, resultado

@app.route('/exercicio_ordem', methods=['GET', 'POST'])
@login_required
def exercicio_ordem():
    # Se for a primeira vez ou não tiver questão salva, gera uma nova
    if request.method == 'GET' or 'questao_ordem' not in session:
        expressao, resultado = gerar_expressao_ordem()
        
        session['questao_ordem'] = {
            'pergunta_texto': expressao,
            'correto': resultado
        }
        session['tentativas_ordem'] = 0

    questao = session['questao_ordem']

    if request.method == 'POST':
        try:
            resposta_aluno = int(request.form.get('resposta', '').strip())
        except ValueError:
            flash('Por favor, digite um número válido.', 'error')
            return render_template('exercicio.html', 
                                   questao=questao, 
                                   indice=1, 
                                   nivel=current_user.nivel_ordem_operacoes, 
                                   total_estrelas=current_user.total_estrelas)

        session['tentativas_ordem'] += 1
        tentativas = session['tentativas_ordem']

        if resposta_aluno == questao['correto']:
            # Calcula estrelas
            estrelas = 3 if tentativas == 1 else (2 if tentativas == 2 else 1)
            current_user.total_estrelas += estrelas
            db.session.commit()
            
            flash(f'🎉 Correto! Você ganhou {estrelas} estrelas!', 'success')
            session.pop('questao_ordem', None)
            return redirect(url_for('exercicio_ordem'))
        else:
            if tentativas >= 3:
                flash(f'❌ A resposta correta era {questao["correto"]}. Vamos para a próxima!', 'error')
                session.pop('questao_ordem', None)
                return redirect(url_for('exercicio_ordem'))
            else:
                flash('❌ Errado! Lembre-se: Multiplicação primeiro! Tente novamente.', 'error')

    # Reutiliza o mesmo template bonito 'exercicio.html' que ajustamos antes
    return render_template('exercicio.html', 
                           questao=questao, 
                           indice=1, 
                           nivel=current_user.nivel_ordem_operacoes, 
                           total_estrelas=current_user.total_estrelas)

# ==========================================
# 5. INICIALIZAÇÃO
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    
    # Inicia o servidor de forma limpa, sem prints de chaves secretas
    app.run(debug=True, host='0.0.0.0', port=5000)