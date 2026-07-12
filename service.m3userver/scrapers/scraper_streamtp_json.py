# scraper_streamtp_json.py

import os
import requests

import urllib.parse



URL = "https://streamtp.sbs/wc.json"


referer = urllib.parse.quote(
    "https://streamtp.sbs/"
)




# Compatibilidad fuera de Kodi
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
                f"[KODI] {comando}"
            )


    xbmc = XBMC()
def obtener_ip():

    ip = xbmc.getInfoLabel(
        "Network.IPAddress"
    )

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
                "Mozilla/5.0"
            }
        )

        respuesta.raise_for_status()

        return respuesta.json()


    except Exception as e:

        xbmc.log(
            f"Error obteniendo JSON StreamTP: {e}",
            xbmc.LOGERROR
        )

        return None



def extraer_canales(datos):

    canales = []


    try:

        for evento in datos.get(
            "events",
            []
        ):


            titulo = evento.get(
                "title",
                "Evento"
            )


            categoria = evento.get(
                "category",
                "Eventos"
            )


            hora = evento.get(
                "time",
                ""
            )



            for link in evento.get(
                "links",
                []
            ):


                url = link.get(
                    "url",
                    ""
                )


                if not url:
                    continue



                bitrate = link.get(
                    "bitrate",
                    ""
                )

                DRM=""
                # Agregar DRM=true solamente a DRM
                if bitrate.upper() == "DRM":
                    DRM=" | DRM"
                    if "?" in url:
                        url += "&DRM=true"

                    else:
                        url += "?DRM=true"



                server = link.get(
                    "server",
                    "Stream"
                )


                calidad = link.get(
                    "quality",
                    {}
                ).get(
                    "label",
                    ""
                )



                canales.append({

                    "nombre":
                    f"{hora} | {titulo} | {server} {calidad}{DRM}",

                    "grupo":"streamtp.sbs",
                    

                    "url":
                    url

                })


    except Exception as e:

        xbmc.log(
            f"Error procesando StreamTP JSON: {e}",
            xbmc.LOGERROR
        )


    return canales




def crear_lista(carpeta_listas):


    xbmc.log(
        "Generando lista StreamTP JSON",
        xbmc.LOGINFO
    )



    datos = obtener_json(
        URL
    )


    if not datos:

        return



    canales = extraer_canales(
        datos
    )


    if not canales:

        xbmc.log(
            "No hay canales StreamTP",
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
        )



        lista += (

            '#EXTINF:-1 '
            f'group-title="{canal["grupo"]}",'
            f'{canal["nombre"]}\n'
            f'{proxy}\n'

        )



    archivo = os.path.join(
        carpeta_listas,
        "streamtpsbs.m3u"
    )



    try:


        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                lista
            )


        xbmc.log(
            f"Lista creada: {archivo}",
            xbmc.LOGINFO
        )



    except Exception as e:


        xbmc.log(
            f"Error guardando streamtp.m3u: {e}",
            xbmc.LOGERROR
        )

        return




    try:


        contenido = unir_listas_m3u(
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
                contenido
            )


        xbmc.log(
            "Lista unificada creada",
            xbmc.LOGINFO
        )


        xbmc.executebuiltin(
            "PVR.ReloadChannels"
        )


    except Exception as e:


        xbmc.log(
            f"Error unificando listas: {e}",
            xbmc.LOGERROR
        )
        
if __name__ == "__main__":

    carpeta = "./"

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)


    crear_lista(
        carpeta
    )