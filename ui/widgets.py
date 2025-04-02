# widgets.py
# Componentes reutilizables para interfaces Tkinter (plantilla base)

import tkinter as tk

def crear_boton(parent, texto, comando, color="lightblue"):
    return tk.Button(parent, text=texto, command=comando, bg=color, font=("Arial", 10), padx=10, pady=5)

def crear_titulo(parent, texto):
    return tk.Label(parent, text=texto, font=("Arial", 14, "bold"), pady=10)

def crear_checkbox(parent, texto, variable):
    return tk.Checkbutton(parent, text=texto, variable=variable, anchor="w", justify="left", wraplength=700)
