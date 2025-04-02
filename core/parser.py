# core/parser.py
import re
from collections import namedtuple
from rich.console import Console
import os # Necesario para el log

console = Console()
Pregunta = namedtuple('Pregunta', ['numero', 'enunciado', 'opciones', 'correctas', 'es_multiple'])
LOG_FILE = 'log_parser.txt'

def cargar_preguntas(ruta_archivo, num_esperado=None): # Añadido num_esperado opcional
    """
    Carga las preguntas desde el archivo, con mejor tolerancia a variaciones de formato.
    """
    preguntas = []
    preguntas_problematicas = []

    # Limpiar log anterior al inicio
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
        except OSError as e:
            console.print(f"[yellow]No se pudo limpiar el log anterior: {e}[/yellow]")


    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Normalizar finales de línea y añadir uno al inicio/final para asegurar matches
        contenido = '\n' + contenido.replace('\r\n', '\n').replace('\r', '\n') + '\n'

        # Patrón mejorado para detectar números de pregunta (más robusto a espacios)
        # Busca: salto de línea, dígitos, dos puntos, espacio opcional, salto de línea
        patron_pregunta = r'\n(\d+):[ \t]*\n'

        # Dividir en bloques usando el patrón
        # El resultado es [numero1, contenido1, numero2, contenido2, ...]
        bloques = re.split(patron_pregunta, contenido)

        # El primer elemento suele ser vacío si el archivo empieza con el patrón, lo quitamos
        if bloques and bloques[0].strip() == '':
            bloques = bloques[1:]

        if not bloques:
             console.print("[red]No se pudo dividir el archivo en bloques de preguntas. ¿Formato incorrecto?[/red]")
             return []

        # Procesar bloques en pares (número de pregunta + contenido)
        i = 0
        while i < len(bloques) - 1:
            num_pregunta_str = "?"
            try:
                num_pregunta_str = bloques[i].strip()
                num_pregunta = int(num_pregunta_str) # Validar que sea un número
                contenido_pregunta = bloques[i + 1]

                # Dividir el contenido en líneas limpias
                lineas = [l.strip() for l in contenido_pregunta.split('\n') if l.strip()]
                if not lineas:
                     raise ValueError("Bloque de pregunta vacío.")

                # --- Extracción Mejorada ---
                enunciado_lines = []
                opciones = []
                opcion_actual = None
                correctas_raw = [] # Guardamos las líneas completas de 'Correct Answer'

                patron_opcion = re.compile(r'^([A-Z])\.(.*)') # Captura letra y texto
                patron_correcta = re.compile(r'^Correct Answer:\s*([A-Z])(?:[.\s]|$)', re.IGNORECASE) # Más robusto

                estado = 'enunciado' # Estados: enunciado, opcion, correcta

                for j, linea in enumerate(lineas):
                    match_opcion = patron_opcion.match(linea)
                    match_correcta = patron_correcta.match(linea)

                    if match_opcion:
                        estado = 'opcion'
                        if opcion_actual: # Guardar la opción anterior completa
                            opciones.append(" ".join(opcion_actual['texto']).strip())

                        letra_opcion = match_opcion.group(1)
                        texto_inicial_opcion = match_opcion.group(2).strip()
                        opcion_actual = {'letra': letra_opcion, 'texto': [texto_inicial_opcion]}

                    elif match_correcta:
                        # Solo nos interesa la letra
                        letra_correcta = match_correcta.group(1).upper()
                        if letra_correcta not in correctas_raw:
                             correctas_raw.append(letra_correcta)
                        # Continuamos procesando por si hay más texto en la línea (aunque no debería)
                        if estado == 'opcion' and opcion_actual:
                            pass # No añadir "Correct Answer" al texto de la opción
                        elif estado == 'enunciado':
                            pass # Tampoco al enunciado

                    # Si no es inicio de opción ni respuesta, añadir al elemento actual
                    elif estado == 'enunciado':
                        enunciado_lines.append(linea)
                    elif estado == 'opcion' and opcion_actual:
                        # Añadir línea a la opción actual si no es una línea de "Correct Answer" redundante
                        if not patron_correcta.match(linea):
                             opcion_actual['texto'].append(linea.strip())

                # Guardar la última opción
                if opcion_actual:
                    opciones.append(" ".join(opcion_actual['texto']).strip())

                enunciado = " ".join(enunciado_lines).strip()

                if not enunciado:
                     raise ValueError("Enunciado vacío.")
                if not opciones:
                    raise ValueError("No se encontraron opciones.")
                if not correctas_raw:
                    raise ValueError("No se encontró 'Correct Answer:'.")

                # Validar que las letras correctas correspondan a opciones existentes
                letras_opciones_validas = [chr(65 + k) for k in range(len(opciones))]
                correctas = sorted(list(set(letra for letra in correctas_raw if letra in letras_opciones_validas)))

                if not correctas:
                     raise ValueError(f"Las respuestas correctas indicadas ({correctas_raw}) no coinciden con las opciones válidas ({letras_opciones_validas}).")


                es_multiple = len(correctas) > 1

                # Logging detallado
                with open(LOG_FILE, 'a', encoding='utf-8') as log:
                    log.write(f"--- Pregunta {num_pregunta_str} ---\n")
                    log.write(f"Enunciado: {enunciado}\n")
                    log.write(f"Opciones ({len(opciones)}): {letras_opciones_validas}\n")
                    for idx, opt_text in enumerate(opciones):
                         log.write(f"  {chr(65+idx)}. {opt_text}\n")
                    log.write(f"Correctas Detectadas (raw): {correctas_raw}\n")
                    log.write(f"Correctas Validadas: {correctas}\n")
                    log.write(f"Es Múltiple: {es_multiple}\n\n")


                preguntas.append(Pregunta(
                    numero=num_pregunta_str, # Guardar como string por si acaso
                    enunciado=enunciado,
                    opciones=opciones,
                    correctas=correctas, # Lista de letras correctas validadas
                    es_multiple=es_multiple
                ))

            except Exception as e:
                error_msg = f"Error procesando bloque después de pregunta '{num_pregunta_str}': {str(e)}"
                preguntas_problematicas.append((num_pregunta_str, str(e)))
                console.print(f"[red]❌ {error_msg}[/red]")
                with open(LOG_FILE, 'a', encoding='utf-8') as log:
                     log.write(f"*** ERROR en pregunta ~{num_pregunta_str} ***\n{error_msg}\n")
                     # Intentar loguear el bloque problemático
                     if 'contenido_pregunta' in locals():
                          log.write("--- Bloque de contenido ---\n")
                          log.write(contenido_pregunta + "\n-------------------------\n\n")


            i += 2 # Avanzar al siguiente par (número + contenido)

    except FileNotFoundError:
         console.print(f"[bold red]❌ Error: Archivo no encontrado en '{ruta_archivo}'[/bold red]")
         return []
    except Exception as e:
        console.print(f"[bold red]❌ Error general al leer o procesar el archivo: {str(e)}[/bold red]")
        # Loguear el error general también
        with open(LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(f"*** ERROR GENERAL ***\n{str(e)}\n")
        return preguntas # Devolver lo que se haya podido parsear

    # --- Resumen Final del Parseo ---
    if preguntas_problematicas:
        console.print(f"[yellow]⚠️ {len(preguntas_problematicas)} bloques tuvieron problemas durante el parseo (ver detalles arriba y en {LOG_FILE}).[/yellow]")

    # Verificar número esperado si se proporcionó
    if num_esperado is not None and len(preguntas) != num_esperado:
         console.print(f"[yellow]⚠️ Se esperaban {num_esperado} preguntas, pero se cargaron {len(preguntas)} válidas.[/yellow]")

    if not preguntas and not preguntas_problematicas:
         console.print("[red]No se cargó ninguna pregunta y no hubo errores específicos de bloque. Revise el formato general del archivo.[/red]")


    return preguntas