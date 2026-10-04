import requests
import re
from html import unescape


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

BASE_URL = "http://localhost:5000"

# Mantiene la sesión y las cookies entre solicitudes
sesion = requests.Session()


# --------------------------------------------------
# REGISTRAR USUARIO
# POST /registro
# --------------------------------------------------

def registrar_usuario():

    print("\n--- REGISTRO DE USUARIO ---")

    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")

    datos = {
        "usuario": usuario,
        "contraseña": contraseña
    }

    try:

        respuesta = sesion.post(
            f"{BASE_URL}/registro",
            json=datos
        )

        datos_respuesta = respuesta.json()

        if respuesta.status_code == 201:

            print(
                datos_respuesta.get(
                    "mensaje",
                    "Usuario registrado correctamente."
                )
            )

        else:

            print(
                datos_respuesta.get(
                    "error",
                    "Ocurrió un error durante el registro."
                )
            )

    except requests.exceptions.ConnectionError:

        print(
            "Error: no se pudo conectar con el servidor."
        )


# --------------------------------------------------
# INICIAR SESIÓN
# POST /login
# --------------------------------------------------

def iniciar_sesion():

    print("\n--- INICIO DE SESIÓN ---")

    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")

    datos = {
        "usuario": usuario,
        "contraseña": contraseña
    }

    try:

        respuesta = sesion.post(
            f"{BASE_URL}/login",
            json=datos
        )

        datos_respuesta = respuesta.json()

        if respuesta.status_code == 200:

            print(
                datos_respuesta.get(
                    "mensaje",
                    "Inicio de sesión correcto."
                )
            )

            # Si el login fue correcto,
            # accedemos automáticamente a /tareas
            acceder_tareas()

        else:

            print(
                datos_respuesta.get(
                    "error",
                    "No se pudo iniciar sesión."
                )
            )

    except requests.exceptions.ConnectionError:

        print(
            "Error: no se pudo conectar con el servidor."
        )


# --------------------------------------------------
# ACCEDER A TAREAS
# GET /tareas
# --------------------------------------------------

def acceder_tareas():

    try:

        respuesta = sesion.get(
            f"{BASE_URL}/tareas"
        )

        if respuesta.status_code == 200:

            # Quitar etiquetas HTML
            texto = re.sub(
                r"<[^>]+>",
                "",
                respuesta.text
            )

            # Convertir entidades HTML
            texto = unescape(texto)

            # Limpiar espacios y líneas vacías
            lineas = [
                linea.strip()
                for linea in texto.splitlines()
                if linea.strip()
            ]

            # Quitamos textos que no interesa
            # mostrar en la consola
            lineas_filtradas = []

            for linea in lineas:

                if linea == "Gestión de Tareas":
                    continue

                if linea == "Cerrar sesión":
                    continue

                lineas_filtradas.append(linea)

            print("\n--- TAREAS ---")

            for linea in lineas_filtradas:
                print(linea)

        else:

            print(
                "No se pudo acceder a /tareas."
            )

    except requests.exceptions.ConnectionError:

        print(
            "Error: no se pudo conectar con el servidor."
        )


# --------------------------------------------------
# MENÚ PRINCIPAL
# --------------------------------------------------

def menu():

    while True:

        print("\n--- SISTEMA DE GESTIÓN DE TAREAS ---")

        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input(
            "Elegí una opción: "
        )

        if opcion == "1":

            registrar_usuario()

        elif opcion == "2":

            iniciar_sesion()

        elif opcion == "3":

            print(
                "Cliente finalizado."
            )

            break

        else:

            print(
                "Opción inválida."
            )


# --------------------------------------------------
# INICIO DEL CLIENTE
# --------------------------------------------------

if __name__ == "__main__":

    menu()