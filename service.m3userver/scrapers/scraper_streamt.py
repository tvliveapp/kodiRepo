# scraper_streamt.py

import os
import re
import requests
import xbmc
import urllib.parse
from scrapers.merge_lists import unir_listas_m3u
#https://streamtp.sbs/wc.json
#https://streamhdx.com/eventos.json

URL = "https://streamtp.sbs/"

referer=urllib.parse.quote(
                "https://streamtpday1.xyz/"
            )

def obtener_ip():

    ip = xbmc.getInfoLabel(
        "Network.IPAddress"
    )

    if not ip:
        ip = "127.0.0.1"

    return ip

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

    xbmc.log(
        "Generando lista StreamTP",
        xbmc.LOGINFO
    )

    html = obtener_html(URL)

    if not html:

        xbmc.log(
            "HTML vacío",
            xbmc.LOGERROR
        )

        return

    canales = extraer_canales(html)

    if not canales:

        xbmc.log(
            "No se encontraron canales",
            xbmc.LOGERROR
        )

        return

    lista = "#EXTM3U\n"
   
    ip = obtener_ip()
    
    
    print("-------------------------------")
    print(ip)
    for canal in canales:
        encoded = urllib.parse.quote(
                canal["url"].replace("streamtp-x-y-z.ws","streamtp.sbs")
            )
    
        proxy = (
                f"http://{ip}:8090/proxy?"
                f"url={encoded}"
                f"&referer={referer}"
            )
    
        lista += (
            '#EXTINF:-1 '
            'group-title="StreamTP",'
            f'{canal["nombre"]}\n'
            f'{proxy}\n'
        )

    archivo_streamtp = os.path.join(
        carpeta_listas,
        "streamtp.m3u"
    )

    try:

        with open(
            archivo_streamtp,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(lista)

        xbmc.log(
            f"Lista creada: {archivo_streamtp}",
            xbmc.LOGINFO
        )

    except Exception as e:

        xbmc.log(
            f"Error guardando streamtp.m3u: {e}",
            xbmc.LOGERROR
        )

        return
    
    try:

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

        xbmc.log(
            f"Lista unificada creada: {archivo_unico}",
            xbmc.LOGINFO
        )
        xbmc.executebuiltin("PVR.ReloadChannels")
    except Exception as e:

        xbmc.log(
            f"Error creando unicalista.m3u: {e}",
            xbmc.LOGERROR
        )
    