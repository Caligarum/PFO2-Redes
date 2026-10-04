import sqlite3


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

DB_NAME = "usuarios.db"


# --------------------------------------------------
# MOSTRAR USUARIOS REGISTRADOS
# --------------------------------------------------

def ver_usuarios():

    try:

        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id, usuario, password_hash
            FROM usuarios
        """)

        usuarios = cursor.fetchall()

        conexion.close()

        print("\n--- USUARIOS REGISTRADOS ---\n")

        if not usuarios:

            print("No hay usuarios registrados.")
            return

        for usuario in usuarios:

            print(f"ID: {usuario[0]}")
            print(f"Usuario: {usuario[1]}")
            print(f"Hash de contraseña: {usuario[2]}")
            print("-" * 60)

    except sqlite3.Error as error:

        print(
            f"Error al acceder a la base de datos: {error}"
        )


# --------------------------------------------------
# INICIO
# --------------------------------------------------

if __name__ == "__main__":

    ver_usuarios()