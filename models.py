from app import db

class Usuario(db.Model):
    __tablename__ = 'Usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(300))
    email = db.Column(db.String(245), nullable=False)
    senha = db.Column(db.String(40), nullable=False)

class Andar(db.Model):
    __tablename__ = 'Andar'
    numero = db.Column(db.Integer, primary_key=True)
    concluido = db.Column(db.Boolean)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario'))  # Substitui 'nome'
    usuario = db.relationship('Usuario', backref=db.backref('andares', lazy=True))


class Jogo(db.Model):
    __tablename__ = 'Jogo'
    id_jogo = db.Column(db.Integer, primary_key=True)
    vidas = db.Column(db.Integer, nullable=False)
    feito = db.Column(db.Boolean, default=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario'), nullable=False)
    
    # Relacionamento inverso para acessar as questões relacionadas ao jogo
    questoes = db.relationship('Questao', backref='jogo', lazy=True)

class Questao(db.Model):
    __tablename__ = 'Questao'
    id_questao = db.Column(db.Integer, primary_key=True)
    texto_pergunta = db.Column(db.Text, nullable=False)
    id_jogo = db.Column(db.Integer, db.ForeignKey('Jogo.id_jogo'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario'))
    numero = db.Column(db.Integer, db.ForeignKey('Andar.numero'))
    id_alternativa_correta = db.Column(db.Integer, db.ForeignKey('Alternativa_Correta.id_alternativa_correta'))
    respondida = db.Column(db.Boolean, default=False)

    alternativa_correta = db.relationship('Alternativa_Correta', backref='questao')

class Alternativa_Correta(db.Model):
    __tablename__ = 'Alternativa_Correta'
    id_alternativa_correta = db.Column(db.Integer, primary_key=True)
    texto_alternativa = db.Column(db.Text, nullable=False)

class Alternativa(db.Model):
    __tablename__ = 'Alternativa'
    id_alternativa = db.Column(db.Integer, primary_key=True)
    texto_alternativa = db.Column(db.Text)
    id_questao = db.Column(db.Integer, db.ForeignKey('Questao.id_questao'))

class Status_Jogo(db.Model):
    __tablename__ = 'Status_Jogo'
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_jogo = db.Column(db.Integer, primary_key=True)
    status_jogo = db.Column(db.String(50))
