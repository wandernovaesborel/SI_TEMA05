from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# Configurações do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'mypy',
    'port': 7306,
}

# Função para análise de sentimentos simples
def analise_sentimento(texto):
    # Aqui você pode implementar suas regras para determinar o sentimento do texto
    # Por exemplo, contar palavras positivas e negativas e calcular uma pontuação de sentimento
    # Este é um exemplo muito simplificado apenas para ilustração
    palavras_positivas = get_palavras_positivas()
    palavras_negativas = get_palavras_negativas()

    pontuacao = 0
    for palavra in texto.split():
        if palavra in palavras_positivas:
            pontuacao += 1
        elif palavra in palavras_negativas:
            pontuacao -= 1

    if pontuacao > 0:
        return 'positivo'
    elif pontuacao < 0:
        return 'negativo'
    else:
        return 'neutro'

# Função para obter palavras positivas do banco de dados
def get_palavras_positivas():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT palavra FROM palavras_positivas")
    palavras_positivas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return palavras_positivas

# Função para obter palavras negativas do banco de dados
def get_palavras_negativas():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT palavra FROM palavras_negativas")
    palavras_negativas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return palavras_negativas

# Rota para página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para análise de sentimentos
@app.route('/analise-sentimento', methods=['POST'])
def analisar_sentimento():
    texto = request.form['texto']

    # Realizar análise de sentimento
    sentimento = analise_sentimento(texto)

    return render_template('resultado.html', sentimento=sentimento)

# Rota para adicionar palavras positivas e negativas
@app.route('/adicionar-palavra', methods=['POST'])
def adicionar_palavra():
    palavra = request.form['palavra']
    tipo = request.form['tipo']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if tipo == 'positiva':
        cursor.execute("INSERT INTO palavras_positivas (palavra) VALUES (%s)", (palavra,))
    elif tipo == 'negativa':
        cursor.execute("INSERT INTO palavras_negativas (palavra) VALUES (%s)", (palavra,))

    conn.commit()
    conn.close()

    return 'Palavra adicionada com sucesso!'

if __name__ == '__main__':
    app.run(debug=True)
