from flask import jsonify, render_template, redirect, url_for, request, session, flash
from app import app, db
from models import Status_Jogo, Usuario, Jogo, Questao, Alternativa, Alternativa_Correta, Andar

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mapaGeral')
def mapaGeral():
    return render_template('mapaGeral.html')

@app.route('/andar/<int:numero>')
def andar(numero):
    andar = Andar.query.get_or_404(numero)
    return render_template('andar.html', andar=andar)

@app.route('/andar1')
def andar1():
    return render_template('andar1.html')

@app.route('/andar2')
def andar2():
    return render_template('andar2.html')

@app.route('/andar3')
def andar3():
    return render_template('andar3.html')

@app.route('/andar4')
def andar4():
    andar = Andar.query.get_or_404(4)
    return render_template('andar4.html', andar=andar)

@app.route('/andar5')
def andar5():
    return render_template('andar5.html')

@app.route('/perguntaAndar4Final')
def perguntaAndar4Final():
    return render_template('perguntaAndar4Final.html')

@app.route('/check_answer', methods=['POST'])
def check_answer():
    try:
        dados = request.get_json()
        resposta_usuario = dados.get('resposta')
        texto_resposta_correta = dados.get('texto_resposta_correta')

        if not resposta_usuario or not texto_resposta_correta:
            return jsonify({'resultado': 'Dados inválidos recebidos.'}), 400

        questao_id = session.get('questao_id')
        questao = Questao.query.get(questao_id)

        if not questao:
            return jsonify({'resultado': 'Questão não encontrada.'}), 404

        resposta_correta = questao.alternativa_correta.texto_alternativa
        jogo = Jogo.query.get(questao.id_jogo)

        if resposta_usuario == resposta_correta:
            questao.respondida = True
            
            andar = Andar.query.get(questao.numero)
            if andar:
                todas_questoes_respondidas = all(q.respondida for q in Questao.query.filter_by(numero=questao.numero).all())
                if todas_questoes_respondidas:
                    andar.concluido = True
                    db.session.commit()

                    # Verifica se todos os andares estão concluídos
                    todos_andares_concluidos = all(a.concluido for a in Andar.query.filter_by(id_usuario=jogo.id_usuario).all())
                    if todos_andares_concluidos:
                        # O jogo foi concluído com sucesso
                        return jsonify({
                            'resultado': 'Resposta correta!',
                            'vidas': jogo.vidas,
                            'jogo_acabado': True,
                            'redirecionar': url_for('status_jogo', id_usuario=jogo.id_usuario)
                        })
                    else:
                        return jsonify({
                            'resultado': 'Resposta correta!',
                            'vidas': jogo.vidas,
                            'jogo_acabado': False,
                            'redirecionar': False
                        })

        else:
            jogo.vidas -= 1
            db.session.commit()

            if jogo.vidas <= 0:
                # O jogo acabou porque o jogador ficou sem vidas
                return jsonify({
                    'resultado': 'Resposta incorreta! Você ficou sem vidas.',
                    'vidas': jogo.vidas,
                    'jogo_acabado': True,
                    'redirecionar': url_for('status_jogo', id_usuario=jogo.id_usuario)
                })
            else:
                return jsonify({
                    'resultado': 'Resposta incorreta!',
                    'vidas': jogo.vidas,
                    'jogo_acabado': False
                })

    except Exception as e:
        return jsonify({'resultado': 'Ocorreu um erro no servidor.'}), 500

@app.route('/reiniciar_jogo')
def reiniciar_jogo():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('login'))  # Redireciona para a página de login se o usuário não estiver autenticado

    try:
        # Redefinir vidas para 3
        jogo = Jogo.query.filter_by(id_usuario=id_usuario).first()
        if jogo:
            jogo.vidas = 3

        # Redefinir status dos andares
        andares = Andar.query.filter_by(id_usuario=id_usuario).all()
        for andar in andares:
            if andar.numero in [1, 2, 4]:
                andar.concluido = 0

        # Commit das alterações no banco de dados
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback em caso de erro
        print(f'Erro ao reiniciar o jogo: {e}')
        return 'Ocorreu um erro ao reiniciar o jogo', 500

    flash('O jogo foi reiniciado com sucesso!', 'success')
    return redirect(url_for('andar1'))  # Redirecionar para o primeiro andar ou outra página inicial

# Rota que renderiza a questão
@app.route('/questao/<int:id_questao>')
def exibir_questao(id_questao):
    questao = Questao.query.get_or_404(id_questao)
    alternativas = Alternativa.query.filter_by(id_questao=questao.id_questao).all()
    if not questao:
        return 'Questão não encontrada', 404
    session['questao_id'] = id_questao  # Armazena o ID da questão na sessão

    return render_template('questao.html', questao=questao, alternativas=alternativas, texto_alternativa=questao.alternativa_correta.texto_alternativa)

@app.route('/proxima_questao')
def proxima_questao():
    jogo = Jogo.query.get(session['id_jogo'])
    questao = Questao.query.filter_by(id_jogo=jogo.id_jogo).first()
    if not questao:
        return redirect(url_for('fim_jogo'))
    return redirect(url_for('questao', id_questao=questao.id_questao))

@app.route('/status_jogo/<int:id_usuario>')
def status_jogo(id_usuario):
    # Consulta a view Status_Jogo para o usuário específico
    status_jogo_list = Status_Jogo.query.filter_by(id_usuario=id_usuario).all()
    
    # Verifica se algum jogo está concluído
    jogos_concluidos = any(sj.status_jogo == 'Concluído' for sj in status_jogo_list)

    # Pega o jogo associado ao usuário e obtém o número de vidas
    jogo = Jogo.query.filter_by(id_usuario=id_usuario).first()
    
    # Verifica se o jogo existe e obtém o número de vidas
    vidas = jogo.vidas if jogo else 0
    
    if vidas <= 0:
        mensagem = "Game Over!"
        mensagem2 = "Não foi dessa vez!"
        imagem = url_for('static', filename='imagens/game-over.png')
    elif jogos_concluidos:
        mensagem = "Parabéns!"
        mensagem2 = "Você concluiu todos os andares!"
        imagem = url_for('static', filename='imagens/trofeu.png')
    else:
        mensagem = "Continue jogando! Você ainda tem andares para concluir."

    # Renderiza o template com a lista de status dos jogos e as vidas
    return render_template('status_jogo.html', status_jogo_list=status_jogo_list, jogos_concluidos=jogos_concluidos, vidas=vidas, mensagem=mensagem, mensagem2=mensagem2, imagem=imagem)

# Rota para o login de usuário
# Método GET apresenta o HTML
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Cria a requisião de POST com email e senha do usuário
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Busca o primeiro usuário com o email inserido na tabela
        user = Usuario.query.filter_by(email=email).first()
        
        if user and user.senha == password:  # Comparando senha
            
            session['user_id'] = user.id_usuario  # Armazenar o ID do usuário na sessão
            session.permanent = True  # Torna a sessão permanente
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Email ou senha inválidos!'})

    return render_template('login.html')

# Rota para verificar se o e-mail foi cadastrado no banco de dados
@app.route('/verificar-email', methods=['POST'])
def verificar_email():
    email = request.json['email']
    user = Usuario.query.filter_by(email=email).first()
    return jsonify({'exists': user is not None})

# Rota para página de cadastro
# Método GET apresenta o HTML
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    # Cria a requisição com as informações do usuário
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        # Verifica se a confirmação de senha está correta
        if password != confirm_password:
            # Mostra no prompt a não confirmação e retorna pra cadastro
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('cadastro'))
        
        # Instancia o novo usuário no banco de dados e relaciona
        # valor dos inputs com as colunas da tabela
        new_user = Usuario(nome=name, email=email, senha=password)
        
        # Tenta dar insert do usuário acima, dá commit se tiver sucesso
        # e rollback se houver algum erro
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()  # Reverte em caso de erro
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
            return jsonify({'success': False, 'errors': {'message': 'Erro ao criar usuário'}})
    
    return render_template('cadastro.html')