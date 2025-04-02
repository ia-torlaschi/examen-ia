import tkinter as tk

def mostrar_popup_incorrecto(parent, pregunta, mensaje, on_close=None):
    """Muestra popup de error, con tamaño controlado y detalles en Text widget."""
    popup = tk.Toplevel(parent)
    popup.title("❌ Respuesta Incorrecta")
    popup.configure(bg="white")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.grab_set()

    # --- Icono y Mensaje Principal ---
    frame_top = tk.Frame(popup, bg="white")
    frame_top.pack(pady=(10, 5))
    icono = tk.Label(frame_top, text="❌", font=("Arial", 36), bg="white", fg="red")
    icono.pack(side="left", padx=(20, 10))
    label_titulo = tk.Label(frame_top, text="Incorrecto", font=("Arial", 16, "bold"), bg="white", fg="red")
    label_titulo.pack(side="left", anchor="center")

    # --- Mensaje con la respuesta del usuario ---
    # 'mensaje' ahora solo contiene "Tu respuesta: X,Y"
    label_tu_respuesta = tk.Label(popup, text=mensaje, font=("Arial", 10), bg="white", wraplength=400, justify="left")
    label_tu_respuesta.pack(pady=(0, 10), padx=20, fill="x")

    # --- Detalles de la Respuesta Correcta (en un Text widget) ---
    detail_frame = tk.Frame(popup, bg="#f0f0f0", bd=1, relief="sunken") # Marco para destacar
    detail_frame.pack(padx=20, pady=(0,10), fill="x")

    detail_title = tk.Label(detail_frame, text="Respuesta(s) Correcta(s):", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w")
    detail_title.pack(fill="x", padx=5, pady=(5,2))

    detalles_texto = [] # Lista de "A -> Opción Texto"
    for letra in sorted(pregunta.correctas):
        idx = ord(letra.upper()) - 65
        if 0 <= idx < len(pregunta.opciones):
            # Limitar longitud del texto de la opción para previsualización
            texto_opcion = pregunta.opciones[idx]
            if len(texto_opcion) > 100: # Ajusta este límite si es necesario
                texto_opcion = texto_opcion[:97] + "..."
            detalles_texto.append(f"{letra} → {texto_opcion}")

    # Calcular altura del Text widget (mínimo 1, máximo ~5 líneas)
    text_height = max(1, min(len(detalles_texto), 5))
    texto_details = tk.Text(detail_frame, height=text_height, wrap="word", font=("Arial", 9), padx=5, pady=5, relief="flat", bg="#f0f0f0")
    texto_details.insert("1.0", "\n".join(detalles_texto))
    texto_details.configure(state="disabled")
    texto_details.pack(fill="x", padx=5, pady=(0,5))


    # --- Botón OK y Cierre ---
    def cerrar_popup(event=None):
        if popup and popup.winfo_exists():
            popup.grab_release()
            popup.destroy()
            if on_close:
                on_close()
        elif on_close: # Asegurar llamada a on_close incluso si ya se cerró
             on_close()


    boton_ok = tk.Button(popup, text="OK", command=cerrar_popup, width=10)
    boton_ok.pack(pady=(5, 15))

    popup.bind("<Return>", cerrar_popup) # Cerrar con Enter también
    popup.focus_set() # Foco en el popup
    boton_ok.focus()  # Foco específico en el botón OK

    # --- Centrado ---
    popup.update_idletasks()
    popup_width = popup.winfo_width()
    popup_height = popup.winfo_height()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    position_x = parent_x + (parent_width // 2) - (popup_width // 2)
    position_y = parent_y + (parent_height // 2) - (popup_height // 2)
    # Ajustes básicos para que no se salga pantalla
    screen_width = parent.winfo_screenwidth(); screen_height = parent.winfo_screenheight()
    position_x = max(0, min(position_x, screen_width - popup_width))
    position_y = max(0, min(position_y, screen_height - popup_height))
    popup.geometry(f"+{position_x}+{position_y}")