# scraper_streamt.py

import os
import re
import requests
try:
    import xbmc
except: 
    xbmc=""
import urllib.parse

try:
    from scrapers.merge_lists import unir_listas_m3u
except:
    from merge_lists import unir_listas_m3u
URL = "https://raw.githubusercontent.com/tvliveapp/channels/refs/heads/master/milista/canales.m3u"

#URL="https://raw.githubusercontent.com/tvliveapp/channels/refs/heads/master/milista/milista.m3u"

def obtener_ip():

    ip = xbmc.getInfoLabel(
        "Network.IPAddress"
    )

    if not ip:
        ip = "127.0.0.1"

    return ip

myIP=obtener_ip()
if myIP:
   myIP="http://"+myIP+":8090"
def obtener_html(url):

    try:
    
        respuesta = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        respuesta.raise_for_status()

        return respuesta.text
    
    except Exception as e:
        if xbmc:
            xbmc.log(
                f"Error obteniendo HTML StreamTP: {e}",
                xbmc.LOGERROR
            )

        return ""


def extraer_canales(html):

    canales = []

    bloque = re.search(
        r"const\s+channels\s*=\s*\{(.*?)\};",
        html,
        re.DOTALL
    )

    if not bloque:
        if xbmc:
            xbmc.log(
                "No se encontró la variable channels",
                xbmc.LOGERROR
            )

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
    if xbmc:
        xbmc.log(
            "Generando lista StreamTP",
            xbmc.LOGINFO
        )

    html = obtener_html(URL)

    if not html:
        if xbmc:
            xbmc.log(
                "HTML vacío",
                xbmc.LOGERROR
            )

        return

    archivo_streamtp = os.path.join(
        carpeta_listas,
        "canales.m3u"
    )
    if 1:
    #try:

        with open(
            archivo_streamtp,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html.replace("proxyIP",myIP))
        if xbmc:
            xbmc.log(
                f"Lista creada: {archivo_streamtp}",
                xbmc.LOGINFO
            )
    else:
    #except Exception as e:
        if xbmc:
            xbmc.log(
                f"Error guardando streamtp.m3u: {e}",
                xbmc.LOGERROR
            )

        return
    if 1:
    #try:

        contenido_unificado = unir_listas_m3u(
            carpeta_listas
        )

        archivo_unico = os.path.join(
            carpeta_listas,
            "unicalista.m3u"
        )

        with open(
            archivo_unico,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                contenido_unificado
            )
        if xbmc:
            xbmc.log(
                f"Lista unificada creada: {archivo_unico}",
                xbmc.LOGINFO
            )
            xbmc.executebuiltin("PVR.ReloadChannels")
    else:
    #except Exception as e:
        if xbmc:
            xbmc.log(
                f"Error creando unicalista.m3u: {e}",
                xbmc.LOGERROR
            )

