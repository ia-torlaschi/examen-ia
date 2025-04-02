# ui/popup_correcto.py
import tkinter as tk

def mostrar_popup_correcto(parent, on_close=None):
    """
    Muestra una ventana emergente indicando que la respuesta es correcta.
    Se cierra automáticamente después de 1.5 segundos o con clic/Enter.

    Args:
        parent: La ventana Tkinter padre sobre la cual se mostrará el popup.
        on_close: Una función opcional que se llamará después de cerrar el popup.
                  Se usa típicamente para avanzar a la siguiente pregunta.
    """
    popup = tk.Toplevel(parent)
    popup.title("✅ Respuesta Correcta")
    popup.configure(bg="white")
    popup.resizable(False, False) # Evitar que se redimensione

    # Hacer que aparezca encima de otras ventanas
    popup.attributes("-topmost", True)
    # Capturar eventos para esta ventana (modalidad temporal)
    popup.grab_set()

    # --- Contenido del Popup ---
    label = tk.Label(popup, text="✅ Correcto", font=("Arial", 24, "bold"), bg="white", fg="green")
    label.pack(pady=20, padx=40)

    # --- Función de Cierre ---
    def cerrar(event=None):
        """Cierra el popup de forma segura y llama al callback."""
        # Verificar si el popup aún existe antes de intentar destruirlo
        # (Evita errores si se cierra manualmente justo cuando salta el 'after')
        if popup and popup.winfo_exists():
            popup.grab_release() # Liberar la captura de eventos
            popup.destroy()
            # Llamar al callback DESPUÉS de destruir la ventana
            if on_close:
                on_close()

    # --- Vinculación de Eventos ---
    # Permitir cerrar manualmente con clic en cualquier lugar del popup o presionando Enter
    popup.bind("<Button-1>", cerrar)
    popup.bind("<Return>", cerrar)
    # Poner el foco en el popup para que <Return> funcione inmediatamente
    popup.focus_set()

    # --- Cierre Automático ---
    # Programar la llamada a 'cerrar' después de 1500 milisegundos (1.5 segundos)
    # El identificador devuelto por 'after' podría usarse para cancelar el cierre si fuera necesario
    after_id = popup.after(1500, cerrar)

    # --- Centrado del Popup ---
    # Forzar la actualización de la ventana para obtener sus dimensiones reales
    popup.update_idletasks()

    # Obtener dimensiones del popup
    popup_width = popup.winfo_width()
    popup_height = popup.winfo_height()

    # Obtener dimensiones y posición de la ventana padre
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    # Calcular posición para centrar
    position_x = parent_x + (parent_width // 2) - (popup_width // 2)
    position_y = parent_y + (parent_height // 2) - (popup_height // 2)

    # Ajustar si se sale de la pantalla (básico)
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    if position_x + popup_width > screen_width: position_x = screen_width - popup_width
    if position_y + popup_height > screen_height: position_y = screen_height - popup_height
    if position_x < 0: position_x = 0
    if position_y < 0: position_y = 0

    # Aplicar la geometría calculada
    popup.geometry(f"+{position_x}+{position_y}")

    # Nota: No usamos parent.wait_window(popup) aquí porque
    # grab_set() ya maneja la modalidad y el cierre (manual o automático)
    # se encarga de devolver el control.

# --- Ejemplo de uso (si se ejecuta este archivo directamente) ---
if __name__ == '__main__':
    def mi_callback():
        print("Popup cerrado, ejecutando callback.")

    # Crear una ventana principal simple para probar
    root = tk.Tk()
    root.title("Ventana Principal de Prueba")
    root.geometry("400x300")

    # Botón para lanzar el popup
    test_button = tk.Button(root, text="Mostrar Popup Correcto",
                           command=lambda: mostrar_popup_correcto(root, mi_callback))
    test_button.pack(pady=50)

    root.mainloop()