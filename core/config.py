# core/config.py
import json
import os

CONFIG_FILE = 'examen_config.json'
DEFAULT_RUTA_ARCHIVO = '50-finales-completo.txt' # Ajusta si tu archivo por defecto es otro

def cargar_configuracion():
    """Carga la configuración desde un archivo JSON."""
    config = {
        'ultima_ruta': DEFAULT_RUTA_ARCHIVO,
        'ultimo_modo_interfaz': 'gui', # 'gui' o 'cli'
        'ultimo_modo_examen_cli': '1' # Para el menú CLI
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_cargada = json.load(f)
                # Actualizar solo las claves que existen en el archivo y son esperadas
                for key in config:
                    if key in config_cargada:
                        config[key] = config_cargada[key]
        except Exception as e:
            print(f"[yellow]⚠️ Error al cargar la configuración: {e}. Usando valores por defecto.[/yellow]")

    return config

def guardar_configuracion(config_actualizada):
    """Guarda la configuración actualizada en un archivo JSON."""
    try:
        # Cargar primero la existente para no sobrescribir otras claves
        config_existente = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_existente = json.load(f)
            except Exception:
                pass # Ignorar errores al leer, se sobrescribirá

        # Fusionar la configuración existente con la actualizada
        config_final = {**config_existente, **config_actualizada}

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_final, f, indent=4) # Usar indent para legibilidad
    except Exception as e:
        print(f"[yellow]⚠️ No se pudo guardar la configuración: {e}[/yellow]")