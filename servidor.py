from flask import Flask, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------

app = Flask(__name__)

# Necesaria para utilizar sesiones.
# Para este proyecto local utilizamos una clave fija.
app.secret_key = "clave-secreta-pfo2"

DB_NAME = "usuarios.db"


# --------------------------------------------------
# BASE DE DATOS
# --------------------------------------------------

def inicializar_base_datos():
    """
    Crea la base de datos y la tabla de usuarios
    si todavía no existen.
    """

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


# --------------------------------------------------
# REGISTRO DE USUARIOS
# POST /registro
# --------------------------------------------------

@app.route("/registro", methods=["POST"])
def registro():

    datos = request.get_json()

    if not datos:
        return jsonify({
            "error": "No se recibieron datos"
        }), 400

    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")

    if not usuario or not contraseña:
        return jsonify({
            "error": "Usuario y contraseña son obligatorios"
        }), 400

    # La contraseña nunca se guarda en texto plano.
    password_hash = generate_password_hash(contraseña)

    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios (usuario, password_hash)
            VALUES (?, ?)
            """,
            (usuario, password_hash)
        )

        conexion.commit()
        conexion.close()

        return jsonify({
            "mensaje": "Usuario registrado correctamente"
        }), 201

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "El usuario ya existe"
        }), 409

    except sqlite3.Error as error:

        return jsonify({
            "error": f"Error de base de datos: {error}"
        }), 500


# --------------------------------------------------
# INICIO DE SESIÓN
#
# GET  /login -> formulario para el navegador
# POST /login -> login desde navegador o cliente.py
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    # ----------------------------------------------
    # LOGIN DESDE NAVEGADOR
    # ----------------------------------------------

    if request.method == "GET":

        return """
        <!DOCTYPE html>

        <html>

        <head>
            <meta charset="UTF-8">
            <title>Iniciar sesión</title>
        </head>

        <body>

            <h1>Iniciar sesión</h1>

            <form method="POST">

                <label>Usuario:</label>
                <br>

                <input
                    type="text"
                    name="usuario"
                    required
                >

                <br><br>

                <label>Contraseña:</label>
                <br>

                <input
                    type="password"
                    name="contraseña"
                    required
                >

                <br><br>

                <button type="submit">
                    Iniciar sesión
                </button>

            </form>

        </body>

        </html>
        """

    # ----------------------------------------------
    # RECIBIR CREDENCIALES
    # ----------------------------------------------

    # Si los datos vienen del cliente de consola,
    # llegan en formato JSON.
    if request.is_json:

        datos = request.get_json()

        usuario = datos.get("usuario")
        contraseña = datos.get("contraseña")

        origen_json = True

    # Si vienen del formulario HTML,
    # llegan como datos de formulario.
    else:

        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")

        origen_json = False


    if not usuario or not contraseña:

        if origen_json:
            return jsonify({
                "error": "Usuario y contraseña son obligatorios"
            }), 400

        return """
        <h1>Error</h1>
        <p>Usuario y contraseña son obligatorios.</p>
        <a href="/login">Volver al login</a>
        """, 400


    # ----------------------------------------------
    # BUSCAR USUARIO EN SQLITE
    # ----------------------------------------------

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT password_hash
        FROM usuarios
        WHERE usuario = ?
        """,
        (usuario,)
    )

    resultado = cursor.fetchone()

    conexion.close()


    # ----------------------------------------------
    # USUARIO NO ENCONTRADO
    # ----------------------------------------------

    if resultado is None:

        if origen_json:

            return jsonify({
                "error": "Credenciales inválidas"
            }), 401

        return """
        <h1>Credenciales inválidas</h1>
        <p>Usuario o contraseña incorrectos.</p>
        <a href="/login">Volver al login</a>
        """, 401


    password_hash = resultado[0]


    # ----------------------------------------------
    # VERIFICAR CONTRASEÑA
    # ----------------------------------------------

    if check_password_hash(password_hash, contraseña):

        # Guardar al usuario en la sesión.
        session["usuario"] = usuario

        # Cliente de consola
        if origen_json:

            return jsonify({
                "mensaje": "Inicio de sesión correcto"
            }), 200

        # Navegador
        return redirect(
            url_for("tareas")
        )


    # ----------------------------------------------
    # CONTRASEÑA INCORRECTA
    # ----------------------------------------------

    if origen_json:

        return jsonify({
            "error": "Credenciales inválidas"
        }), 401

    return """
    <h1>Credenciales inválidas</h1>
    <p>Usuario o contraseña incorrectos.</p>
    <a href="/login">Volver al login</a>
    """, 401


# --------------------------------------------------
# GESTIÓN DE TAREAS
# GET /tareas
# --------------------------------------------------

@app.route("/tareas", methods=["GET"])
def tareas():

    # Si no existe una sesión iniciada,
    # enviar al usuario al login.
    if "usuario" not in session:

        return redirect(
            url_for("login")
        )

    usuario = session["usuario"]

    return f"""
    <!DOCTYPE html>

    <html>

    <head>
        <meta charset="UTF-8">
        <title>Gestión de Tareas</title>
    </head>

    <body>

        <h1>Bienvenido al Sistema de Gestión de Tareas</h1>

        <p>
            Usuario conectado: <strong>{usuario}</strong>
        </p>

        <p>
            API funcionando correctamente.
        </p>

        <br>

        <a href="/logout">
            Cerrar sesión
        </a>

    </body>

    </html>
    """


# --------------------------------------------------
# CERRAR SESIÓN
#
# Funcionalidad adicional para el navegador.
# --------------------------------------------------

@app.route("/logout", methods=["GET"])
def logout():

    session.clear()

    return """
    <!DOCTYPE html>

    <html>

    <head>
        <meta charset="UTF-8">
        <title>Sesión cerrada</title>
    </head>

    <body>

        <h1>Sesión cerrada</h1>

        <p>
            La sesión se cerró correctamente.
        </p>

        <a href="/login">
            Iniciar sesión nuevamente
        </a>

    </body>

    </html>
    """


# --------------------------------------------------
# INICIO DEL SERVIDOR
# --------------------------------------------------

if __name__ == "__main__":

    inicializar_base_datos()

    app.run(
        host="localhost",
        port=5000,
        debug=True
    )