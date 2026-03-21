import random
import re
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = 'tabuada_magica_123'  # Troque depois para algo mais seguro

# Frases divertidas para gamificação (criança ama!)
feedbacks_certo = ["🎉 MUITO BEM!", "🌟 Você é um gênio!", "🔥 Arrasou!", "😎 Super-herói da matemática!", "⭐ Parabéns, craque!"]
feedbacks_errado = ["😔 Quase! Vamos tentar de novo!", "💪 Na próxima você acerta!", "🙃 Ops! A resposta certa era {}"]

def get_parametros_nivel(nivel):
    """Escalável: fácil adicionar novos níveis depois (C, D, frações, etc.)"""
    if nivel.startswith('A'):
        return 1, 9, 1, 9          # Tabuada completa 1-9
    elif nivel.startswith('B'):
        return 10, 99, 1, 9        # Dezenas e unidades (ex: 12 × 3)
    return 1, 9, 1, 9

@app.route('/')
def home():
    if 'total_score' not in session:
        session['total_score'] = 0
        session['current_level'] = 'A1'
    return render_template('index.html')

@app.route('/iniciar_exercicio')
def iniciar_exercicio():
    """Gera 10 questões novas aleatórias no início de cada fase"""
    nivel = session.get('current_level', 'A1')
    min_a, max_a, min_b, max_b = get_parametros_nivel(nivel)
    
    questoes = []
    for _ in range(10):
        a = random.randint(min_a, max_a)
        b = random.randint(min_b, max_b)
        questoes.append({
            'a': a,
            'b': b,
            'correto': a * b,
            'resposta_aluno': None
        })
    
    session['questoes'] = questoes
    session['indice_atual'] = 0
    session['acertos_fase'] = 0
    return redirect(url_for('exercicio'))

@app.route('/exercicio', methods=['GET', 'POST'])
def exercicio():
    if 'questoes' not in session:
        return redirect(url_for('iniciar_exercicio'))
    
    questoes = session['questoes']
    indice = session['indice_atual']
    
    if request.method == 'POST':
        try:
            resposta = int(request.form['resposta'])
        except:
            resposta = -999  # inválido
        
        questao_atual = questoes[indice]
        if resposta == questao_atual['correto']:
            session['acertos_fase'] += 1
            feedback = random.choice(feedbacks_certo)
        else:
            feedback = random.choice(feedbacks_errado).format(questao_atual['correto'])
        
        questao_atual['resposta_aluno'] = resposta
        session['questoes'] = questoes  # salva
        
        session['indice_atual'] += 1
        
        # Fim da fase (10 questões)
        if session['indice_atual'] >= 10:
            acertos = session['acertos_fase']
            nivel_atual = session['current_level']
            
            # Lógica de subida de nível (exatamente como você pediu)
            if acertos >= 8:  # 80% ou mais = sobe de nível
                if nivel_atual.startswith('A'):
                    sub = int(nivel_atual[1:])
                    novo_nivel = f'A{sub+1}' if sub < 10 else 'B1'
                else:
                    sub = int(nivel_atual[1:]) if nivel_atual[1:].isdigit() else 1
                    novo_nivel = f'B{sub+1}'
                
                session['current_level'] = novo_nivel
                mensagem = f"🎉 PARABÉNS! Você acertou {acertos}/10 e subiu para o nível <strong>{novo_nivel}</strong>!"
            else:
                mensagem = f"💪 Você acertou {acertos}/10. Vamos repetir essa fase para ficar expert!"
                # Não sobe, mas mantém o mesmo nível
            
            session['total_score'] = session.get('total_score', 0) + acertos * 10
            session.pop('questoes', None)
            session.pop('indice_atual', None)
            
            return render_template('fase_completa.html', 
                                   mensagem=mensagem, 
                                   nivel=nivel_atual,
                                   acertos=acertos,
                                   total=session['total_score'])
        
        # Continua para próxima questão
        return redirect(url_for('exercicio'))
    
    # GET: mostra a pergunta atual
    questao = questoes[indice]
    progresso = (indice / 10) * 100
    nivel = session['current_level']
    
    return render_template('question.html',
                           questao=questao,
                           indice=indice + 1,
                           nivel=nivel,
                           progresso=progresso,
                           total_score=session.get('total_score', 0))

# ------------------ ORDEM DAS OPERAÇÕES ------------------

def gerar_expressao_simples(nivel):
    """Gera expressões fáceis para níveis iniciais (O1-O4)"""
    ops = ['+', '-', '*', '/']  # usamos * e / no código, mas mostramos × e ÷
    if nivel <= 2:  # Nível 1-2: 2-3 termos, só parênteses simples ou sem
        num_termos = random.choice([2, 3])
        nums = [random.randint(2, 15) for _ in range(num_termos)]
        op_list = [random.choice(ops) for _ in range(num_termos-1)]
        
        # Chance de colocar parênteses simples
        if random.random() < 0.6 and num_termos >= 3:
            pos = random.randint(1, num_termos-2)
            expr = f"{nums[0]} {op_list[0]} ({nums[1]} {op_list[1]} {nums[2]})"
            if num_termos > 3:
                expr += f" {op_list[2]} {nums[3]}"
        else:
            expr = ' '.join([str(n) if i % 2 == 0 else op_list[i//2] for i, n in enumerate(nums + op_list)])
        
        # Garantir que não divida por zero e resultado inteiro
        try:
            res = eval(expr.replace('×', '*').replace('÷', '/'))
            if not isinstance(res, int) or res <= 0 or '/' in expr and res != int(res):
                return gerar_expressao_simples(nivel)  # tenta de novo
            return expr.replace('*', '×').replace('/', '÷'), int(res)
        except:
            return gerar_expressao_simples(nivel)
    
    else:  # Níveis mais avançados: mais termos, colchetes opcionais
        # ... pode expandir depois
        return gerar_expressao_simples(2)  # placeholder por enquanto

@app.route('/ordem_operacoes')
def ordem_operacoes_home():
    if 'ordem_nivel' not in session:
        session['ordem_nivel'] = 'O1'
        session['ordem_total_score'] = 0
    return render_template('ordem_home.html', nivel=session['ordem_nivel'], total=session.get('ordem_total_score', 0))

@app.route('/iniciar_ordem')
def iniciar_ordem():
    nivel = session.get('ordem_nivel', 'O1')
    subnivel = int(nivel[1:]) if nivel.startswith('O') else 1
    
    questoes = []
    for _ in range(10):
        expr, correto = gerar_expressao_simples(subnivel)
        questoes.append({
            'expressao': expr,
            'correto': correto,
            'resposta_aluno': None
        })
    
    session['ordem_questoes'] = questoes
    session['ordem_indice'] = 0
    session['ordem_acertos'] = 0
    return redirect(url_for('exercicio_ordem'))

@app.route('/exercicio_ordem', methods=['GET', 'POST'])
def exercicio_ordem():
    if 'ordem_questoes' not in session:
        return redirect(url_for('iniciar_ordem'))
    
    questoes = session['ordem_questoes']
    indice = session['ordem_indice']
    
    if request.method == 'POST':
        try:
            resposta = int(request.form['resposta'])
        except:
            resposta = -999
        
        questao_atual = questoes[indice]
        if resposta == questao_atual['correto']:
            session['ordem_acertos'] += 1
            feedback = random.choice(feedbacks_certo)
        else:
            feedback = random.choice(feedbacks_errado).format(questao_atual['correto'])
        
        questao_atual['resposta_aluno'] = resposta
        session['ordem_questoes'] = questoes
        
        session['ordem_indice'] += 1
        
        if session['ordem_indice'] >= 10:
            acertos = session['ordem_acertos']
            nivel_atual = session['ordem_nivel']
            
            if acertos >= 8:
                sub = int(nivel_atual[1:])
                novo_nivel = f'O{sub+1}' if sub < 10 else 'O10'  # pode expandir depois
                session['ordem_nivel'] = novo_nivel
                mensagem = f"🎉 INCRÍVEL! Você acertou {acertos}/10 e subiu para o nível <strong>{novo_nivel}</strong>!"
            else:
                mensagem = f"💪 Você acertou {acertos}/10. Vamos treinar mais esse nível!"
            
            session['ordem_total_score'] = session.get('ordem_total_score', 0) + acertos * 10
            session.pop('ordem_questoes', None)
            session.pop('ordem_indice', None)
            
            return render_template('fase_completa.html', 
                                   mensagem=mensagem, 
                                   nivel=nivel_atual,
                                   acertos=acertos,
                                   total=session['ordem_total_score'],
                                   voltar_url='/ordem_operacoes')
        
        return redirect(url_for('exercicio_ordem'))
    
    questao = questoes[indice]
    progresso = (indice / 10) * 100
    
    return render_template('ordem_question.html',
                           questao=questao,
                           indice=indice + 1,
                           nivel=session['ordem_nivel'],
                           progresso=progresso,
                           total_score=session.get('ordem_total_score', 0))

if __name__ == '__main__':
    import socket
    
    ip = socket.gethostbyname(socket.gethostname())
    print(f"🚀 Tabuada Master rodando!")
    print(f"→ Local:    http://127.0.0.1:5000")
    print(f"→ Rede:     http://{ip}:5000   (teste no celular!)")
    
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)