from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configurações do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'mypy2',
    'port': 7306,
}

# Função para análise de sentimentos com pesos
def analise_sentimento(texto):
    palavras_positivas = get_palavras_positivas()
    palavras_negativas = get_palavras_negativas()

    pontuacao = 0
    for palavra in texto.split():
        if palavra in palavras_positivas:
            peso = get_peso_palavra(palavra, 'positiva')
            pontuacao += peso
        elif palavra in palavras_negativas:
            peso = get_peso_palavra(palavra, 'negativa')
            pontuacao -= peso

    if pontuacao > 0:
        return 'positivo'
    elif pontuacao < 0:
        return 'negativo'
    else:
        return 'neutro'

# Função para obter peso da palavra do banco de dados
def get_peso_palavra(palavra, tipo):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT peso FROM palavras_positivas WHERE palavra = %s" if tipo == 'positiva' else "SELECT peso FROM palavras_negativas WHERE palavra = %s", (palavra,))
    peso = cursor.fetchone()[0]
    conn.close()
    return peso if peso else 0

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
    peso = int(request.form['peso'])

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if tipo == 'positiva':
        cursor.execute("INSERT INTO palavras_positivas (palavra, peso) VALUES (%s, %s)", (palavra, peso))
    elif tipo == 'negativa':
        cursor.execute("INSERT INTO palavras_negativas (palavra, peso) VALUES (%s, %s)", (palavra, peso))

    conn.commit()
    conn.close()

    # Redirecionar de volta à página inicial após ação
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
