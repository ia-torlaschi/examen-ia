# core/examen_runner.py
import random
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm # Confirm para sí/no
from rich.progress import track

# Requerido para que funcione desde main.py
try:
    # Intenta importar como si core fuera un paquete
    from . import parser, exportador, diagnostico, config as app_config
except ImportError:
    # Si falla (ej. ejecutado directamente), importa normalmente
    import parser
    import exportador
    import diagnostico
    import config as app_config


console = Console()

# --- Lógica Común ---
def es_respuesta_correcta(pregunta: parser.Pregunta, respuesta_usuario):
    """
    Valida si la respuesta proporcionada por el usuario es correcta.
    'respuesta_usuario' debe ser una lista de strings (letras).
    """
    if not isinstance(respuesta_usuario, list):
        # Convertir a lista si es un solo string (para consistencia)
        respuesta_usuario = [respuesta_usuario] if isinstance(respuesta_usuario, str) else []

    # Comparar conjuntos para ignorar orden y duplicados
    respuesta_set = set(r.upper() for r in respuesta_usuario if r) # Limpiar y asegurar mayúsculas
    correctas_set = set(pregunta.correctas) # Ya están en mayúsculas y validadas por el parser

    # Debug detallado (opcional, comentar para producción)
    # console.print(f"[grey50]Debug Check: Usuario={respuesta_set} vs Correctas={correctas_set}[/grey50]")

    return respuesta_set == correctas_set

# --- Lógica Específica de CLI ---

def mostrar_pregunta_cli(pregunta: parser.Pregunta, indice, total):
    """Muestra la pregunta formateada para la CLI usando Rich."""
    os.system('cls' if os.name == 'nt' else 'clear')

    tipo_pregunta = ""
    if pregunta.es_multiple:
        tipo_pregunta = f" [cyan](Selección Múltiple - {len(pregunta.correctas)} opciones)[/cyan]"

    titulo_panel = f"[bold yellow]Pregunta {indice}/{total} (#{pregunta.numero}){tipo_pregunta}[/bold yellow]"
    panel_pregunta = Panel.fit(f"[white]{pregunta.enunciado}[/white]", title=titulo_panel, border_style="magenta", padding=(1, 2))
    console.print(panel_pregunta)

    opciones_texto = []
    for idx, opcion_texto in enumerate(pregunta.opciones):
        letra = chr(65 + idx)
        opciones_texto.append(f"[bold cyan]{letra}.[/bold cyan] {opcion_texto}")

    panel_opciones = Panel("\n".join(opciones_texto), title="Opciones", border_style="blue", padding=(1,1))
    console.print(panel_opciones)

def esperar_respuesta_cli(pregunta: parser.Pregunta) -> list[str]:
    """Espera y valida la respuesta del usuario en modo CLI."""
    num_correctas = len(pregunta.correctas)
    letras_validas = [chr(65 + i) for i in range(len(pregunta.opciones))]
    prompt_texto = f"Respuesta ({'/'.join(letras_validas)}):"
    if pregunta.es_multiple:
        prompt_texto = f"Selecciona {num_correctas} ({'/'.join(letras_validas)}, ej: AC):"

    while True:
        try:
            respuesta_raw = Prompt.ask(f"[bold green]{prompt_texto}[/bold green]").upper().replace(" ", "").replace(",", "")
            respuestas_seleccionadas = sorted(list(set(respuesta_raw))) # Ordenar y quitar duplicados

            # Validar caracteres
            validos = True
            for letra in respuestas_seleccionadas:
                if letra not in letras_validas:
                    console.print(f"[red]Error: La opción '{letra}' no es válida.[/red]")
                    validos = False
                    break
            if not validos:
                continue

            # Validar cantidad si es múltiple
            if pregunta.es_multiple and len(respuestas_seleccionadas) != num_correctas:
                 console.print(f"[red]Error: Debes seleccionar exactamente {num_correctas} opciones.[/red]")
                 continue

            # Si es respuesta única y se ingresaron varias
            if not pregunta.es_multiple and len(respuestas_seleccionadas) > 1:
                 console.print(f"[red]Error: Solo puedes seleccionar una opción.[/red]")
                 continue

            # Si pasa todas las validaciones
            return respuestas_seleccionadas # Devolver siempre como lista

        except KeyboardInterrupt:
             console.print("[yellow]\nInterrupción detectada. Volviendo al menú...[/yellow]")
             return ["INTERRUPT"] # Señal para salir del modo
        except Exception as e:
             console.print(f"[red]Error inesperado al leer respuesta: {e}[/red]")
             # Podríamos decidir qué hacer aquí, por ahora reintentamos


def mostrar_feedback_cli(pregunta: parser.Pregunta, respuesta_usuario: list[str]):
    """Muestra el feedback detallado en la CLI."""
    es_correcta = es_respuesta_correcta(pregunta, respuesta_usuario)

    console.print("\n" + "="*30 + " FEEDBACK " + "="*30)
    if es_correcta:
        console.print("[bold green]✅ ¡Correcto![/bold green]")
    else:
        console.print("[bold red]❌ Incorrecto.[/bold red]")

    # Mostrar respuesta del usuario
    resp_usuario_str = ", ".join(sorted(respuesta_usuario))
    console.print(f"[bold cyan]Tu respuesta:[/bold cyan] {resp_usuario_str if resp_usuario_str else '(ninguna)'}")
    for letra in sorted(respuesta_usuario):
         if letra and (idx := ord(letra) - 65) < len(pregunta.opciones):
             console.print(f"  [yellow]{letra}[/yellow] → {pregunta.opciones[idx]}")


    # Mostrar la(s) correcta(s) si fue incorrecta o siempre (opcional)
    if not es_correcta:
        resp_correcta_str = ", ".join(sorted(pregunta.correctas))
        console.print(f"[bold green]✔ Respuesta(s) correcta(s):[/bold green] {resp_correcta_str}")
        for letra in sorted(pregunta.correctas):
             if letra and (idx := ord(letra) - 65) < len(pregunta.opciones):
                console.print(f"  [green]{letra}[/green] → {pregunta.opciones[idx]}")
    console.print("="*70 + "\n")


def mostrar_resultado_cli(resultados: list[tuple], total_preguntas: int, ruta_archivo: str):
    """Muestra el resultado final y ofrece exportación en CLI."""
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel("[bold]📊 Resultados Finales 📊[/bold]", style="bold blue", expand=False))

    aciertos = sum(1 for _, correcta, _ in resultados if correcta)
    puntuacion = (aciertos / total_preguntas) * 100 if total_preguntas > 0 else 0

    estilo_puntuacion = "green" if puntuacion >= 80 else ("yellow" if puntuacion >= 60 else "red")
    console.print(f"\n[bold {estilo_puntuacion}]Puntuación Final: {puntuacion:.2f}% ({aciertos} de {total_preguntas})[/bold {estilo_puntuacion}]\n")

    # Ver detalle
    if Confirm.ask("¿Desea ver el detalle de las respuestas?", default=False):
        console.print("\n[bold underline]Detalle de Respuestas:[/bold underline]")
        for i, (pregunta, correcta, respuesta_usuario) in enumerate(resultados, 1):
            estilo = "[green]Correcta[/green]" if correcta else "[red]Incorrecta[/red]"
            resp_usr_str = ", ".join(sorted(respuesta_usuario)) if respuesta_usuario else "(ninguna)"
            resp_corr_str = ", ".join(sorted(pregunta.correctas))

            console.print(f"\n{i}. [bold]Pregunta #{pregunta.numero}:[/bold] {estilo}")
            console.print(f"   [cyan]Tu Respuesta:[/cyan] {resp_usr_str}")
            if not correcta:
                console.print(f"   [green]Respuesta Correcta:[/green] {resp_corr_str}")
                # Opcional: Mostrar el texto de las opciones correctas
                # for letra in sorted(pregunta.correctas):
                #      if (idx := ord(letra) - 65) < len(pregunta.opciones):
                #           console.print(f"      [green]{letra}.[/green] {pregunta.opciones[idx]}")

    # Exportar Resultados
    if Confirm.ask("\n¿Desea exportar los resultados detallados?", default=False):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Usar nombre base del archivo de preguntas para el resultado
        base_name = os.path.splitext(os.path.basename(ruta_archivo))[0]
        default_filename_txt = f"resultados_{base_name}_{timestamp}.txt"
        default_filename_pdf = f"resultados_{base_name}_{timestamp}.pdf"

        formato = Prompt.ask("Formato de exportación", choices=["txt", "pdf", "ambos"], default="txt")

        try:
            # Adaptar resultados al formato esperado por exportador si es necesario
            # El exportador espera lista de tuplas: (pregunta_obj, respuesta_usuario_lista)
            resultados_export = [(p, resp) for p, _, resp in resultados]

            if formato in ["txt", "ambos"]:
                exportador.exportar_txt(resultados_export, aciertos, total_preguntas, default_filename_txt)
                console.print(f"[green]✅ Resultados exportados a {default_filename_txt}[/green]")
            if formato in ["pdf", "ambos"]:
                exportador.exportar_pdf(resultados_export, aciertos, total_preguntas, default_filename_pdf)
                console.print(f"[green]✅ Resultados exportados a {default_filename_pdf}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error al exportar resultados: {e}[/red]")


def modo_paso_a_paso_cli(preguntas: list, ruta_archivo: str):
    """Modo CLI con feedback inmediato."""
    if not preguntas:
         console.print("[red]No hay preguntas cargadas para este modo.[/red]")
         return

    aciertos = 0
    resultados_finales = [] # Para resumen aunque no se use mucho aquí

    for i, pregunta in enumerate(track(preguntas, description="📝 Resolviendo paso a paso..."), start=1):
        mostrar_pregunta_cli(pregunta, i, len(preguntas))
        respuesta_usuario = esperar_respuesta_cli(pregunta)

        if respuesta_usuario == ["INTERRUPT"]: break # Salir si se interrumpió

        es_correcta = es_respuesta_correcta(pregunta, respuesta_usuario)
        if es_correcta:
            aciertos += 1

        mostrar_feedback_cli(pregunta, respuesta_usuario)
        resultados_finales.append((pregunta, es_correcta, respuesta_usuario))

        # Pausa antes de la siguiente
        if i < len(preguntas):
             try:
                  input("Presione Enter para continuar...")
             except KeyboardInterrupt:
                  console.print("[yellow]\nInterrupción detectada. Finalizando modo...[/yellow]")
                  break


    console.print("\n[bold blue]--- Fin del Modo Paso a Paso ---[/bold blue]")
    if resultados_finales:
        mostrar_resultado_cli(resultados_finales, len(resultados_finales), ruta_archivo)


def modo_examen_cli(preguntas: list, ruta_archivo: str):
    """Modo CLI tipo examen sin feedback inmediato, muestra resultado al final."""
    if not preguntas:
         console.print("[red]No hay preguntas cargadas para este modo.[/red]")
         return

    respuestas_usuario_final = [] # Lista de tuplas: (pregunta_obj, correcta_bool, respuesta_usr_list)

    interrumpido = False
    for i, pregunta in enumerate(track(preguntas, description="📝 Completando examen..."), start=1):
        mostrar_pregunta_cli(pregunta, i, len(preguntas))
        respuesta_usuario = esperar_respuesta_cli(pregunta)

        if respuesta_usuario == ["INTERRUPT"]:
             interrumpido = True
             break

        es_correcta = es_respuesta_correcta(pregunta, respuesta_usuario)
        respuestas_usuario_final.append((pregunta, es_correcta, respuesta_usuario))
        # No mostrar feedback aquí

    console.print("\n[bold blue]--- Fin del Examen ---[/bold blue]")
    if interrumpido:
         console.print("[yellow]El examen fue interrumpido.[/yellow]")

    if respuestas_usuario_final:
         mostrar_resultado_cli(respuestas_usuario_final, len(preguntas), ruta_archivo) # Mostrar resultado sobre el total original


def modo_practica_limitada_cli(preguntas_totales: list, ruta_archivo: str):
    """Modo CLI para practicar N preguntas aleatorias."""
    if not preguntas_totales:
         console.print("[red]No hay preguntas cargadas para este modo.[/red]")
         return

    max_preguntas = len(preguntas_totales)
    default_num = str(min(10, max_preguntas))

    while True:
        try:
            num_str = Prompt.ask(f"Ingrese número de preguntas a practicar (1-{max_preguntas})", default=default_num)
            num_preguntas = int(num_str)
            if 1 <= num_preguntas <= max_preguntas:
                break
            else:
                console.print(f"[red]Por favor, ingrese un número entre 1 y {max_preguntas}.[/red]")
        except ValueError:
            console.print("[red]Entrada inválida. Debe ser un número.[/red]")
        except KeyboardInterrupt:
             console.print("[yellow]\nSelección cancelada.[/yellow]")
             return

    preguntas_seleccionadas = random.sample(preguntas_totales, num_preguntas)
    console.print(f"\n[cyan]Iniciando práctica con {num_preguntas} preguntas aleatorias...[/cyan]")
    # Usamos el modo paso a paso para la práctica
    modo_paso_a_paso_cli(preguntas_seleccionadas, ruta_archivo)


def menu_diagnostico_cli(ruta_archivo: str):
    """Muestra menú de diagnóstico CLI."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(Panel("[bold blue]🔧 Menú de Diagnóstico 🔧[/bold blue]", expand=False))
        console.print(f"[cyan]Archivo actual: {ruta_archivo}[/cyan]\n")
        console.print("1. Diagnóstico General (Formato Básico)")
        console.print("2. Analizar Preguntas Faltantes/Duplicadas")
        # console.print("3. Extraer Preguntas Problemáticas (Avanzado)") # Podría añadirse
        # console.print("4. Corregir Formato (Experimental)") # Podría añadirse
        console.print("5. Volver al Menú Principal")

        opcion = Prompt.ask("Seleccione una opción", choices=["1", "2", "5"], default="1")

        if opcion == "1":
            diagnostico.diagnosticar_archivo(ruta_archivo)
        elif opcion == "2":
            diagnostico.analizar_preguntas_faltantes(ruta_archivo)
        # elif opcion == "3":
        #     diagnostico.extraer_preguntas_problematicas(ruta_archivo)
        # elif opcion == "4":
            # Lógica para corregir formato
        elif opcion == "5":
            break # Salir del menú diagnóstico

        input("\nPresione Enter para continuar...")


def mostrar_menu_cli(config_actual: dict) -> str:
    """Muestra el menú principal de CLI y devuelve la opción seleccionada."""
    os.system('cls' if os.name == 'nt' else 'clear')
    ultimo_modo = config_actual.get('ultimo_modo_examen_cli', '1')

    menu_texto = (
        "[bold cyan]Seleccione el modo:[/bold cyan]\n\n"
        f"1. [yellow]Paso a paso[/yellow] (Ordenado, con feedback) {'[grey50]<último>[/grey50]' if ultimo_modo == '1' else ''}\n"
        f"2. [yellow]Paso a paso (Random)[/yellow] (Aleatorio, con feedback) {'[grey50]<último>[/grey50]' if ultimo_modo == '2' else ''}\n"
        f"3. [green]Examen Completo[/green] (Ordenado, resultado al final) {'[grey50]<último>[/grey50]' if ultimo_modo == '3' else ''}\n"
        f"4. [green]Examen Completo (Random)[/green] (Aleatorio, resultado al final) {'[grey50]<último>[/grey50]' if ultimo_modo == '4' else ''}\n"
        f"5. [magenta]Práctica Limitada[/magenta] (N preguntas aleatorias)\n"
        f"6. [blue]Diagnóstico[/blue] (Analizar archivo)\n"
        f"7. [red]Salir[/red]"
    )

    console.print(Panel.fit(menu_texto, title="📖 Menú Principal CLI 📖", border_style="blue"))
    opcion = Prompt.ask("Opción", choices=['1', '2', '3', '4', '5', '6', '7'], default=ultimo_modo)

    # Guardar el último modo si no es diagnóstico o salir
    if opcion not in ['6', '7']:
         config_actual['ultimo_modo_examen_cli'] = opcion
         # No guardamos aquí, se guarda al salir del bucle principal
         # app_config.guardar_configuracion({'ultimo_modo_examen_cli': opcion})

    return opcion

def iniciar_cli(preguntas: list, ruta_archivo: str, modo_directo: str = None):
    """Bucle principal para la interfaz de línea de comandos."""
    console.print("[bold green]--- Interfaz de Línea de Comandos Activada ---[/bold green]")

    config = app_config.cargar_configuracion() # Cargar config para menú

    modo = modo_directo # Usar modo directo si se pasó por argumento

    while True:
        if not modo: # Si no hay modo directo, mostrar menú
            modo = mostrar_menu_cli(config)

        preguntas_a_usar = list(preguntas) # Copiar para no modificar la original con shuffle

        # Aleatorizar si corresponde
        if modo in ['2', '4', '5']:
            random.shuffle(preguntas_a_usar)

        # Ejecutar modo
        if modo == '1' or modo == '2':
             modo_paso_a_paso_cli(preguntas_a_usar, ruta_archivo)
        elif modo == '3' or modo == '4':
             modo_examen_cli(preguntas_a_usar, ruta_archivo)
        elif modo == '5':
             modo_practica_limitada_cli(preguntas_a_usar, ruta_archivo)
        elif modo == '6':
             menu_diagnostico_cli(ruta_archivo)
        elif modo == '7':
             break # Salir del bucle principal

        # Si se ejecutó un modo directo, salir después de ejecutarlo una vez
        if modo_directo:
             break

        # Resetear modo para volver a mostrar el menú en la siguiente iteración
        modo = None
        input("\nPresione Enter para volver al menú principal...")

    # Guardar configuración al salir del bucle CLI
    app_config.guardar_configuracion({'ultimo_modo_examen_cli': config.get('ultimo_modo_examen_cli', '1')})
    console.print("[bold cyan]Saliendo del modo CLI.[/bold cyan]")