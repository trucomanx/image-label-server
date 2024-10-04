import os
import sqlite3
import json
from flask import Flask, request, jsonify, send_file, Response
from io import BytesIO
from mimetypes import guess_type
#from werkzeug.security import check_password_hash
from pathlib import Path
import sys
import functools

# Configurações
EX_USER_STRING="""
{
    "user":"username",
    "password":"clave"
}
"""
EX_DB_STRING="""
{
    "dataset_name":"NAMEDB",
    "labels":["positive","negative","neutral","pain","other"],
    "base_dir":"/some/path/directory",
    "samples": [
        {"filepath":"relative/path/of/image1.png", "label":"neutral"},
        {"filepath":"relative/path/of/image2.jpeg", "label":""},
        {"filepath":"relative/path/of/image3.bmp", "label":"positive"}
    ]
}
"""
CONFIG_PATH = os.path.expanduser("~/.config/image-label-server/config.json")

##
JSON_DB_DIR = None;
SQLITE_DB_DIR = None;
JSON_USER_DIR = None;

app = Flask(__name__)

# Funções Auxiliares
def load_users():
    users = {}
    for user_file in Path(JSON_USER_DIR).glob('*.json'):
        with open(user_file, 'r') as f:
            user_data = json.load(f)
            users[user_data['user']] = user_data['password']
    return users

def auth_required(f):
    @functools.wraps(f)  # Adiciona isto
    def wrapped_function(*args, **kwargs):
        auth = request.authorization
        
        if not auth or not check_password(auth.username, auth.password):
            return jsonify({"message": "Authentication failed"}), 401
        return f(*args, **kwargs)
    return wrapped_function

def check_password(username, password):
    users = load_users()
    
    #if username in users and check_password_hash(users[username], password):
    if username in users and users[username] == password:
        return True
    return False

def init_sqlite_db(dataset_name, json_file):
    os.makedirs(SQLITE_DB_DIR,exist_ok=True)
    db_path = os.path.join(SQLITE_DB_DIR, f"{dataset_name}.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Criando as tabelas
    c.execute('''CREATE TABLE IF NOT EXISTS metadata (dataset_name TEXT, base_dir TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS labels (label TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS samples (filepath TEXT, label TEXT)''')
    
    # Inserindo dados do JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
        c.execute('INSERT INTO metadata VALUES (?, ?)', (data['dataset_name'], data['base_dir']))
        for label in data['labels']:
            c.execute('INSERT INTO labels VALUES (?)', (label,))
        for sample in data['samples']:
            c.execute('INSERT INTO samples VALUES (?, ?)', (sample['filepath'], sample['label']))
    
    conn.commit()
    conn.close()

def load_datasets():
    for json_file in Path(JSON_DB_DIR).glob('*.json'):
        with open(json_file, 'r') as f:
            data = json.load(f)
            db_path = os.path.join(SQLITE_DB_DIR, f"{data['dataset_name']}.db")
            if not os.path.exists(db_path):
                init_sqlite_db(data['dataset_name'], json_file)

# Verificação inicial de bases de dados e usuários
def verify_initial_conditions():
    # Verificar se há bases de dados no diretório SQLITE_DB_DIR
    if not list(Path(SQLITE_DB_DIR).glob('*.db')):
        print(f"Error: No database found in {SQLITE_DB_DIR}. The server cannot start.")
        print(f"Aggregate new databases by adding a *.json file into {JSON_DB_DIR}. Using the next format:")
        print(EX_DB_STRING)
        print(f"Or modify the sqlite_db_dir value in the config file {CONFIG_PATH}")
        sys.exit(1)

    # Verificar se há usuários no diretório JSON_USER_DIR
    if not list(Path(JSON_USER_DIR).glob('*.json')):
        print(f"Error: No user found in {JSON_USER_DIR}. The server cannot start.")
        print(f"Aggregate new databases by adding a *.json file into {JSON_USER_DIR}. Using the next format:")
        print(EX_USER_STRING)
        print(f"Or modify the json_user_dir value in the config file {CONFIG_PATH}")
        sys.exit(1)

# Rotas
@app.route('/size', methods=['POST'])
@auth_required
def size():
    data = request.json
    dataset_name = data.get("dataset_name")
    db_path = os.path.join(SQLITE_DB_DIR, f"{dataset_name}.db")
    
    if not os.path.exists(db_path):
        return jsonify({"message": "Database not found"}), 404

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM samples')
    size = c.fetchone()[0]
    conn.close()

    return jsonify({"dataset_name": dataset_name, "size": size})

@app.route('/obtain', methods=['POST'])
@auth_required
def obtain():
    data = request.json
    dataset_name = data.get("dataset_name")
    image_id = data.get("id")

    db_path = os.path.join(SQLITE_DB_DIR, f"{dataset_name}.db")
    
    if not os.path.exists(db_path):
        print(f"The file {db_path} doesn't exist!")
        return jsonify({"message": "Database not found"}), 404

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Recupera o base_dir da tabela de metadados
    c.execute('SELECT base_dir FROM metadata WHERE dataset_name = ?', (dataset_name,))
    base_dir_row = c.fetchone()
    
    if not base_dir_row:
        return jsonify({"message": "Metadata not found"}), 404
    
    base_dir = base_dir_row[0]

    if image_id >= 0:
        c.execute('SELECT filepath FROM samples WHERE rowid = ?', (image_id + 1,))
    else:
        c.execute('SELECT filepath FROM samples WHERE label = "" LIMIT 1')

    sample = c.fetchone()
    
    if not sample:
        return jsonify({"message": "Sample not found"}), 404

    # Recupera todas as labels da tabela de labels
    c.execute('SELECT label FROM labels')
    labels = [row[0] for row in c.fetchall()]

    conn.close()

    # Monta o caminho completo da imagem
    image_path = os.path.join(base_dir, sample[0])

    # Verifica se o arquivo da imagem existe
    if not os.path.exists(image_path):
        return jsonify({"message": "Image file not found"}), 404

    # Determina o tipo MIME da imagem
    mime_type, _ = guess_type(image_path)

    # Carrega a imagem como um arquivo binário
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()

    # Cria o JSON com as informações desejadas
    response_json = {
        "dataset_name": dataset_name,
        "base_dir": base_dir,
        "filepath": sample[0],
        "labels": labels  # Aqui, pegamos todas as labels da tabela
    }

    # Retorna a imagem como resposta e o JSON em um dicionário separado
    response = send_file(BytesIO(img_data), mimetype=mime_type)
    response.headers['X-Response-Json'] = json.dumps(response_json)  # Modificado para usar json.dumps()
    return response

@app.route('/classify', methods=['POST'])
@auth_required
def classify():
    data = request.json
    dataset_name = data.get("dataset_name")
    base_dir = data.get("base_dir")
    filepath = data.get("filepath")
    label = data.get("label")

    db_path = os.path.join(SQLITE_DB_DIR, f"{dataset_name}.db")
    if not os.path.exists(db_path):
        return jsonify({"response": False}), 404

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('SELECT label FROM labels WHERE label = ?', (label,))
    if not c.fetchone():
        return jsonify({"response": False})

    c.execute('UPDATE samples SET label = ? WHERE filepath = ?', (label, filepath))
    conn.commit()
    conn.close()

    return jsonify({"response": True})

def load_config_info(config_path):
    default_config = {
        "json_db_dir": os.path.expanduser("~/.config/image-label-server/json_data"),
        "sqlite_db_dir": os.path.expanduser("~/.config/image-label-server/sqlite_dbs"),
        "json_user_dir": os.path.expanduser("~/.config/image-label-server/json_users")
    }

    # Se o diretório não existir, crie-o
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Se o arquivo não existir, crie-o com os valores padrão
    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        return default_config["json_db_dir"], default_config["sqlite_db_dir"], default_config["json_user_dir"]
    
    # Carrega o arquivo de configuração existente
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    # Preenche com valores padrão se alguma chave estiver faltando
    updated_config = {**default_config, **config}
    
    # Se algum valor foi adicionado, atualize o arquivo
    if config != updated_config:
        with open(config_path, 'w') as config_file:
            json.dump(updated_config, config_file, indent=4)

    return updated_config["json_db_dir"], updated_config["sqlite_db_dir"], updated_config["json_user_dir"]

def main():
    global JSON_DB_DIR, SQLITE_DB_DIR, JSON_USER_DIR
    JSON_DB_DIR, SQLITE_DB_DIR, JSON_USER_DIR = load_config_info(CONFIG_PATH)
    
    # Carregar datasets existentes
    load_datasets()
    
    # Verificar se há bases de dados e usuários antes de iniciar o servidor
    verify_initial_conditions()
    
    # Iniciar o servidor
    app.run(host="0.0.0.0",port=44444, debug=True)
    #app.run(host="0.0.0.0",port=44444, debug=False, ssl_context=('path/to/cert.pem', 'path/to/key.pem')) # transmicion encriptada 


if __name__ == "__main__":
    main()
    
