import os
import random
import re
import argparse
import tkinter as tk
from tkinter import filedialog
from collections import namedtuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import track
from rich import print as rprint
import json
from pathlib import Path
import time
import platform

# Definición de estructura para preguntas
Pregunta = namedtuple('Pregunta', ['numero', 'enunciado', 'opciones', 'correcta'])
DEFAULT_RUTA_ARCHIVO = 'Todas.txt'
CONFIG_FILE = 'config.json'

console = Console()

# Implementación multiplataforma para captura de teclas
if platform.system() == 'Windows':
    import msvcrt
    
    def esperar_tecla():
        """Espera una tecla y devuelve su valor."""
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                return key
            time.sleep(0.05)
    
    def tecla_presionada(key):
        """Verifica si una tecla específica está siendo presionada."""
        if msvcrt.kbhit():
            pressed = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            msvcrt.ungetch(pressed.encode('utf-8'))  # Devuelve la tecla al buffer
            return pressed == key.lower()
        return False
else:
    # En sistemas Unix/Linux/Mac
    try:
        import termios
        import sys
        import select
        
        def esperar_tecla():
            """Espera una tecla y devuelve su valor."""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                # Configurar terminal para lectura sin buffer ni eco
                tty_settings = termios.tcgetattr(fd)
                tty_settings[3] = tty_settings[3] & ~termios.ICANON & ~termios.ECHO
                termios.tcsetattr(fd, termios.TCSANOW, tty_settings)
                
                while True:
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if rlist:
                        key = sys.stdin.read(1).lower()
                        return key
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, old_settings)
        
        def tecla_presionada(key):
            """Verifica si una tecla específica está siendo presionada."""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                # Configurar terminal para lectura sin buffer ni eco
                tty_settings = termios.tcgetattr(fd)
                tty_settings[3] = tty_settings[3] & ~termios.ICANON & ~termios.ECHO
                termios.tcsetattr(fd, termios.TCSANOW, tty_settings)
                
                rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                if rlist:
                    char = sys.stdin.read(1).lower()
                    if char == key.lower():
                        return True
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, old_settings)
            return False
    except (ImportError, ModuleNotFoundError):
        # Fallback para otros sistemas: usar pynput
        try:
            from pynput import keyboard as kb
            
            def esperar_tecla():
                """Espera una tecla y devuelve su valor."""
                key_pressed = [None]
                
                def on_press(key):
                    try:
                        key_pressed[0] = key.char.lower()
                        return False  # Detener el listener
                    except AttributeError:
                        pass
                
                # Crear y iniciar el listener
                with kb.Listener(on_press=on_press) as listener:
                    listener.join()
                
                return key_pressed[0]
            
            def tecla_presionada(key):
                """Verifica si una tecla específica está siendo presionada."""
                is_pressed = [False]
                
                def on_press(k):
                    try:
                        if k.char.lower() == key.lower():
                            is_pressed[0] = True
                            return False
                    except AttributeError:
                        pass
                    return True
                
                with kb.Listener(on_press=on_press) as listener:
                    # Esperamos un corto tiempo para ver si se presiona la tecla
                    time.sleep(0.05)
                    listener.stop()
                
                return is_pressed[0]
        except (ImportError, ModuleNotFoundError):
            # Si todo falla, usamos input() como último recurso
            def esperar_tecla():
                """Espera una tecla y devuelve su valor."""
                return input().lower()
            
            def tecla_presionada(key):
                """Simulación básica con input()."""
                console.print(f"Presione '{key}' o cualquier otra tecla para continuar...")
                pressed = input().lower()
                return pressed == key.lower()

def guardar_configuracion(ultima_ruta=None, ultimo_modo=None):
    """Guarda la configuración en un archivo JSON."""
    config = {}
    
    # Intentar cargar la configuración existente primero
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            pass  # Si hay error, usamos un diccionario vacío
    
    # Actualizar solo los valores proporcionados
    if ultima_ruta is not None:
        config['ultima_ruta'] = ultima_ruta
    if ultimo_modo is not None:
        config['ultimo_modo'] = ultimo_modo
    
    # Guardar la configuración actualizada
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        console.print(f"[yellow]⚠️ No se pudo guardar la configuración: {e}[/yellow]")

def cargar_configuracion():
    """Carga la configuración desde un archivo JSON."""
    config = {
        'ultima_ruta': DEFAULT_RUTA_ARCHIVO,
        'ultimo_modo': '1'
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_cargada = json.load(f)
                # Actualizar solo las claves que existen en el archivo
                for key in config:
                    if key in config_cargada:
                        config[key] = config_cargada[key]
        except Exception as e:
            console.print(f"[yellow]⚠️ Error al cargar la configuración: {e}[/yellow]")
    
    return config

def seleccionar_archivo_dialogo():
    """Muestra un cuadro de diálogo para seleccionar un archivo."""
    # Inicializar Tkinter (oculto)
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal de Tkinter
    
    # Configurar el diálogo de selección de archivos
    config = cargar_configuracion()
    ultima_ruta = config.get('ultima_ruta', DEFAULT_RUTA_ARCHIVO)
    directorio_inicial = os.path.dirname(os.path.abspath(ultima_ruta))
    
    # Mostrar el diálogo de selección de archivos
    archivo_seleccionado = filedialog.askopenfilename(
        title="Seleccione archivo de preguntas",
        initialdir=directorio_inicial,
        filetypes=[
            ("Archivos de texto", "*.txt"),
            ("Todos los archivos", "*.*")
        ]
    )
    
    # Destruir la ventana Tkinter después de usar el diálogo
    root.destroy()
    
    # Si no se seleccionó ningún archivo, regresar la última ruta utilizada
    if not archivo_seleccionado:
        return ultima_ruta
    
    # Guardar la configuración con la nueva ruta
    guardar_configuracion(ultima_ruta=archivo_seleccionado)
    return archivo_seleccionado

def cargar_preguntas(ruta_archivo):
    """Carga las preguntas desde el archivo, manejando opciones con múltiples líneas."""
    preguntas = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = [linea.strip() for linea in f if linea.strip() != '']
    except FileNotFoundError:
        console.print(f"[bold red]❌ Error:[/bold red] Archivo '{ruta_archivo}' no encontrado")
        return preguntas
    except Exception as e:
        console.print(f"[bold yellow]⚠️ Error al leer archivo:[/bold yellow] {str(e)}")
        return preguntas

    num, enunciado, opciones, correcta = None, "", [], None
    estado = 'inicio'

    for linea in lineas:
        if re.match(r'^\d+:$', linea):
            if num is not None and enunciado and len(opciones) == 4 and correcta:
                preguntas.append(Pregunta(numero=num, enunciado=enunciado.strip(), opciones=opciones, correcta=correcta))

            num, enunciado, opciones, correcta = linea[:-1].strip(), "", [], None
            estado = 'pregunta'
        
        elif estado == 'pregunta':
            if re.match(r'^[A-D]\.', linea):
                opciones.append(linea[2:].strip())
                estado = 'opciones'
            else:
                enunciado += " " + linea if enunciado else linea
        
        elif estado == 'opciones':
            if re.match(r'^[A-D]\.', linea):
                opciones.append(linea[2:].strip())
            elif linea.startswith("Correct Answer:"):
                correcta = linea.split("Correct Answer:")[1].strip().split('.')[0]
                estado = 'fin'
            else:
                if opciones:
                    opciones[-1] += " " + linea  # Une líneas en la última opción
                else:
                    enunciado += " " + linea  # Une líneas en el enunciado de la pregunta
    
    if num is not None and enunciado and len(opciones) == 4 and correcta:
        preguntas.append(Pregunta(numero=num, enunciado=enunciado.strip(), opciones=opciones, correcta=correcta))
    
    return preguntas

def mostrar_menu():
    """Muestra el menú de selección con opciones resaltadas y un recuadro ajustado al contenido."""
    os.system('cls' if os.name == 'nt' else 'clear')

    config = cargar_configuracion()
    ultimo_modo = config.get('ultimo_modo', '1')
    
    menu_texto = (
        "[bold cyan]Seleccione el modo de examen:[/bold cyan]\n\n"
        f"1️⃣  [yellow]Paso a paso[/yellow] (Preguntas en orden con retroalimentación) {'[bright_black][último usado][/bright_black]' if ultimo_modo == '1' else ''}\n"
        f"2️⃣  [yellow]Paso a paso (random)[/yellow] (Preguntas aleatorias con retroalimentación) {'[bright_black][último usado][/bright_black]' if ultimo_modo == '2' else ''}\n"
        f"3️⃣  [green]Examen completo[/green] (Todas las preguntas sin retroalimentación inmediata) {'[bright_black][último usado][/bright_black]' if ultimo_modo == '3' else ''}\n"
        f"4️⃣  [green]Examen completo (random)[/green] (Preguntas aleatorias sin retroalimentación inmediata) {'[bright_black][último usado][/bright_black]' if ultimo_modo == '4' else ''}\n"
        "5️⃣  [magenta]Modo práctica limitada[/magenta] (Seleccionar número de preguntas aleatorias)\n\n"
        "[bold]Presiona 1, 2, 3, 4 o 5 para elegir.[/bold]"
    )
    
    menu = Panel.fit(menu_texto, title="📖 Menú de Examen", border_style="blue")
    console.print(menu)

    while True:
        key = esperar_tecla()
        if key in ['1', '2', '3', '4', '5']:
            guardar_configuracion(ultimo_modo=key)
            return key
        time.sleep(0.1)  # Reducir uso de CPU

def modo_examen(preguntas):
    """Modo sin feedback inmediato, pero ahora mostrando si es correcto o incorrecto en cada pregunta."""
    respuestas_usuario = []
    aciertos = 0

    for i, pregunta in enumerate(track(preguntas, description="📝 Respondiendo preguntas..."), start=1):
        mostrar_pregunta(pregunta, i, len(preguntas))
        respuesta = esperar_respuesta_tecla()
        
        mostrar_feedback(pregunta, respuesta)  # 🔥 Ahora también muestra feedback en examen completo

        respuestas_usuario.append((pregunta, respuesta))
        if respuesta == pregunta.correcta:
            aciertos += 1

    mostrar_resultado(respuestas_usuario, aciertos, len(preguntas))

def modo_paso_a_paso(preguntas):
    """Modo con feedback inmediato."""
    aciertos = 0
    for i, pregunta in enumerate(track(preguntas, description="📝 Resolviendo preguntas..."), start=1):
        mostrar_pregunta(pregunta, i, len(preguntas))
        respuesta = esperar_respuesta_tecla()
        mostrar_feedback(pregunta, respuesta)
        if respuesta == pregunta.correcta:
            aciertos += 1
        console.print("\n[cyan]Presiona Enter para continuar...[/cyan]")
        input()
    
    console.print(f"\n🎯 [bold yellow]Resumen:[/bold yellow] {aciertos}/{len(preguntas)} correctas.")

def modo_practica_limitada(preguntas):
    """Modo que permite seleccionar un número limitado de preguntas aleatorias."""
    if not preguntas:
        console.print("[bold red]No hay preguntas disponibles.[/bold red]")
        return
    
    max_preguntas = len(preguntas)
    console.print(f"[bold cyan]Número total de preguntas disponibles: {max_preguntas}[/bold cyan]")
    
    try:
        num = Prompt.ask("Ingrese el número de preguntas a practicar", default=str(min(10, max_preguntas)))
        num_preguntas = int(num)
        
        if num_preguntas <= 0:
            console.print("[yellow]⚠️ El número debe ser positivo. Usando 1.[/yellow]")
            num_preguntas = 1
        elif num_preguntas > max_preguntas:
            console.print(f"[yellow]⚠️ El número excede el total disponible. Usando {max_preguntas}.[/yellow]")
            num_preguntas = max_preguntas
            
        preguntas_seleccionadas = random.sample(preguntas, num_preguntas)
        modo_paso_a_paso(preguntas_seleccionadas)
        
    except ValueError:
        console.print("[bold red]❌ Entrada inválida. Debe ser un número entero.[/bold red]")
        input("[cyan]Presiona Enter para volver al menú principal...[/cyan]")

def mostrar_pregunta(pregunta, indice, total):
    """Muestra la pregunta con opciones bien formateadas."""
    os.system('cls' if os.name == 'nt' else 'clear')
    panel = Panel.fit(f"[bold yellow]Pregunta {indice}/{total} (#{pregunta.numero})[/bold yellow]\n\n{pregunta.enunciado}", title="📌 Pregunta", border_style="magenta")
    console.print(panel)
    
    for idx, opcion in enumerate(pregunta.opciones, start=65):
        console.print(f"[bold cyan]{chr(idx)}.[/bold cyan] {opcion}")

def esperar_respuesta_tecla():
    """Espera la presión de una tecla entre A y D para registrar la respuesta."""
    console.print("[bold blue]Presiona una tecla (A/B/C/D):[/bold blue]")
    
    while True:
        key = esperar_tecla()
        if key in ['a', 'b', 'c', 'd']:
            return key.upper()
        time.sleep(0.05)  # Reducir uso de CPU

def mostrar_feedback(pregunta, respuesta):
    """Muestra si la respuesta fue correcta o incorrecta y cuál era la correcta."""
    os.system('cls' if os.name == 'nt' else 'clear')

    if respuesta == pregunta.correcta:
        console.print("\n[bold green]✅ Correcto![/bold green]")
    else:
        console.print(f"\n[bold red]❌ Incorrecto.[/bold red]")

    console.print(f"\n[bold cyan]Tu respuesta:[/bold cyan] [yellow]{respuesta}[/yellow] → {pregunta.opciones[ord(respuesta) - 65]}")
    console.print(f"[bold green]✔ Respuesta correcta:[/bold green] [bold]{pregunta.correcta}[/bold] → {pregunta.opciones[ord(pregunta.correcta) - 65]}")

def mostrar_resultado(respuestas, aciertos, total):
    """Muestra un resultado detallado del examen."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    puntuacion = (aciertos / total) * 100
    console.print("\n[bold]📊 Resultados del examen[/bold]")
    
    # Mostrar puntuación con color según rendimiento
    if puntuacion >= 80:
        console.print(f"[bold green]Puntuación: {puntuacion:.1f}% ({aciertos}/{total})[/bold green]")
    elif puntuacion >= 60:
        console.print(f"[bold yellow]Puntuación: {puntuacion:.1f}% ({aciertos}/{total})[/bold yellow]")
    else:
        console.print(f"[bold red]Puntuación: {puntuacion:.1f}% ({aciertos}/{total})[/bold red]")
    
    # Preguntar si desea ver el detalle de respuestas
    ver_detalle = Prompt.ask("\n¿Desea ver el detalle de las respuestas?", choices=["s", "n"], default="s")
    
    if ver_detalle.lower() == "s":
        console.print("\n[bold underline]Detalle de respuestas:[/bold underline]")
        for i, (pregunta, respuesta) in enumerate(respuestas, 1):
            correcta = respuesta == pregunta.correcta
            estilo = "[green]Correcta[/green]" if correcta else "[red]Incorrecta[/red]"
            console.print(f"\n{i}. Pregunta #{pregunta.numero}: {estilo}")
            console.print(f"   Su respuesta: [bold]{respuesta}[/bold] - {pregunta.opciones[ord(respuesta) - 65]}")
            if not correcta:
                console.print(f"   Respuesta correcta: [bold green]{pregunta.correcta}[/bold green] - {pregunta.opciones[ord(pregunta.correcta) - 65]}")
    
    # Opción para exportar resultados
    exportar = Prompt.ask("\n¿Desea exportar los resultados a un archivo?", choices=["s", "n"], default="n")
    if exportar.lower() == "s":
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Resultados del examen - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Puntuación: {puntuacion:.1f}% ({aciertos}/{total})\n\n")
                f.write("Detalle de respuestas:\n")
                
                for i, (pregunta, respuesta) in enumerate(respuestas, 1):
                    correcta = respuesta == pregunta.correcta
                    estado = "Correcta" if correcta else "Incorrecta"
                    f.write(f"\n{i}. Pregunta #{pregunta.numero}: {estado}\n")
                    f.write(f"   Enunciado: {pregunta.enunciado}\n")
                    f.write(f"   Su respuesta: {respuesta} - {pregunta.opciones[ord(respuesta) - 65]}\n")
                    if not correcta:
                        f.write(f"   Respuesta correcta: {pregunta.correcta} - {pregunta.opciones[ord(pregunta.correcta) - 65]}\n")
            
            console.print(f"[bold green]✅ Resultados exportados exitosamente a: {filename}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Error al exportar resultados: {e}[/bold red]")
    
    input("\n[cyan]Presiona Enter para continuar...[/cyan]")

def mostrar_informacion():
    """Muestra información sobre el programa."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    info_texto = (
        "[bold cyan]Programa de Examen - Información[/bold cyan]\n\n"
        "Este programa permite practicar preguntas de opción múltiple en diferentes modos:\n"
        "• [yellow]Paso a paso[/yellow]: Revise cada pregunta con retroalimentación inmediata\n"
        "• [green]Examen completo[/green]: Simule un examen real respondiendo todas las preguntas\n"
        "• [magenta]Práctica limitada[/magenta]: Seleccione un número específico de preguntas para practicar\n\n"
        "[bold]Formato del archivo de preguntas:[/bold]\n"
        "El archivo debe seguir este formato específico:\n"
        "- Número de pregunta seguido de dos puntos (ej. '1:')\n"
        "- Enunciado de la pregunta\n"
        "- Opciones A, B, C y D precedidas por la letra y un punto\n"
        "- Respuesta correcta indicada como 'Correct Answer: X'\n\n"
        "[bold]Atajos de teclado:[/bold]\n"
        "- Use las teclas [A], [B], [C], [D] para responder\n"
        "- Presione [Enter] para continuar entre preguntas\n\n"
        "Desarrollado por [italic]Jorge Torlaschi[/italic] - Versión 2.0"
    )
    
    panel = Panel.fit(info_texto, title="ℹ️ Información del Programa", border_style="cyan")
    console.print(panel)
    
    input("\n[cyan]Presiona Enter para volver al menú principal...[/cyan]")

def linea_comandos():
    """Configura los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Programa de preguntas de examen')
    parser.add_argument('-f', '--file', help='Ruta al archivo de preguntas')
    parser.add_argument('-m', '--mode', choices=['1', '2', '3', '4', '5'], 
                        help='Modo de examen (1-5)')
    parser.add_argument('-n', '--num', type=int, 
                        help='Número de preguntas para modo práctica limitada')
    return parser.parse_args()

def main():
    args = linea_comandos()
    
    # Mostrar pantalla de bienvenida
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print("[bold cyan]¡Bienvenido al Programa de Examen![/bold cyan]", justify="center")
    console.print("[yellow]Presione cualquier tecla para continuar...[/yellow]", justify="center")
    esperar_tecla()
    
    # Selección y carga de archivo
    if args.file:
        ruta_archivo = args.file
        guardar_configuracion(ultima_ruta=ruta_archivo)
    else:
        # Primer paso: selección de archivo (con mejor manejo de UI)
        os.system('cls' if os.name == 'nt' else 'clear')
        config = cargar_configuracion()
        ultima_ruta = config.get('ultima_ruta', DEFAULT_RUTA_ARCHIVO)
        
        console.print("[bold cyan]Opciones para archivo de preguntas:[/bold cyan]")
        console.print(f"1. Usar archivo por defecto o último usado: [yellow]{ultima_ruta}[/yellow]")
        console.print("2. Seleccionar archivo desde cuadro de diálogo")
        console.print("3. Ingresar ruta manualmente")
        console.print("\n[yellow]Presione 1, 2 o 3 para continuar...[/yellow]")
        
        # Esperar a que se presione una tecla válida
        while True:
            key = esperar_tecla()
            if key == '1':
                ruta_archivo = ultima_ruta
                break
            elif key == '2':
                # Usar el cuadro de diálogo para seleccionar archivo
                ruta_archivo = seleccionar_archivo_dialogo()
                
                # Mostrar confirmación
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print(f"[bold green]Archivo seleccionado: {ruta_archivo}[/bold green]")
                console.print("[yellow]Presione Enter para continuar...[/yellow]")
                input()
                break
            elif key == '3':
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print("[bold cyan]Selección de archivo[/bold cyan]")
                ruta_archivo = Prompt.ask("Ingrese la ruta del archivo de preguntas", default=ultima_ruta)
                guardar_configuracion(ultima_ruta=ruta_archivo)
                
                # Mostrar confirmación
                console.print(f"[bold green]Archivo seleccionado: {ruta_archivo}[/bold green]")
                console.print("[yellow]Presione Enter para continuar...[/yellow]")
                input()
                break
    
    # Cargar preguntas del archivo seleccionado
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(f"[bold cyan]Cargando preguntas de: {ruta_archivo}[/bold cyan]")
    preguntas = cargar_preguntas(ruta_archivo)
    
    if not preguntas:
        console.print("[bold red]No se encontraron preguntas válidas.[/bold red]")
        console.print("[yellow]Presione Enter para salir...[/yellow]")
        input()
        return
        
    console.print(f"[bold green]✅ Se cargaron correctamente {len(preguntas)} preguntas.[/bold green]")
    console.print("[yellow]Presione Enter para continuar...[/yellow]")
    input()  # Esperar entrada del usuario
    
    # Selección de modo de examen
    modo = args.mode if args.mode else mostrar_menu()
    
    if modo in ['2', '4', '5']:  # Random
        preguntas = random.sample(preguntas, len(preguntas))

    if modo in ['1', '2']:
        modo_paso_a_paso(preguntas)
    elif modo == '5':
        if args.num:
            num_preguntas = min(args.num, len(preguntas))
            modo_paso_a_paso(preguntas[:num_preguntas])
        else:
            modo_practica_limitada(preguntas)
    else:
        modo_examen(preguntas)
    
    # Preguntar si desea volver al menú principal
    volver = Prompt.ask("\n¿Desea volver al menú principal?", choices=["s", "n"], default="s")
    if volver.lower() == "s":
        main()  # Reiniciar el programa

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Programa interrumpido por el usuario.[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error inesperado: {str(e)}[/bold red]")
    finally:
        console.print("\n[bold cyan]¡Gracias por usar el Programa de Examen![/bold cyan]")
