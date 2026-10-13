from flask import Flask, request, jsonify, render_template
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_NAME = "tareas.db"

def inicializar_db():
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        # Tabla de usuarios original
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        # NUEVA: Tabla de tareas vinculada al usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
            )
        ''')
        conexion.commit()

@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    usuario = data.get('usuario')
    password = data.get('contraseña')

    if not usuario or not password:
        return jsonify({"error": "Datos incompletos"}), 400

    hash_pwd = generate_password_hash(password)

    try:
        with sqlite3.connect(DB_NAME) as conexion:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)", (usuario, hash_pwd))
            conexion.commit()
        return jsonify({"mensaje": "Registro exitoso"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya se encuentra registrado"}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    password = data.get('contraseña')

    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()

    if resultado and check_password_hash(resultado[0], password):
        return jsonify({"mensaje": "Acceso validado a las tareas"}), 200
    else:
        return jsonify({"error": "Credenciales incorrectas"}), 401

# --- NUEVOS ENDPOINTS PARA LA API DE TAREAS ---

@app.route('/api/tareas', methods=['POST'])
def agregar_tarea():
    data = request.get_json()
    usuario = data.get('usuario')
    descripcion = data.get('descripcion')

    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO tareas (usuario, descripcion) VALUES (?, ?)", (usuario, descripcion))
        conexion.commit()
    
    return jsonify({"mensaje": "Tarea guardada exitosamente"}), 201

@app.route('/api/tareas/<usuario>', methods=['GET'])
def listar_tareas(usuario):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, descripcion FROM tareas WHERE usuario = ?", (usuario,))
        tareas_db = cursor.fetchall()
    
    # Transformamos el resultado de la base de datos a una lista de diccionarios JSON
    lista_tareas = [{"id": fila[0], "descripcion": fila[1]} for fila in tareas_db]
    return jsonify({"tareas": lista_tareas}), 200

# --- FIN NUEVOS ENDPOINTS ---

@app.route('/tareas/<usuario>', methods=['GET'])
def tareas(usuario):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT descripcion FROM tareas WHERE usuario = ?", (usuario,))
        tareas_db = cursor.fetchall()
    
    # Extraemos solo el texto de las tareas en una lista de Python
    lista_tareas = [fila[0] for fila in tareas_db]
    
    # Le enviamos el usuario y las tareas al archivo HTML
    return render_template('bienvenida.html', usuario=usuario, tareas=lista_tareas)

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True, port=5000)