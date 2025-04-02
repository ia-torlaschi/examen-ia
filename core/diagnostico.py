# core/diagnostico.py
import re
from rich.console import Console
from rich.panel import Panel
import os

console = Console()

def diagnosticar_archivo(ruta_archivo):
    """
    Analiza en detalle el archivo de preguntas para detectar problemas.
    """
    console.print(Panel(f"[bold cyan]Diagnóstico General del Archivo: {ruta_archivo}[/bold cyan]", expand=False))

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        console.print(f"[bold red]❌ Error al leer archivo: {str(e)}[/bold red]")
        return

    # Normalizar y añadir saltos para regex
    contenido = '\n' + contenido.replace('\r\n', '\n').replace('\r', '\n') + '\n'
    lineas = contenido.splitlines() # Usar splitlines para contar bien

    # --- Estadísticas Básicas ---
    num_lineas = len(lineas) - 2 # Restar los saltos añadidos
    num_lineas_no_vacias = sum(1 for l in lineas[1:-1] if l.strip())
    console.print(f"[cyan]Líneas totales (aprox): {num_lineas}[/cyan]")
    console.print(f"[cyan]Líneas no vacías: {num_lineas_no_vacias}[/cyan]")

    # --- Búsqueda de Patrones ---
    # Preguntas: salto de línea, dígitos, dos puntos, espacio opcional, salto de línea
    patron_pregunta_regex = re.compile(r'\n(\d+):[ \t]*\n')
    # Respuestas: inicio línea (o después de espacio), "Correct Answer:", espacio*, Letra, (punto o espacio o fin línea)
    patron_respuesta_regex = re.compile(r'^\s*Correct Answer:\s*([A-Z])(?:[.\s]|$)', re.IGNORECASE | re.MULTILINE)
    # Opciones: inicio línea (o después de espacio), Letra, punto, espacio*
    patron_opcion_regex = re.compile(r'^\s*([A-Z])\.\s*(.*)', re.MULTILINE)

    inicios_pregunta_match = list(patron_pregunta_regex.finditer(contenido))
    respuestas_match = list(patron_respuesta_regex.finditer(contenido))
    opciones_match = list(patron_opcion_regex.finditer(contenido))

    num_preguntas_detectadas = len(inicios_pregunta_match)
    num_respuestas_detectadas = len(respuestas_match) # Líneas que *parecen* ser una respuesta

    console.print(f"[cyan]Inicios de pregunta ('N:'): {num_preguntas_detectadas}[/cyan]")
    console.print(f"[cyan]Líneas 'Correct Answer: X': {num_respuestas_detectadas}[/cyan]")
    console.print(f"[cyan]Líneas de opción ('X.'): {len(opciones_match)}[/cyan]")

    # --- Verificación de Consistencia ---
    problemas = []
    if num_preguntas_detectadas == 0:
         problemas.append("[red]No se detectó ninguna pregunta con el formato 'N:'.[/red]")
    elif num_respuestas_detectadas == 0:
         problemas.append("[red]No se detectó ninguna línea 'Correct Answer:'.[/red]")
    # Esta comparación es menos fiable porque respuestas múltiples usan varias líneas
    # elif num_preguntas_detectadas != num_respuestas_detectadas:
    #      problemas.append(f"[yellow]Advertencia: Número de preguntas ({num_preguntas_detectadas}) no coincide con número de líneas 'Correct Answer' ({num_respuestas_detectadas}). Puede ser normal por respuestas múltiples.[/yellow]")

    # --- Análisis por Bloque (si se detectaron preguntas) ---
    if num_preguntas_detectadas > 0:
        console.print("\n[cyan]Análisis por bloque de pregunta:[/cyan]")
        preguntas_ok = 0
        preguntas_con_warning = 0
        preguntas_con_error = 0

        # Usamos el parser para un análisis más profundo
        # Necesitamos importar Pregunta del parser
        try:
            from .parser import cargar_preguntas, Pregunta
        except ImportError:
            from parser import cargar_preguntas, Pregunta

        # Ejecutamos el parser en modo "silencioso" para diagnóstico
        console_original = parser.console # Guardar consola original
        parser.console = Console(quiet=True) # Suprimir output del parser
        preguntas_parseadas = cargar_preguntas(ruta_archivo)
        parser.console = console_original # Restaurar

        num_parseadas_ok = len(preguntas_parseadas)
        console.print(f"  - El parser logró cargar [bold {'green' if num_parseadas_ok == num_preguntas_detectadas else 'yellow'}] {num_parseadas_ok} / {num_preguntas_detectadas} [/] preguntas detectadas.")

        # Revisar logs del parser si existe
        log_parser = 'log_parser.txt'
        if os.path.exists(log_parser):
             with open(log_parser, 'r', encoding='utf-8') as log_f:
                  log_content = log_f.read()
                  if "*** ERROR" in log_content:
                       preguntas_con_error = log_content.count("*** ERROR")
                       problemas.append(f"[red]Se encontraron {preguntas_con_error} errores graves durante el parseo (ver {log_parser}).[/red]")
        else:
             console.print(f"  - No se encontró el archivo de log '{log_parser}'.")


        if num_parseadas_ok < num_preguntas_detectadas:
             problemas.append("[yellow]Algunas preguntas detectadas por número ('N:') no pudieron ser procesadas completamente por el parser.[/yellow]")


    # --- Mostrar Problemas ---
    if problemas:
        console.print("\n[bold yellow]Problemas / Advertencias Detectadas:[/bold yellow]")
        for prob in problemas:
            console.print(f"- {prob}")
    else:
        console.print("\n[bold green]✅ Diagnóstico básico no encontró problemas obvios de formato.[/bold green]")

    console.print(f"\n[grey50]Para un análisis más detallado, revise el archivo [bold]{log_parser}[/bold] si fue generado.[/grey50]")


def analizar_preguntas_faltantes(ruta_archivo, rango_max=63): # Asumir 63 por defecto basado en script anterior
    """Detecta huecos y duplicados en la numeración de preguntas."""
    console.print(Panel(f"[bold cyan]Análisis de Numeración en: {ruta_archivo}[/bold cyan]", expand=False))

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        contenido = '\n' + contenido.replace('\r\n', '\n').replace('\r', '\n') + '\n'
    except Exception as e:
        console.print(f"[bold red]❌ Error al leer archivo: {str(e)}[/bold red]")
        return

    # Buscar todos los números de pregunta ('N:')
    patron_pregunta_regex = re.compile(r'\n(\d+):[ \t]*\n')
    numeros_detectados_str = patron_pregunta_regex.findall(contenido)

    if not numeros_detectados_str:
        console.print("[red]No se detectó ninguna pregunta con el formato 'N:'. Imposible analizar numeración.[/red]")
        return

    try:
        numeros_detectados = sorted([int(n) for n in numeros_detectados_str])
        num_total_detectados = len(numeros_detectados)
        console.print(f"[cyan]Números de pregunta detectados: {num_total_detectados}[/cyan]")
        if num_total_detectados > 0:
             console.print(f"  - Rango detectado: {numeros_detectados[0]} a {numeros_detectados[-1]}")
    except ValueError:
        console.print("[red]Error: Algunos números de pregunta detectados no son enteros válidos.[/red]")
        console.print(f"  - Detectados: {numeros_detectados_str}")
        return

    # --- Verificar Duplicados ---
    numeros_unicos = set(numeros_detectados)
    if len(numeros_unicos) < num_total_detectados:
        duplicados = sorted([n for n in numeros_unicos if numeros_detectados.count(n) > 1])
        console.print(f"[bold red]❌ ¡Preguntas Duplicadas Detectadas!: {', '.join(map(str, duplicados))}[/bold red]")
    else:
        console.print("[green]✅ No se encontraron números de pregunta duplicados.[/green]")

    # --- Verificar Faltantes ---
    rango_esperado = set(range(1, rango_max + 1))
    faltantes = sorted(list(rango_esperado - numeros_unicos))

    if faltantes:
        console.print(f"[bold yellow]⚠️ Preguntas Faltantes (esperando hasta {rango_max}): {', '.join(map(str, faltantes))}[/bold yellow]")
    else:
        # Verificar si el máximo detectado coincide con el esperado
        if numeros_detectados and numeros_detectados[-1] == rango_max:
             console.print(f"[green]✅ No faltan preguntas en el rango esperado (1-{rango_max}).[/green]")
        else:
             console.print(f"[yellow]⚠️ No faltan preguntas en el rango detectado, pero el máximo ({numeros_detectados[-1] if numeros_detectados else 'N/A'}) no coincide con el esperado ({rango_max}).[/yellow]")

    console.print("\n[grey50]Nota: El rango esperado se asume hasta 63. Modificar si es necesario.[/grey50]")

# Se podrían añadir aquí las funciones 'extraer_preguntas_problematicas' y
# 'corregir_formato_preguntas' del script CLI anterior si se desea esa funcionalidad.