import os
import requests
import urllib.parse
import re
import json

# Intentar cargar XBMC/Kodi
noXmbc=0
try:
    import xbmc
    from scrapers.merge_lists import unir_listas_m3u
except ImportError:
    noXmbc=1
    from merge_lists import unir_listas_m3u
    class XBMC:
        LOGINFO = "INFO"
        LOGERROR = "ERROR"

        @staticmethod
        def log(mensaje, nivel=None):
            print(f"[{nivel}] {mensaje}")

        @staticmethod
        def getInfoLabel(valor):
            if valor == "Network.IPAddress":
                return "127.0.0.1"
            return ""

        @staticmethod
        def executebuiltin(comando):
            print(f"[KODI] Ejecutando: {comando}")

    xbmc = XBMC()

# NUEVA URL: Ahora apunta al sitio principal o sección HTML donde están los scripts
URL = "https://streamtp.site/eventos.html" 
referer = urllib.parse.quote("https://streamtp.site/")

def obtener_ip():
    ip = ""
    try:
        ip = xbmc.getInfoLabel("Network.IPAddress")
    except:
        pass
    if not ip:
        ip = "127.0.0.1"
    return ip

def obtener_eventos_desde_html(url):
    """
    Descarga el HTML de la página y extrae mediante Regex 
    la estructura JSON contenida en la variable JavaScript 'EVENTS'.
    """
    try:
        respuesta = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        respuesta.raise_for_status()
        html_content = respuesta.text
        if noXmbc:
            print (html_content)
        # Expresión regular para capturar el contenido de var EVENTS = [ ... ];
        # Busca desde el corchete de apertura hasta el corchete de cierre del array
        match = re.search(r'var\s+EVENTS\s*=\s*(\[.*?\])\s*;', html_content, re.DOTALL)
        
        if match:
            json_texto = match.group(1)
            # Convertimos la cadena de texto JS estructurada a un objeto Python
            eventos = json.loads(json_texto)
            return eventos
        else:
            xbmc.log("No se encontró la variable 'EVENTS' en el código HTML.", xbmc.LOGERROR)
            return None

    except Exception as e:
        try:
            xbmc.log(f"Error obteniendo u obteniendo HTML de StreamHDX: {e}", xbmc.LOGERROR)
        except:
            pass
        return None

def extraer_eventos(eventos_js):
    """
    Procesa la nueva estructura de datos de la variable EVENTS 
    y la mapea al formato de canales compatible con tu generador M3U.
    """
    canales = []
    if not eventos_js:
        return canales

    try:
        for evento in eventos_js:
            titulo = evento.get("title", "Evento")
            fecha = evento.get("date", "Sin fecha")
            hora = evento.get("time", "")
            clase = evento.get("category", "Fútbol")

            # Iterar sobre las opciones/canales disponibles para este evento
            for opcion in evento.get("options", []):
                # Usar el ID u orden como identificador si el campo 'label' viene vacío
                label = opcion.get("label", "").strip()
                url_canal = opcion.get("url", "")

                if not label:
                    # Intenta extraer un nombre limpio del parámetro 'stream=' de la URL
                    parsed_url = urllib.parse.urlparse(url_canal)
                    queries = urllib.parse.parse_qs(parsed_url.query)
                    label = queries.get("stream", [f"Opción {opcion.get('order', 0)}"])[0].upper()

                if url_canal:
                    canales.append({
                        "nombre": f"{hora} | {titulo} | {label}",
                        "grupo": f"{fecha} - {clase}",
                        "url": url_canal
                    })

    except Exception as e:
        try:
            xbmc.log(f"Error procesando eventos extraídos de StreamHDX: {e}", xbmc.LOGERROR)
        except:
            pass
        
    return canales

def crear_lista(carpeta_listas):
    xbmc.log("Generando lista StreamHDX desde HTML", xbmc.LOGINFO)

    # Llamada al nuevo extractor basado en HTML/Regex
    datos_eventos = obtener_eventos_desde_html(URL)

    if not datos_eventos:
        xbmc.log("Lista de eventos vacía o error de parseo en StreamHDX", xbmc.LOGERROR)
        return

    canales = extraer_eventos(datos_eventos)

    if not canales:
        xbmc.log("No se encontraron eventos procesables en StreamHDX", xbmc.LOGERROR)
        return

    lista = "#EXTM3U\n"
    ip = obtener_ip()

    for canal in canales:
        encoded = urllib.parse.quote(canal["url"])
        proxy = (
            f"http://{ip}:8090/proxy?"
            f"url={encoded}"
            f"&referer={referer}"
            f"&scraper=streamhdx"
        )

        lista += (
            '#EXTINF:-1 '
            f'group-title="{canal["grupo"]}",'
            f'{canal["nombre"]}\n'
            f'{proxy}\n'
        )

    archivo_streamhdx = os.path.join(carpeta_listas, "streamhdx.m3u")

    try:
        with open(archivo_streamhdx, "w", encoding="utf-8") as f:
            f.write(lista)
        xbmc.log(f"Lista StreamHDX guardada con éxito en {archivo_streamhdx}", xbmc.LOGINFO)
    except Exception as e:
        try:
            xbmc.log(f"Error al guardar el archivo M3U: {e}", xbmc.LOGERROR)
        except:
            pass
if __name__ == "__main__":
    # Definir una carpeta por defecto donde guardar la lista si se ejecuta directamente
    carpeta_destino = os.path.join(os.path.dirname(__file__), "./")
    
    # Crear la carpeta si no existe para evitar errores de ruta
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
        
    print(f"[*] Ejecución directa detectada. Guardando lista en: {carpeta_destino}")
    
    # Llamar a la función principal
    crear_lista(carpeta_destino)
