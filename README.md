# Examen IA - Simulador de Exámenes

## Descripción

Este proyecto es un simulador de exámenes versátil que permite a los usuarios practicar con preguntas cargadas desde archivos de texto (`.txt`). Ofrece interfaces tanto gráficas (GUI) como de línea de comandos (CLI) y múltiples modos de examen, incluyendo feedback inmediato y evaluación final.

## Características Principales

* **Carga de Preguntas:** Importa preguntas y respuestas desde archivos `.txt` formateados [2].
* **Múltiples Interfaces:**
    * Interfaz Gráfica de Usuario (GUI) basada en Tkinter (`ui/gui.py`).
    * Interfaz de Línea de Comandos (CLI) interactiva basada en Rich (`core/examen_runner.py`).
* **Modos de Examen:**
    * **Paso a Paso:** Feedback inmediato (correcto/incorrecto) después de cada pregunta [22, 48].
    * **Examen Completo:** Responde todas las preguntas; el resultado se muestra al final.
    * **Práctica Limitada (CLI):** Responde un número N de preguntas aleatorias.
    * **Orden Aleatorio:** Opción para barajar las preguntas en los modos principales.
* **Tipos de Pregunta:** Soporta preguntas de selección única y selección múltiple [26, 53].
* **Exportación de Resultados:** Guarda los resultados detallados del examen en formato `.txt` y/o `.pdf` (`core/exportador.py`).
* **Configuración Persistente:** Guarda la última ruta de archivo y modo de interfaz utilizados (`examen_config.json`).
* **Diagnóstico (CLI):** Herramientas para analizar archivos de preguntas en busca de problemas de formato o numeración (`core/diagnostico.py`).
* **Logging del Parser:** Genera `log_parser.txt` con detalles sobre el proceso de carga de preguntas (`core/parser.py`).

## Estructura del Proyecto

```
examen-ia/
│
├── core/                 # Lógica principal del programa
│   ├── __init__.py
│   ├── config.py         # Manejo de configuración (examen_config.json)
│   ├── diagnostico.py    # Funciones de análisis de archivos
│   ├── examen_runner.py  # Lógica de ejecución de exámenes (CLI y común)
│   ├── exportador.py     # Funciones para exportar resultados (TXT, PDF)
│   └── parser.py         # Carga y análisis de archivos de preguntas
│
├── ui/                   # Componentes de la interfaz de usuario
│   ├── __init__.py
│   ├── gui.py            # Interfaz Gráfica de Usuario (Tkinter)
│   ├── popup_correcto.py # Ventana emergente para respuesta correcta
│   ├── popup_incorrecto.py# Ventana emergente para respuesta incorrecta
│   └── widgets.py        # (Potencialmente para widgets reutilizables)
│
├── main.py               # Punto de entrada principal de la aplicación
├── requirements.txt      # Dependencias de Python
├── test.txt              # Archivo de ejemplo con preguntas
└── examen_config.json    # Archivo de configuración (creado/actualizado por la app)
└── log_parser.txt        # Archivo de log (creado por la app)
```

## Requisitos

* **Python 3.x**
* Dependencias listadas en `requirements.txt` [1]. Instalar con:
    ```bash
    pip install -r requirements.txt
    ```
    Las dependencias clave directamente utilizadas por el simulador son:
    * `rich`: Para la interfaz CLI mejorada.
    * `fpdf`: Para la exportación a PDF.
    * (Tkinter suele venir incluido con Python estándar)
    * *Nota: Revisa si todas las dependencias en `requirements.txt` son necesarias para este proyecto.*

## Formato del Archivo de Preguntas (`.txt`)

El archivo de preguntas debe seguir este formato (ver `test.txt` como ejemplo) [2]:

```
[NúmeroPregunta]:
[Enunciado de la pregunta - puede ocupar varias líneas] [3, 4]
A. [Texto de la opción A] [5]
B. [Texto de la opción B] [15]
C. [Texto de la opción C] [6, 12]
...
Correct Answer: [Letra(s) correcta(s)] [10, 14]
```

* Cada pregunta empieza con `Número:` en una línea nueva.
* El enunciado sigue al número.
* Las opciones empiezan con `Letra.` (A., B., C., etc.).
* La(s) respuesta(s) correcta(s) se indican con `Correct Answer: Letra`.
* Para preguntas de **selección múltiple**, añade una línea `Correct Answer: Letra` por cada opción correcta [26, 55].
* Deja al menos una línea en blanco entre preguntas.

## Uso

Ejecuta la aplicación desde la terminal en el directorio raíz del proyecto:

```bash
python main.py [opciones]
```

### Selección de Interfaz

Al iniciar sin argumentos, la aplicación te preguntará si deseas usar la interfaz gráfica (GUI) o la de línea de comandos (CLI), usando la última guardada como predeterminada.

Puedes forzar una interfaz específica:

* `python main.py --interfaz gui`
* `python main.py --interfaz cli`

### Selección de Archivo

Si no especificas un archivo, la aplicación te preguntará si quieres usar el último archivo recordado (mostrado en la consola) o seleccionar uno nuevo mediante un diálogo gráfico.

Puedes especificar un archivo directamente:

* `python main.py --archivo ruta/a/tu/archivo.txt`

### Opciones Específicas de CLI

Si eliges o fuerzas la interfaz CLI, puedes seleccionar un modo directamente o se mostrará un menú interactivo si no especificas `--modo-cli`.

* `python main.py --interfaz cli --modo-cli [1-6]`
    * `1`: Paso a paso (Ordenado)
    * `2`: Paso a paso (Aleatorio)
    * `3`: Examen Completo (Ordenado)
    * `4`: Examen Completo (Aleatorio)
    * `5`: Práctica Limitada (N preguntas aleatorias)
    * `6`: Diagnóstico del archivo de preguntas

### Interfaz Gráfica (GUI)

La GUI (`ui/gui.py`) ofrece una experiencia visual:
* **Menú Archivo:** Abrir nuevos archivos de preguntas, Salir.
* **Menú Modo:** Cambiar entre "Paso a Paso" (feedback inmediato) y "Examen Completo" (resultado al final), Reiniciar el examen (ordenado o aleatorio).
* Navega entre preguntas usando "Anterior" / "Siguiente" (solo en modo "Examen Completo").
* Selecciona tus respuestas usando los checkboxes.
* Recibe feedback visual inmediato (popups en modo "Paso a Paso") o un resumen final.
* Opción de exportar resultados detallados a TXT/PDF al finalizar.

### Interfaz de Línea de Comandos (CLI)

La CLI (`core/examen_runner.py`) usa `rich` para una experiencia mejorada:
* Menú interactivo para seleccionar modos de examen o herramientas de diagnóstico.
* Muestra preguntas y opciones formateadas.
* Valida las entradas del usuario.
* Proporciona feedback detallado o resumen final en la consola.
* Permite exportar resultados.

## Exportación

Al finalizar un examen (o al terminar el modo paso a paso), se te ofrecerá exportar los resultados. Puedes elegir formato TXT, PDF o ambos. Los archivos se guardarán en el mismo directorio que el archivo de preguntas, con un nombre que incluye `resultados_`, el nombre base del archivo de preguntas, y la fecha/hora.

## Diagnóstico (CLI)

El modo Diagnóstico (opción 6 en CLI) (`core/diagnostico.py`) permite analizar el archivo de preguntas actual para detectar:
* Problemas básicos de formato (ej. falta de 'N:', 'Correct Answer:').
* Números de pregunta faltantes o duplicados en la secuencia.
* Errores durante el parseo (revisar también `log_parser.txt`).

Consulta la salida en la terminal para los resultados del diagnóstico.
