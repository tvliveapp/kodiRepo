# scraper_streamhdx.py

import os
import requests

import os
import requests
import urllib.parse

import re
import ast
import base64

import re
import ast
import base64
import requests






# Intentar cargar XBMC/Kodi


try:
    import xbmc
    from scrapers.merge_lists import unir_listas_m3u
except ImportError:
    from merge_lists import unir_listas_m3u
    class XBMC:

        LOGINFO = "INFO"
        LOGERROR = "ERROR"


        @staticmethod
        def log(mensaje, nivel=None):
            print(
                f"[{nivel}] {mensaje}"
            )


        @staticmethod
        def getInfoLabel(valor):

            if valor == "Network.IPAddress":
                return "127.0.0.1"

            return ""


        @staticmethod
        def executebuiltin(comando):

            print(
                f"[KODI] Ejecutando: {comando}"
            )


    xbmc = XBMC()
import urllib.parse


    

URL = "https://streamtp.site/eventos.json"


referer = urllib.parse.quote(
    "https://streamtp.site/"
)


def obtener_ip():
    ip=""
    try:
        ip = xbmc.getInfoLabel(
            "Network.IPAddress"
        )
    except:
        pass
    if not ip:
        ip = "127.0.0.1"

    return ip



def obtener_json(url):

    try:

        respuesta = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )

        respuesta.raise_for_status()

        return respuesta.json()


    except Exception as e:
        try:
            xbmc.log(
                f"Error obteniendo JSON StreamHDX: {e}",
                xbmc.LOGERROR
            )
        except:
            pass
        return None



def extraer_eventos(datos):

    canales = []


    try:

        for dia in datos.get("dias", []):

            fecha = dia.get(
                "fecha",
                "Sin fecha"
            )


            for evento in dia.get("eventos", []):

                titulo = evento.get(
                    "titulo",
                    "Evento"
                )

                clase = evento.get(
                    "clase",
                    "Eventos"
                )

                hora = evento.get(
                    "hora",
                    ""
                )


                for canal in evento.get("canales", []):

                    nombre = canal.get(
                        "nombre",
                        ""
                    )

                    url = canal.get(
                        "url",
                        ""
                    )


                    if url:

                        canales.append({

                            "nombre":
                            f"{hora} | {titulo} | {nombre}",

                            "grupo":
                            f"{fecha} - {clase}",

                            "url":
                            url
                        })


    except Exception as e:
        try:
            xbmc.log(
                f"Error procesando eventos StreamHDX: {e}",
                xbmc.LOGERROR
            )
        except:
            pass
        
    return canales




def crear_lista(carpeta_listas):


    xbmc.log(
        "Generando lista StreamHDX",
        xbmc.LOGINFO
    )


    datos = obtener_json(
        URL
    )


    if not datos:

        xbmc.log(
            "JSON vacío StreamHDX",
            xbmc.LOGERROR
        )

        return



    canales = extraer_eventos(
        datos
    )


    if not canales:

        xbmc.log(
            "No se encontraron eventos StreamHDX",
            xbmc.LOGERROR
        )

        return



    lista = "#EXTM3U\n"


    ip = obtener_ip()



    for canal in canales:


        encoded = urllib.parse.quote(
            canal["url"]
        )


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



    archivo_streamhdx = os.path.join(
        carpeta_listas,
        "streamhdx.m3u"
    )



    try:


        with open(
            archivo_streamhdx,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                lista
            )


        xbmc.log(
            f"Lista creada: {archivo_streamhdx}",
            xbmc.LOGINFO
        )


    except Exception as e:


        xbmc.log(
            f"Error guardando streamhdx.m3u: {e}",
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


        xbmc.executebuiltin(
            "PVR.ReloadChannels"
        )



    except Exception as e:


        xbmc.log(
            f"Error creando unicalista.m3u: {e}",
            xbmc.LOGERROR
        )
 
crear_lista("./")






pagina = "https://streamx-hd.com/live1.php?stream=espn3"
import re
import base64
import requests
from urllib.parse import urljoin


def extraer_playback(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Descargar página
    html = requests.get(url, headers=headers).text

    # Buscar JS externos
    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)',
        html
    )

    archivos_js = [html]

    for src in scripts:
        try:
            js_url = urljoin(url, src)
            js = requests.get(js_url, headers=headers).text
            archivos_js.append(js)
        except:
            pass


    for js in archivos_js:

        # Busca cualquier array:
        # nombre = [[numero,"base64"],[numero,"base64"]...]
        bloques = re.findall(
            r'(\w+)\s*=\s*(\[\s*\[\s*\d+\s*,\s*["\'][A-Za-z0-9+/=]+["\'].*?\]\s*\])\s*;',
            js,
            re.S
        )


        for nombre, array_txt in bloques:

            try:

                datos = eval(array_txt)

                # Solo arrays grandes
                if len(datos) < 40:
                    continue


                datos.sort(
                    key=lambda x:x[0]
                )


                # Buscar funciones return numero cerca del array
                pos = js.find(nombre)

                zona = js[pos:pos+6000]


                claves = re.findall(
                    r'function\s+\w+\s*\(\)\s*\{\s*return\s+(\d+)',
                    zona
                )


                if len(claves) < 2:
                    continue


                k = int(claves[0]) + int(claves[1])


                resultado = ""


                for item in datos:

                    valor = item[1]

                    dec = base64.b64decode(
                        valor
                    ).decode(
                        errors="ignore"
                    )

                    numero = int(
                        re.sub(
                            r"\D",
                            "",
                            dec
                        )
                    )

                    resultado += chr(
                        numero - k
                    )


                # Validar que parece URL
                if resultado.startswith(
                    ("http://","https://")
                ):
                    return resultado


            except Exception:
                continue


    return None



# ==========================
# USO
# ==========================
try:
    video = extraer_playback(pagina)
    print(video)
except:
    print("No video")