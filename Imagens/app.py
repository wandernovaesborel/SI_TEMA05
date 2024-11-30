from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import tensorflow as tf

# Configurações do Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Carregar o modelo pré-treinado
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Função para verificar a extensão do arquivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Rota principal da página
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return render_template('index.html', error='Nenhum arquivo enviado.')
        
        file = request.files['file']
        
        # Verifica se o arquivo tem um nome válido
        if file.filename == '':
            return render_template('index.html', error='Nenhum arquivo selecionado.')
        
        # Verifica se a extensão do arquivo é permitida
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Realiza o reconhecimento de imagem
            predicoes_imagem = reconhecimento_de_imagem(filepath)
            
            # Exibe as predições na página
            return render_template('index.html', predictions=predicoes_imagem)
        else:
            return render_template('index.html', error='Extensão de arquivo não permitida.')
    
    return render_template('index.html')

# Função para reconhecimento de imagem usando TensorFlow
def reconhecimento_de_imagem(image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    
    predictions = model.predict(img_array)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
    
    return decoded_predictions

if __name__ == '__main__':
    app.run(debug=True)
