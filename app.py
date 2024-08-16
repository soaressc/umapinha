from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

# Código que configura uma aplicação web com o framework Flask, utilizando o SQLAlchemy 
# para lidar com o banco de dados e Flask-Migrate para gerenciar migrações de banco de dados

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Conexão com o banco de dados
        try:
            db.engine.connect()
        # Feedback sobre a conexão
            print("Conexão com o banco de dados bem-sucedida!")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
    app.run(debug=True)