from flask import Flask, render_template, request, redirect, url_for, session
import random

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

if __name__ == '__main__':
    print("🚀 Tabuada Master rodando! Acesse http://127.0.0.1:5000")
    app.run(debug=True)