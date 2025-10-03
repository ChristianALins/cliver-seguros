print("Teste simples funcionando!")
print("Diretorio de trabalho OK!")

from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Cliver Seguros - Teste OK!"

if __name__ == '__main__':
    print("Iniciando servidor de teste...")
    app.run(debug=True, port=5004, host='0.0.0.0')