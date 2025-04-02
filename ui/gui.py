import tkinter as tk
from tkinter import messagebox, simpledialog, Menu # Añadido Menu
import random
import os # Para path de config
import sys # Para path
import time # Para Exportación
from tkinter import filedialog # Para Abrir Archivo

# Asegurarse de que el directorio raíz esté en el path para encontrar 'core'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core import parser, examen_runner, exportador, config as app_config
from ui.popup_correcto import mostrar_popup_correcto
from ui.popup_incorrecto import mostrar_popup_incorrecto

class SimuladorExamenGUI:
    def __init__(self, root, preguntas_originales, ruta_archivo):
        self.root = root
        self.preguntas_originales = preguntas_originales # Mantener lista original
        self.preguntas_actuales = list(preguntas_originales) # Copia para el examen actual
        self.ruta_archivo = ruta_archivo
        self.indice_actual = 0
        self.resultados_examen = [] # Almacena tuplas: (pregunta_obj, respuesta_usuario_lista)
        self.modo_examen = "paso_a_paso" # 'paso_a_paso', 'examen_completo'

        self.setup_ui()
        self.mostrar_pregunta_actual()

    def setup_ui(self):
        self.root.title(f"Simulador de Examen - {os.path.basename(self.ruta_archivo)}")
        self.root.geometry("850x550") # Más alto para feedback/botones
        self.root.configure(bg="white")

        # --- Menú Superior ---
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Menú Archivo
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        self.file_menu.add_command(label="Abrir Archivo...", command=self.abrir_archivo)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)

        # Menú Modo
        self.mode_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Modo", menu=self.mode_menu)
        self.mode_var = tk.StringVar(value=self.modo_examen)
        self.mode_menu.add_radiobutton(label="Paso a Paso (Feedback inmediato)", variable=self.mode_var,
                                        value="paso_a_paso", command=self.cambiar_modo)
        self.mode_menu.add_radiobutton(label="Examen Completo (Resultado al final)", variable=self.mode_var,
                                        value="examen_completo", command=self.cambiar_modo)
        self.mode_menu.add_separator()
        self.mode_menu.add_command(label="Reiniciar Examen (Ordenado)", command=lambda: self.reiniciar_examen(randomize=False))
        self.mode_menu.add_command(label="Reiniciar Examen (Aleatorio)", command=lambda: self.reiniciar_examen(randomize=True))
        # Podría añadirse Práctica Limitada aquí

        # Menú Herramientas (Diagnóstico)
        # self.tools_menu = Menu(self.menu_bar, tearoff=0)
        # self.menu_bar.add_cascade(label="Herramientas", menu=self.tools_menu)
        # self.tools_menu.add_command(label="Diagnosticar Archivo Actual", command=self.ejecutar_diagnostico)
        # (...) Añadir más opciones de diagnóstico si se desea

        # --- Contenido Principal ---
        self.frame_info = tk.Frame(self.root, bg="white")
        self.frame_info.pack(fill="x", padx=20, pady=(10, 0))

        self.titulo_label = tk.Label(self.frame_info, text="", font=("Arial", 11, "italic"), bg="white", anchor="w")
        self.titulo_label.pack(side="left")

        self.modo_label = tk.Label(self.frame_info, text=f"Modo: {self.modo_examen.replace('_',' ')}", font=("Arial", 10), bg="white", fg="blue", anchor="e")
        self.modo_label.pack(side="right")


        self.pregunta_text = tk.Text(self.root, font=("Arial", 14, "bold"), wrap="word", height=4, borderwidth=0, bg="white", relief="flat")
        self.pregunta_text.pack(fill="x", padx=20, pady=5)
        self.pregunta_text.config(state="disabled") # Para mostrar, no editar

        self.frame_opciones = tk.Frame(self.root, bg="white")
        self.frame_opciones.pack(fill="both", expand=True, anchor="nw", padx=20) # Expandir para opciones largas

        self.frame_botones = tk.Frame(self.root, bg="white")
        self.frame_botones.pack(fill="x", pady=10, padx=20)

        self.boton_anterior = tk.Button(self.frame_botones, text="⬅ Anterior", command=self.pregunta_anterior, font=("Arial", 12), state="disabled")
        self.boton_anterior.pack(side="left", padx=5)

        self.boton_siguiente = tk.Button(self.frame_botones, text="Siguiente ➡", command=self.procesar_respuesta_y_avanzar, font=("Arial", 12, "bold"))
        self.boton_siguiente.pack(side="right", padx=5)

        # Espacio para feedback en modo examen completo (opcional)
        # self.feedback_label = tk.Label(self.root, text="", font=("Arial", 10), bg="white")
        # self.feedback_label.pack(pady=5)


    def mostrar_pregunta_actual(self):
        if not self.preguntas_actuales or self.indice_actual >= len(self.preguntas_actuales):
            self.finalizar_examen()
            return

        p = self.preguntas_actuales[self.indice_actual]
        num_total = len(self.preguntas_actuales)

        # Actualizar título
        tipo_pregunta = f" (Múltiple - {len(p.correctas)})" if p.es_multiple else ""
        self.titulo_label.config(text=f"Pregunta {self.indice_actual + 1} de {num_total} (#{p.numero}){tipo_pregunta}")

        # Mostrar enunciado en Text widget
        self.pregunta_text.config(state="normal")
        self.pregunta_text.delete("1.0", tk.END)
        self.pregunta_text.insert("1.0", f"{self.indice_actual + 1}. {p.enunciado}")
        self.pregunta_text.config(state="disabled")

        # Limpiar opciones anteriores
        for widget in self.frame_opciones.winfo_children():
            widget.destroy()

        # Crear checkboxes para opciones
        self.vars_opciones = []
        letras_validas = [chr(65 + i) for i in range(len(p.opciones))]

        for i, opcion_texto in enumerate(p.opciones):
            var = tk.BooleanVar() # Usar BooleanVar para checkboxes
            letra = letras_validas[i]
            cb = tk.Checkbutton(self.frame_opciones, text=f"{letra}. {opcion_texto}", variable=var,
                                font=("Arial", 12), anchor="nw", justify="left", wraplength=750, # Ajustar wraplength
                                bg="white", padx=10, pady=2)
            cb.pack(fill="x", anchor="w")
            self.vars_opciones.append((var, letra)) # Guardar variable y letra asociada

        # Restaurar selección si se está navegando hacia atrás/adelante en modo examen
        if self.modo_examen == "examen_completo" and self.indice_actual < len(self.resultados_examen):
            pregunta_guardada, respuesta_guardada = self.resultados_examen[self.indice_actual]
            if pregunta_guardada.numero == p.numero and respuesta_guardada: # Si hay respuesta guardada para esta pregunta
                 for var, letra in self.vars_opciones:
                      if letra in respuesta_guardada:
                           var.set(True)

        # Actualizar estado botones navegación
        self.boton_anterior.config(state="normal" if self.indice_actual > 0 and self.modo_examen == "examen_completo" else "disabled")
        self.boton_siguiente.config(text="Siguiente ➡" if self.indice_actual < num_total - 1 else "Finalizar Examen")


    def procesar_respuesta_y_avanzar(self):
            if not self.preguntas_actuales or self.indice_actual >= len(self.preguntas_actuales):
                # Si el índice está fuera de rango (ya terminó), no hacer nada o finalizar explícitamente
                # self.finalizar_examen() # Podría llamarse aquí si se llega inesperadamente
                return

            # --- Línea Faltante Añadida ---
            p = self.preguntas_actuales[self.indice_actual]
            # -----------------------------

            # Obtener respuestas seleccionadas de las variables de los checkboxes
            seleccionadas = [letra for var, letra in self.vars_opciones if var.get()]

            # --- Validación de Cantidad ---
            # Ahora 'p' está definida y esta línea funcionará
            if p.es_multiple and len(seleccionadas) != len(p.correctas):
                messagebox.showwarning("Selección Incompleta",
                                       f"Debes seleccionar exactamente {len(p.correctas)} opciones para esta pregunta.\n"
                                       f"Has seleccionado {len(seleccionadas)}.")
                return # No continuar si la selección es inválida

            # --- Guardar Respuesta ---
            while len(self.resultados_examen) <= self.indice_actual:
                self.resultados_examen.append(None)
            self.resultados_examen[self.indice_actual] = (p, seleccionadas)

            # --- Deshabilitar Botón ANTES de mostrar popup ---
            self.boton_siguiente.config(state="disabled")
            self.boton_anterior.config(state="disabled") # Deshabilitar ambos mientras se muestra popup

            # --- Feedback (si aplica) ---
            if self.modo_examen == "paso_a_paso":
                es_correcta = examen_runner.es_respuesta_correcta(p, seleccionadas)
                if es_correcta:
                    # Usar el NUEVO callback que rehabilita el botón
                    mostrar_popup_correcto(self.root, on_close=self.callback_despues_de_popup)
                else:
                    # Crear mensaje simple
                    simple_mensaje = f"Tu respuesta: {', '.join(seleccionadas) if seleccionadas else '(ninguna)'}"
                    # Usar el NUEVO callback que rehabilita el botón
                    mostrar_popup_incorrecto(self.root, p, mensaje=simple_mensaje,
                                             on_close=self.callback_despues_de_popup)
            else: # Modo examen_completo
                # En modo examen, el avance es directo, rehabilitar botón inmediatamente después
                self.ir_a_siguiente_pregunta() # Esto actualiza el índice y la UI
                # Rehabilitar botón (solo si no hemos llegado al final)
                # El estado de los botones se gestiona en mostrar_pregunta_actual ahora
                # if self.indice_actual < len(self.preguntas_actuales):
                #      self.boton_siguiente.config(state="normal")
                #      self.boton_anterior.config(state="normal" if self.indice_actual > 0 else "disabled")
                # Simplificado: mostrar_pregunta_actual se encarga de los estados de los botones

    def ir_a_siguiente_pregunta(self):
        """Avanza al siguiente índice y muestra la pregunta."""
        # ESTA FUNCIÓN YA *NO* REHABILITA EL BOTÓN
        if self.indice_actual < len(self.preguntas_actuales) - 1:
            self.indice_actual += 1
            self.mostrar_pregunta_actual() # mostrar_pregunta_actual ajusta el texto/estado del botón si es necesario
        else:
             # Si estamos en modo paso a paso y cerramos el popup de la última, finaliza
             # Si estamos en modo examen, el botón 'Finalizar' llama a finalizar_examen
             if self.modo_examen == "paso_a_paso":
                  self.finalizar_examen()
             # En modo examen, mostrar_pregunta_actual ya habrá cambiado el texto a "Finalizar"
             # y procesar_respuesta_y_avanzar llamará a finalizar_examen la próxima vez

    def pregunta_anterior(self):
        """Retrocede al índice anterior (solo en modo examen)."""
        if self.modo_examen == "examen_completo" and self.indice_actual > 0:
             # No es necesario guardar la respuesta actual al ir atrás, ya se guarda al ir adelante
             self.indice_actual -= 1
             self.mostrar_pregunta_actual()


    def finalizar_examen(self):
        """Muestra el resumen final, calcula resultados y ofrece exportar."""
        # Deshabilitar botones de navegación
        self.boton_siguiente.config(state="disabled", text="Examen Finalizado")
        self.boton_anterior.config(state="disabled")

        # Limpiar area de pregunta/opciones (opcional)
        # for widget in self.frame_opciones.winfo_children(): widget.destroy()
        # self.pregunta_text.config(state="normal"); self.pregunta_text.delete("1.0", tk.END); self.pregunta_text.config(state="disabled")

        # Calcular resultados (si es modo examen_completo o si hay resultados de paso_a_paso)
        num_respondidas = len([res for res in self.resultados_examen if res is not None])
        if num_respondidas == 0:
             messagebox.showinfo("Examen Vacío", "No se ha respondido ninguna pregunta.")
             return

        aciertos = 0
        resultados_validos = [] # Lista de (pregunta, respuesta_usr) para exportar
        for resultado in self.resultados_examen:
             if resultado: # Ignorar Nones si el examen se interrumpió
                  pregunta_obj, respuesta_usr = resultado
                  resultados_validos.append((pregunta_obj, respuesta_usr))
                  if examen_runner.es_respuesta_correcta(pregunta_obj, respuesta_usr):
                      aciertos += 1

        total_preguntas_evaluadas = len(resultados_validos)
        puntuacion = (aciertos / total_preguntas_evaluadas) * 100 if total_preguntas_evaluadas > 0 else 0

        # Mostrar Resumen
        resumen_texto = f"Examen Finalizado\n\n"
        resumen_texto += f"Preguntas Respondidas: {total_preguntas_evaluadas}/{len(self.preguntas_actuales)}\n"
        resumen_texto += f"Aciertos: {aciertos}\n"
        resumen_texto += f"Puntuación: {puntuacion:.2f}%\n\n"
        resumen_texto += "¿Desea guardar los resultados detallados?"

        if messagebox.askyesno("Resultados Finales", resumen_texto):
            self.exportar_resultados_gui(resultados_validos, aciertos, total_preguntas_evaluadas)


    def exportar_resultados_gui(self, resultados_export, aciertos, total):
         """Pregunta formato y guarda resultados desde GUI."""
         formato = simpledialog.askstring("Exportar Resultados", "Seleccione formato (txt, pdf, ambos):", initialvalue="txt")
         if not formato: return # Cancelado

         formato = formato.lower().strip()
         timestamp = time.strftime("%Y%m%d_%H%M%S")
         base_name = os.path.splitext(os.path.basename(self.ruta_archivo))[0]
         ruta_base = os.path.dirname(self.ruta_archivo) # Guardar en el mismo dir

         try:
            exportado = False
            if formato in ["txt", "ambos"]:
                ruta_txt = os.path.join(ruta_base, f"resultados_{base_name}_{timestamp}.txt")
                exportador.exportar_txt(resultados_export, aciertos, total, ruta_txt)
                exportado = True
            if formato in ["pdf", "ambos"]:
                ruta_pdf = os.path.join(ruta_base, f"resultados_{base_name}_{timestamp}.pdf")
                exportador.exportar_pdf(resultados_export, aciertos, total, ruta_pdf)
                exportado = True

            if exportado:
                 messagebox.showinfo("Exportación Exitosa", f"Resultados guardados correctamente en:\n{ruta_base}")
            else:
                 messagebox.showwarning("Formato Inválido", "Formato no reconocido. No se exportó nada.")

         except Exception as e:
            messagebox.showerror("Error de Exportación", f"No se pudieron guardar los resultados:\n{e}")


    def cambiar_modo(self):
         """Cambia el modo y reinicia el examen."""
         nuevo_modo = self.mode_var.get()
         if nuevo_modo != self.modo_examen:
              if messagebox.askyesno("Cambiar Modo", f"Cambiar a modo '{nuevo_modo.replace('_',' ')}' reiniciará el examen actual.\n¿Continuar?"):
                   self.modo_examen = nuevo_modo
                   self.modo_label.config(text=f"Modo: {self.modo_examen.replace('_',' ')}")
                   self.reiniciar_examen(randomize=False) # Reiniciar ordenado por defecto al cambiar modo
              else:
                   # Restaurar selección del radio button al modo anterior
                   self.mode_var.set(self.modo_examen)


    def reiniciar_examen(self, randomize=False):
         """Limpia resultados y reinicia desde la primera pregunta."""
         self.indice_actual = 0
         self.resultados_examen = []
         self.preguntas_actuales = list(self.preguntas_originales) # Restaurar desde original
         if randomize:
              random.shuffle(self.preguntas_actuales)
         self.boton_siguiente.config(state="normal") # Reactivar botón
         self.mostrar_pregunta_actual()
         print("Examen reiniciado.") # Log a consola


    def abrir_archivo(self):
        """Abre un nuevo archivo de preguntas."""
        config = app_config.cargar_configuracion()
        initial_dir = os.path.dirname(config.get('ultima_ruta', '.'))
        nueva_ruta = filedialog.askopenfilename(
            title="Abrir Archivo de Preguntas",
            initialdir=initial_dir,
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if nueva_ruta and os.path.exists(nueva_ruta):
             # Cargar nuevas preguntas
             nuevas_preguntas = parser.cargar_preguntas(nueva_ruta)
             if nuevas_preguntas:
                  self.ruta_archivo = nueva_ruta
                  self.preguntas_originales = nuevas_preguntas
                  app_config.guardar_configuracion({'ultima_ruta': nueva_ruta})
                  self.root.title(f"Simulador de Examen - {os.path.basename(self.ruta_archivo)}")
                  self.reiniciar_examen(randomize=False) # Reiniciar con el nuevo archivo
             else:
                  messagebox.showerror("Error al Cargar", f"No se pudieron cargar preguntas válidas desde:\n{nueva_ruta}")


    def callback_despues_de_popup(self):
        """Se ejecuta después de cerrar CUALQUIER popup en modo paso_a_paso."""
        # 1. Avanza a la siguiente pregunta (esto actualiza self.indice_actual y la UI)
        self.ir_a_siguiente_pregunta()

        # 2. Rehabilita el botón 'Siguiente' SOLO si el examen no ha terminado
        #    (finalizar_examen ya deshabilita los botones permanentemente)
        if self.indice_actual < len(self.preguntas_actuales):
            self.boton_siguiente.config(state="normal")
            # El botón anterior se maneja dentro de mostrar_pregunta_actual o ir_a_siguiente
            # pero lo aseguramos aquí también por si acaso (solo relevante en modo examen)
            # self.boton_anterior.config(state="normal" if self.indice_actual > 0 and self.modo_examen == "examen_completo" else "disabled")
            # En paso a paso, el botón anterior no se usa, así que no lo tocamos aquí.

    # def ejecutar_diagnostico(self):
    #      """Ejecuta herramientas de diagnóstico (a implementar)."""
    #      # Aquí se podría abrir una nueva ventana o mostrar resultados en un messagebox
    #      messagebox.showinfo("Diagnóstico", "Función de diagnóstico aún no implementada en GUI.")


# --- Función de Arranque ---
def iniciar_gui(ruta_archivo:str, preguntas: list):
    root = tk.Tk()
    app = SimuladorExamenGUI(root, preguntas, ruta_archivo)
    root.mainloop()