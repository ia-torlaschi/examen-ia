# core/exportador.py
from fpdf import FPDF
import time
import os
from rich.console import Console

# Requerido para que funcione desde main.py o examen_runner.py
try:
    from . import parser # Asume que parser está en el mismo directorio
except ImportError:
    import parser # Fallback si se ejecuta de otra forma

console = Console()

# Helper para limpiar texto para PDF (evita errores con caracteres especiales)
def clean_text(text):
    # FPDF usa 'latin-1' por defecto si no se usan fuentes TTF
    # Reemplazar caracteres no compatibles
    return text.encode('latin-1', 'replace').decode('latin-1')

def exportar_txt(resultados: list[tuple], aciertos: int, total: int, ruta='resultados.txt'):
    """
    Exporta los resultados a un archivo TXT.
    'resultados' es una lista de tuplas: (pregunta_obj, respuesta_usuario_lista)
    """
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(f"Resultados del Examen - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            puntuacion = (aciertos / total) * 100 if total > 0 else 0
            f.write(f"Puntuación: {puntuacion:.2f}% ({aciertos}/{total})\n\n")
            f.write("--- Detalle de Respuestas ---\n")

            for i, (pregunta, respuesta_usuario) in enumerate(resultados, 1):
                # Necesitamos re-evaluar la corrección aquí si no viene en los datos
                # Asumimos que es_respuesta_correcta está disponible o la reimportamos
                try:
                     from .examen_runner import es_respuesta_correcta
                except ImportError:
                     from examen_runner import es_respuesta_correcta # Fallback

                correcta = es_respuesta_correcta(pregunta, respuesta_usuario)
                estado = 'Correcta' if correcta else 'Incorrecta'
                resp_usr_str = ", ".join(sorted(respuesta_usuario)) if respuesta_usuario else "(ninguna)"
                resp_corr_str = ", ".join(sorted(pregunta.correctas))

                f.write(f"\n{i}. Pregunta #{pregunta.numero}: {estado}\n")
                f.write(f"   Enunciado: {pregunta.enunciado}\n") # Guardar enunciado
                # Opciones (opcional pero útil)
                # for idx, opt_txt in enumerate(pregunta.opciones):
                #      f.write(f"     {chr(65+idx)}. {opt_txt}\n")
                f.write(f"   Tu respuesta: {resp_usr_str}\n")
                if not correcta:
                    f.write(f"   Respuesta correcta: {resp_corr_str}\n")

        console.print(f"[green]Resultados guardados en TXT: {ruta}[/green]")

    except Exception as e:
        console.print(f"[red]Error al exportar a TXT: {e}[/red]")


def exportar_pdf(resultados: list[tuple], aciertos: int, total: int, ruta='resultados.pdf'):
    """
    Exporta los resultados a un archivo PDF.
    'resultados' es una lista de tuplas: (pregunta_obj, respuesta_usuario_lista)
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12) # Usar fuente estándar compatible

        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Resultados del Examen", ln=True, align='C')
        pdf.ln(5)

        # Puntuación
        pdf.set_font("Arial", 'B', 14)
        puntuacion = (aciertos / total) * 100 if total > 0 else 0
        pdf.cell(0, 10, txt=f"Puntuacion: {puntuacion:.2f}% ({aciertos}/{total})", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=10) # Tamaño más pequeño para detalles

        for i, (pregunta, respuesta_usuario) in enumerate(resultados, 1):
            # Re-evaluar corrección
            try:
                 from .examen_runner import es_respuesta_correcta
            except ImportError:
                 from examen_runner import es_respuesta_correcta # Fallback
            correcta = es_respuesta_correcta(pregunta, respuesta_usuario)
            estado = 'Correcta' if correcta else 'Incorrecta'
            resp_usr_str = ", ".join(sorted(respuesta_usuario)) if respuesta_usuario else "(ninguna)"
            resp_corr_str = ", ".join(sorted(pregunta.correctas))

            # Encabezado de pregunta
            pdf.set_font("Arial", 'B', 10)
            pdf.multi_cell(0, 5, txt=clean_text(f"{i}. Pregunta #{pregunta.numero}: {estado}"))
            pdf.set_font("Arial", size=10)

            # Enunciado (limpiado)
            pdf.multi_cell(0, 5, txt=clean_text(f"   Enunciado: {pregunta.enunciado}"))

            # Respuesta Usuario
            pdf.multi_cell(0, 5, txt=clean_text(f"   Tu respuesta: {resp_usr_str}"))

            # Respuesta Correcta (si falló)
            if not correcta:
                pdf.set_font("Arial", 'I', 10) # Cursiva para la correcta
                pdf.multi_cell(0, 5, txt=clean_text(f"   Respuesta correcta: {resp_corr_str}"))
                pdf.set_font("Arial", size=10) # Volver a normal

            pdf.ln(4) # Espacio entre preguntas

            # Control de salto de página (simple)
            if pdf.get_y() > 260: # Cerca del final de la página
                pdf.add_page()
                pdf.set_font("Arial", size=10) # Restablecer fuente en nueva página

        pdf.output(ruta)
        console.print(f"[green]Resultados guardados en PDF: {ruta}[/green]")

    except Exception as e:
        console.print(f"[red]Error al exportar a PDF: {e}[/red]")
        console.print("[yellow]Asegúrate de que la librería FPDF está instalada (`pip install fpdf`).[/yellow]")