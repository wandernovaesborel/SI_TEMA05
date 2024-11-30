from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob
from googletrans import Translator  # Biblioteca de tradução

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Inicializar o tradutor
translator = Translator()

# Modelo do banco de dados
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    sentimento = db.Column(db.String(50), nullable=False)

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        comentario_texto = request.form['comentario']

        # Traduzir comentário para inglês
        traducao = translator.translate(comentario_texto, src='pt', dest='en')
        texto_em_ingles = traducao.text

        # Analisar sentimento em inglês
        analise = TextBlob(texto_em_ingles)
        sentimento = 'Positivo' if analise.sentiment.polarity > 0 else 'Negativo' if analise.sentiment.polarity < 0 else 'Neutro'

        # Traduzir o sentimento de volta para português
        sentimento_traduzido = {
            'Positivo': 'Positivo',
            'Negativo': 'Negativo',
            'Neutro': 'Neutro'
        }[sentimento]

        # Salvar no banco de dados
        novo_comentario = Comentario(texto=comentario_texto, sentimento=sentimento_traduzido)
        db.session.add(novo_comentario)
        db.session.commit()
        return redirect('/')

    # Filtragem opcional por sentimento
    filtro = request.args.get('filtro')
    if filtro:
        comentarios = Comentario.query.filter_by(sentimento=filtro).all()
    else:
        comentarios = Comentario.query.all()
    
    return render_template('index.html', comentarios=comentarios, filtro=filtro)

# Rota para dados do gráfico
@app.route('/chart-data')
def chart_data():
    positivo = Comentario.query.filter_by(sentimento='Positivo').count()
    negativo = Comentario.query.filter_by(sentimento='Negativo').count()
    neutro = Comentario.query.filter_by(sentimento='Neutro').count()
    return jsonify({"positivo": positivo, "negativo": negativo, "neutro": neutro})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados dentro do contexto da aplicação
    app.run(debug=True)
