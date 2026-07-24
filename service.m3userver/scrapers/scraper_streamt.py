import os
import re
import requests
import urllib.parse

# Intentar cargar XBMC/Kodi para evitar fallos al ejecutar en PC
try:
    import xbmc
    from scrapers.merge_lists import unir_listas_m3u
except ImportError:
    # Si falla, creamos una clase espejo de XBMC para PC
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
    
    # Simulación de la función para que no rompa en PC
    def unir_listas_m3u(carpeta):
        return ""

URL = "https://streamtp99a.sbs/"

referer = urllib.parse.quote(
    "https://streamtpday1.xyz/"
)

def obtener_ip():
    try:
        ip = xbmc.getInfoLabel("Network.IPAddress")
    except:
        ip = ""
        
    if not ip:
        ip = "127.0.0.1"
    return ip

def obtener_html(url):
    try:
        respuesta = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        respuesta.raise_for_status()
        return respuesta.text
    except Exception as e:
        xbmc.log(f"Error obteniendo HTML StreamTP: {e}", xbmc.LOGERROR)
        return ""

def extraer_canales(html):
    canales = []
    bloque = re.search(
        r"const\s+channels\s*=\s*\{(.*?)\};",
        html,
        re.DOTALL
    )

    if not bloque:
        xbmc.log("No se encontró la variable channels", xbmc.LOGERROR)
        return canales

    items = re.findall(
        r"'([^']+)'\s*:\s*'([^']+)'",
        bloque.group(1)
    )

    for nombre, url in items:
        canales.append({
            "nombre": nombre.strip(),
            "url": url.strip()
        })
    return canales

def crear_lista(carpeta_listas):
    xbmc.log("Generando lista StreamTP", xbmc.LOGINFO)
    html = obtener_html(URL)

    if not html:
        xbmc.log("HTML vacío", xbmc.LOGERROR)
        return

    canales = extraer_canales(html)

    if not canales:
        xbmc.log("No se encontraron canales", xbmc.LOGERROR)
        return

    lista = "#EXTM3U\n"
    ip = obtener_ip()
    
    print("-------------------------------")
    print(f"IP Detectada: {ip}")
    
    for canal in canales:
        # Reemplazo de dominio base solicitado en tu script anterior
        url_limpia = canal["url"].replace("streamtp-x-y-z.ws", "streamtp.sbs")
        encoded = urllib.parse.quote(url_limpia)
    
        # Enlace estructurado para el Proxy de tu Addon (Kodi)
        proxy = (
            f"http://{ip}:8090/proxy?"
            f"url={encoded}"
            f"&referer={referer}"
        )
    
        # Combinamos soporte Kodi + VLC (Añadiendo parámetros EXTVLCOPT nativos)
        lista += (
            '#EXTINF:-1 '
            'group-title="StreamTP",'
            f'{canal["nombre"]}\n'
            f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\n'
            f'#EXTVLCOPT:http-referrer=https://streamtpday1.xyz/\n'
            f'{proxy}\n'
        )

    archivo_streamtp = os.path.join(carpeta_listas, "streamtp.m3u")

    try:
        with open(archivo_streamtp, "w", encoding="utf-8") as f:
            f.write(lista)
        xbmc.log(f"Lista creada: {archivo_streamtp}", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"Error guardando streamtp.m3u: {e}", xbmc.LOGERROR)
        return
    
    try:
        contenido_unificado = unir_listas_m3u(carpeta_listas)
        
        # Solo intentamos escribir la lista unificada si devolvió contenido real (Kodi)
        if contenido_unificado:
            archivo_unico = os.path.join(carpeta_listas, "unicalista.m3u")
            with open(archivo_unico, "w", encoding="utf-8") as f:
                f.write(contenido_unificado)

            xbmc.log(f"Lista unificada creada: {archivo_unico}", xbmc.LOGINFO)
            xbmc.executebuiltin("PVR.ReloadChannels")
    except Exception as e:
        xbmc.log(f"Error creando unicalista.m3u: {e}", xbmc.LOGERROR)

if __name__ == "__main__":
    # Definir la carpeta actual del script si se ejecuta directo en PC
    carpeta_destino = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
        
    print(f"[*] Ejecución directa detectada. Guardando lista en: {carpeta_destino}")
    
    # Ejecución local de la función
    crear_lista(carpeta_destino)
