# Examen Interactivo por Consola

Un sistema de exámenes interactivo basado en consola con múltiples modos de práctica, retroalimentación en tiempo real, y soporte multiplataforma.

## 📋 Descripción

Este proyecto implementa un sistema interactivo para realizar exámenes de opción múltiple en una interfaz de línea de comandos con una experiencia visual mejorada. Permite cargar archivos de preguntas personalizados y ofrece diferentes modos de práctica para adaptarse a las necesidades de aprendizaje del usuario.

### ✨ Características principales

- **Interfaz rica en consola**: Visualización con colores, paneles informativos y progreso visual
- **Múltiples modos de examen**:
  - Paso a paso (con retroalimentación inmediata)
  - Examen completo (simula un examen real)
  - Modo aleatorio (preguntas en orden aleatorio)
  - Práctica limitada (selecciona un número específico de preguntas)
- **Compatibilidad multiplataforma**: Funciona en Windows, macOS y Linux
- **Guardado de preferencias**: Recuerda la última configuración utilizada
- **Exportación de resultados**: Permite guardar los resultados en un archivo de texto
- **Selección de archivos visual**: Mediante cuadro de diálogo o entrada manual

## 🔧 Requisitos

- Python 3.6 o superior
- Bibliotecas requeridas:
  - `rich`: Para la interfaz mejorada en consola
  - `tkinter`: Para el cuadro de diálogo de selección de archivos (incluido en la mayoría de las instalaciones de Python)

### Requisitos específicos por plataforma

- **Windows**: No requiere bibliotecas adicionales (utiliza `msvcrt` incluido en Python)
- **macOS/Linux**: Puede requerir `pynput` en algunos casos (como respaldo)

## 🚀 Instalación

1. **Clonar el repositorio**:

```bash
git clone https://github.com/usuario/examen-interactivo.git
cd examen-interactivo
```

2. **Instalar las dependencias**:

```bash
pip install rich 

# Solo en algunos sistemas Unix/Linux/Mac (si el método estándar no funciona)
pip install pynput
```

## 📁 Estructura del proyecto

```
examen-interactivo/
│
├── examen_listado.py     # Programa principal
├── Fundamentos_IA.txt    # Ejemplo de archivo de preguntas
├── README.md             # Este archivo
├── config.json           # Configuración (se genera automáticamente)
└── resultados_*.txt      # Archivos de resultados (generados al exportar)
```

## 📖 Formato del archivo de preguntas

El programa espera archivos de texto con un formato específico:

```
1:
¿Pregunta de ejemplo?
A. Primera opción
B. Segunda opción
C. Tercera opción
D. Cuarta opción
Correct Answer: B

2:
¿Otra pregunta?
A. Opción uno
B. Opción dos
C. Opción tres
D. Opción cuatro
Correct Answer: D
```

**Reglas importantes**:
- Cada pregunta comienza con un número seguido de dos puntos (ej. `1:`)
- Las opciones deben estar etiquetadas con A, B, C y D seguidas de un punto
- La respuesta correcta debe indicarse con `Correct Answer: X` donde X es A, B, C o D
- Se permite que el enunciado o las opciones ocupen varias líneas
- Debe haber una línea en blanco entre preguntas

## 🎮 Uso

### Ejecución básica

```bash
python examen_listado.py
```

El programa mostrará un menú interactivo que permite seleccionar el archivo de preguntas y el modo de examen.

### Ejecución con argumentos

```bash
# Especificar un archivo de preguntas
python examen_listado.py -f mi_archivo.txt

# Especificar modo de examen (1-5)
python examen_listado.py -m 2

# Especificar número de preguntas para modo práctica
python examen_listado.py -m 5 -n 10

# Combinando opciones
python examen_listado.py -f mi_archivo.txt -m 4
```

### Opciones disponibles

- `-f, --file`: Ruta al archivo de preguntas
- `-m, --mode`: Modo de examen (1-5)
  - `1`: Paso a paso (orden original)
  - `2`: Paso a paso (aleatorio)
  - `3`: Examen completo (orden original)
  - `4`: Examen completo (aleatorio)
  - `5`: Práctica limitada
- `-n, --num`: Número de preguntas para modo práctica limitada

## 📊 Modos de examen

### 1️⃣ Paso a paso
- Muestra preguntas una por una
- Proporciona retroalimentación inmediata tras cada respuesta
- Mantiene el orden original del archivo

### 2️⃣ Paso a paso (aleatorio)
- Similar al modo Paso a paso
- Presenta las preguntas en orden aleatorio

### 3️⃣ Examen completo
- Simula un examen real
- Muestra todas las preguntas secuencialmente
- Proporciona retroalimentación para cada pregunta
- Muestra un resumen completo al final

### 4️⃣ Examen completo (aleatorio)
- Similar al modo Examen completo
- Presenta las preguntas en orden aleatorio

### 5️⃣ Práctica limitada
- Permite seleccionar un número específico de preguntas
- Preguntas seleccionadas aleatoriamente
- Funciona en modo paso a paso con retroalimentación

## 🔄 Interacción con el programa

- Usa las teclas **A**, **B**, **C**, **D** para responder preguntas
- Pulsa **Enter** para continuar entre preguntas o pantallas
- En los menús, pulsa la tecla numérica correspondiente a tu elección

## 📝 Creando tus propios archivos de preguntas

Puedes crear tus propios archivos de preguntas siguiendo el formato descrito anteriormente. Recomendaciones:

1. Usa un editor de texto simple (Notepad, VS Code, etc.)
2. Guarda el archivo en formato UTF-8
3. Verifica que cada pregunta tenga exactamente 4 opciones (A-D)
4. Asegúrate de que cada pregunta tenga una respuesta correcta indicada
5. Mantén una línea en blanco entre preguntas

### Ejemplo de archivo personalizado

```
1:
¿Cuál es la capital de Francia?
A. Londres
B. Berlín
C. París
D. Madrid
Correct Answer: C

2:
¿En qué año comenzó la Segunda Guerra Mundial?
A. 1939
B. 1940
C. 1941
D. 1945
Correct Answer: A
```

## 🔍 Solución de problemas

### El programa no detecta las teclas correctamente
- **Windows**: Asegúrate de ejecutar el programa en una ventana de comando (CMD o PowerShell)
- **Linux/Mac**: Instala `pynput` con `pip install pynput` y vuelve a intentarlo

### El programa muestra caracteres extraños
- Verifica que tu archivo de preguntas esté guardado en formato UTF-8
- Ejecuta el programa en una terminal que soporte caracteres Unicode

### Error al cargar archivo de preguntas
- Verifica que el formato del archivo siga exactamente la estructura requerida
- Comprueba que el archivo exista en la ruta especificada

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Pasos para contribuir:

1. Haz un fork del repositorio
2. Crea una rama para tu función (`git checkout -b nueva-funcion`)
3. Realiza tus cambios y haz commit (`git commit -m 'Agrega nueva función'`)
4. Sube los cambios a tu fork (`git push origin nueva-funcion`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 📞 Contacto

Si tienes preguntas o sugerencias, no dudes en abrir un issue en el repositorio.

---

**Desarrollado por Jorge Torlaschi**

¡Espero que disfrutes usando este programa para tus exámenes y prácticas!