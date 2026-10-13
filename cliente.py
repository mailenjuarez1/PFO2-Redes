import requests
import webbrowser

URL_BASE = 'http://127.0.0.1:5000'
usuario_logueado = None  # Variable global para "recordar" quién inició sesión

def registrar():
    print("\n--- NUEVO REGISTRO ---")
    usuario = input("Ingrese su usuario: ")
    password = input("Ingrese su contraseña: ")
    datos = {"usuario": usuario, "contraseña": password}
    try:
        respuesta = requests.post(f"{URL_BASE}/registro", json=datos)
        print(f"\nServidor responde: {respuesta.json()}")
    except requests.exceptions.ConnectionError:
        print("\nError: No se pudo conectar al servidor.")

def iniciar_sesion():
    global usuario_logueado
    print("\n--- INICIO DE SESIÓN ---")
    usuario = input("Ingrese su usuario: ")
    password = input("Ingrese su contraseña: ")
    datos = {"usuario": usuario, "contraseña": password}
    try:
        respuesta = requests.post(f"{URL_BASE}/login", json=datos)
        datos_respuesta = respuesta.json()
        print(f"\nServidor responde: {datos_respuesta}")
        
        # Si el login fue exitoso, guardamos el usuario
        if respuesta.status_code == 200:
            usuario_logueado = usuario
    except requests.exceptions.ConnectionError:
        print("\nError: No se pudo conectar al servidor.")

def agregar_tarea():
    global usuario_logueado
    if not usuario_logueado:
        print("\n[!] Error: Debes iniciar sesión primero para agregar tareas.")
        return
        
    print("\n--- AGREGAR TAREA ---")
    descripcion = input("Escribí tu nueva tarea: ")
    datos = {"usuario": usuario_logueado, "descripcion": descripcion}
    
    respuesta = requests.post(f"{URL_BASE}/api/tareas", json=datos)
    print(f"\nServidor responde: {respuesta.json()}")

def listar_tareas():
    global usuario_logueado
    if not usuario_logueado:
        print("\n[!] Error: Debes iniciar sesión primero para ver tus tareas.")
        return
        
    print(f"\n--- TAREAS DE {usuario_logueado.upper()} ---")
    respuesta = requests.get(f"{URL_BASE}/api/tareas/{usuario_logueado}")
    datos = respuesta.json()
    
    lista = datos.get("tareas", [])
    if len(lista) == 0:
        print("No tenés tareas guardadas todavía.")
    else:
        for tarea in lista:
            print(f" -> [{usuario_logueado.capitalize()}] {tarea['descripcion']}")

def ver_html_bienvenida():
    global usuario_logueado
    if not usuario_logueado:
        print("\n[!] Error: Debes iniciar sesión primero para ver tu panel web.")
        return
        
    print("\nAbriendo la interfaz visual en tu navegador web...")
    # Ahora la URL incluye al usuario, ej: /tareas/mailen
    webbrowser.open(f"{URL_BASE}/tareas/{usuario_logueado}")

def iniciar_cliente():
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Ver interfaz web de bienvenida")
        print("4. Agregar una nueva tarea")
        print("5. Listar mis tareas")
        print("6. Salir")
        
        opcion = input("Elegí una opción: ")
        
        if opcion == '1':
            registrar()
        elif opcion == '2':
            iniciar_sesion()
        elif opcion == '3':
            ver_html_bienvenida()
        elif opcion == '4':
            agregar_tarea()
        elif opcion == '5':
            listar_tareas()
        elif opcion == '6':
            print("Cerrando el cliente...")
            break
        else:
            print("Opción inválida.")

if __name__ == '__main__':
    iniciar_cliente()