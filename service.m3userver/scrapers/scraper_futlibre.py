#scraper_futlibre.py
import os
import re
import base64
import urllib.parse
import requests
import xbmc
from scrapers.merge_lists import unir_listas_m3u

URL = "https://futbol-libres.su/agenda/"
referer=urllib.parse.quote(
                "https://futbol-libres.su"
            )

def obtener_ip():

    ip = xbmc.getInfoLabel(
        "Network.IPAddress"
    )

    if not ip:
        ip = "127.0.0.1"

    return ip



def obtener_html(url, max_redirects=5):

    try:

        r = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )


        if r.status_code != 200:

            raise Exception(
                f"HTTP {r.status_code}"
            )


        return r.text


    except Exception as e:

        xbmc.log(
            f"Error HTML: {e}",
            xbmc.LOGERROR
        )

        return ""



def crear_lista(carpeta_listas):


    xbmc.log(
        "Generando lista Futbol Libre",
        xbmc.LOGINFO
    )


    html = obtener_html(URL)


    if not html:

        return



    ip = obtener_ip()



    lista = "#EXTM3U\n"



    regex_evento = (
        r'<li class="[^"]+">'
        r'([\s\S]*?)'
        r'</ul>\s*</li>'
    )


    eventos = re.findall(
        regex_evento,
        html
    )



    for bloque in eventos:


        evento = "Desconocido"

        hora = "??:??"



        nombre = re.search(
            r'<a href="#">([\s\S]*?)<span class="t">',
            bloque
        )


        hora_match = re.search(
            r'<span class="t">([^<]+)</span>',
            bloque
        )



        if nombre:

            evento = re.sub(
                r"\s+",
                " ",
                nombre.group(1)
            ).strip()



        if hora_match:

            hora = hora_match.group(1).strip()



        links = re.finditer(

            r'href="[^"]*\?r=([^"]+)"'
            r'[^>]*>([^<]+)'
            r'<span>([^<]+)</span>',

            bloque

        )



        for link in links:


            base64_url = link.group(1)

            canal = link.group(2).strip()

            calidad = link.group(3).strip()



            try:


                real = base64.b64decode(
                    base64_url
                ).decode(
                    "utf-8"
                )


            except:

                continue



            encoded = urllib.parse.quote(
                real
            )



            proxy = (
                f"http://{ip}:8090/proxy?"
                f"url={encoded}"
                f"&referer={referer}"
            )



            lista += (
                '#EXTINF:-1 '
                'group-title="eventos futbol libre",'
                f'({hora}) '
                f'{evento} - '
                f'{canal} '
                f'[{calidad}]\n'
                f'{proxy}\n'
            )
            



    archivo = os.path.join(
        carpeta_listas,
        "futlibreEV.m3u"
    )



    with open(
        archivo,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(lista)
    
    contenido = unir_listas_m3u(carpeta_listas)
    archivoUl = os.path.join(
        carpeta_listas,
        "unicalista.m3u"
    )
    with open(
        archivoUl,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(contenido)

    xbmc.log(
        f"Lista creada: {archivo}",
        xbmc.LOGINFO
    )
    xbmc.executebuiltin("PVR.ReloadChannels")
    