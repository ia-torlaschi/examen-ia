import argparse
import tkinter as tk
from tkinter import filedialog
import os
import sys
from rich.console import Console
from rich.prompt import Prompt # <--- IMPORTACIÓN AÑADIDA AQUÍ

# Asegurarse de que los directorios core y ui estén en el path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'core'))
sys.path.insert(0, os.path.join(project_root, 'ui'))

# Ahora importar módulos locales
from core import parser, examen_runner, diagnostico, config as app_config
from ui import gui

console = Console()

def seleccionar_archivo_dialogo(initial_dir):
    """Muestra un cuadro de diálogo para seleccionar un archivo."""
    root = tk.Tk()
    root.withdraw()
    archivo = filedialog.askopenfilename(
        title="Seleccione archivo de preguntas",
        initialdir=initial_dir,
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    root.destroy()
    return archivo

def main():
    parser_args = argparse.ArgumentParser(description="Sistema de Examen v3.0")
    parser_args.add_argument('--interfaz', choices=['gui', 'cli'], help='Forzar modo GUI o CLI')
    parser_args.add_argument('--archivo', type=str, help='Ruta al archivo de preguntas')
    parser_args.add_argument('--modo-cli', choices=['1', '2', '3', '4', '5', '6'],
                             help='Modo específico para CLI (1-5 Examen, 6 Diagnóstico)')
    # Añadir otros argumentos si se desea (ej. --num-preguntas para modo 5)

    args = parser_args.parse_args()

    # --- Cargar Configuración ---
    # Nota: Cargar config aquí para obtener ultima_ruta para el diálogo
    config = app_config.cargar_configuracion()
    ultima_ruta = config.get('ultima_ruta', app_config.DEFAULT_RUTA_ARCHIVO)
    modo_interfaz_preferido = args.interfaz or config.get('ultimo_modo_interfaz', 'gui')


    # --- Seleccionar Archivo ---
    ruta_archivo = args.archivo # Prioridad: argumento de línea de comandos
    config_a_guardar = {} # Diccionario para guardar cambios de config

    if not ruta_archivo: # Si no se dio argumento
        # Usar config ya cargada para directorio inicial y default
        directorio_inicial = os.path.dirname(os.path.abspath(ultima_ruta))

        # Preguntar al usuario qué hacer
        console.print("[bold cyan]Selección de Archivo de Preguntas:[/bold cyan]")
        console.print(f"1. Usar último archivo: [yellow]{ultima_ruta}[/yellow]")
        console.print(f"2. Seleccionar nuevo archivo...")
        # Usar Prompt ahora que está importado
        opcion_archivo = Prompt.ask("Opción", choices=["1", "2"], default="1")


        if opcion_archivo == '1':
            ruta_archivo = ultima_ruta
        else:
            ruta_archivo = seleccionar_archivo_dialogo(directorio_inicial)

    # Validar que el archivo seleccionado existe AHORA
    if not ruta_archivo or not os.path.exists(ruta_archivo):
         console.print(f"[bold red]❌ Archivo no válido o no seleccionado: '{ruta_archivo}'. Saliendo.[/bold red]")
         return

    console.print(f"[cyan]Usando archivo: {ruta_archivo}[/cyan]")
    config_a_guardar['ultima_ruta'] = ruta_archivo # Guardar la ruta que se usará


    # --- Cargar Preguntas ---
    # Se hace aquí DESPUÉS de seleccionar el archivo
    console.print(f"[cyan]Cargando preguntas desde: {ruta_archivo}[/cyan]")
    preguntas = parser.cargar_preguntas(ruta_archivo)

    if not preguntas:
        console.print("[bold red]❌ No se pudieron cargar preguntas válidas del archivo.[/bold red]")
        console.print("[yellow]Considere usar el modo Diagnóstico (CLI opción 6).[/yellow]")
        # Permitir continuar SOLO si se elige CLI explícitamente para diagnóstico
        if not (args.interfaz == 'cli' or args.modo_cli == '6'):
             input("Presione Enter para salir...")
             return
        # Si es CLI y podría ser diagnóstico, pasamos lista vacía
    else:
         console.print(f"[green]✅ {len(preguntas)} preguntas cargadas correctamente.[/green]")
         preguntas_multiples = sum(1 for p in preguntas if p.es_multiple)
         console.print(f"   [cyan]Selección única: {len(preguntas) - preguntas_multiples}[/cyan]")
         console.print(f"   [cyan]Selección múltiple: {preguntas_multiples}[/cyan]")
         input("Presione Enter para continuar...")


    # --- Seleccionar Interfaz ---
    modo_interfaz = modo_interfaz_preferido
    if not args.interfaz: # Si no se forzó por argumento
        # Preguntar solo si no se pasó argumento --modo-cli (que implica CLI)
        if not args.modo_cli:
             try:
                # Usar Prompt aquí también si se desea consistencia, o mantener input
                eleccion = console.input(f"Seleccione interfaz ([bold]G[/bold]UI / [bold]C[/bold]LI) [Predeterminado: {modo_interfaz.upper()}]: ").lower().strip()
                if eleccion == 'c' or eleccion == 'cli':
                    modo_interfaz = 'cli'
                elif eleccion == 'g' or eleccion == 'gui':
                     modo_interfaz = 'gui'
                # Si es vacío, usa el predeterminado/guardado
             except EOFError:
                 console.print(f"Usando interfaz predeterminada: {modo_interfaz.upper()}")

    config_a_guardar['ultimo_modo_interfaz'] = modo_interfaz
    app_config.guardar_configuracion(config_a_guardar) # Guardar config aquí


    # --- Ejecutar ---
    if modo_interfaz == 'cli':
        # Pasar preguntas incluso si está vacío para permitir diagnóstico
        examen_runner.iniciar_cli(preguntas if preguntas else [], ruta_archivo, args.modo_cli)
    else:
        # Solo iniciar GUI si hay preguntas
        if not preguntas:
             console.print("[bold red]No hay preguntas cargadas. No se puede iniciar la GUI.[/bold red]")
             console.print("[yellow]Use la interfaz CLI (opción 6) para diagnosticar el archivo.[/yellow]")
             return
        gui.iniciar_gui(ruta_archivo, preguntas) # Pasar preguntas ya cargadas

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Programa interrumpido por el usuario.[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error inesperado en main: {str(e)}[/bold red]")
        # Mostrar traceback detallado
        console.print_exception(show_locals=True)
    finally:
        console.print("\n[bold cyan]Examen Aplicación Finalizado.[/bold cyan]")