import os
import threading
import time

import xbmcgui
import xbmcaddon

import xbmc
import xbmcvfs

from servidor import iniciar_servidor

from instalar_modulos import instalar_dependencias


'''
from scrapers.scraper_web1 import ejecutar as web1
from scrapers.scraper_web2 import ejecutar as web2
from scrapers.scraper_web3 import ejecutar as web3
'''



ADDON_PATH = xbmcvfs.translatePath(
    "special://home/addons/service.m3userver"
)


LIB_PATH = os.path.join(
    ADDON_PATH,
    "resources",
    "lib"
)


if LIB_PATH not in sys.path:
    sys.path.insert(
        0,
        LIB_PATH
    )


USERDATA = xbmcvfs.translatePath(
    "special://userdata"
)

LISTAS = os.path.join(
    USERDATA,
    "listas"
)


if not xbmcvfs.exists(LISTAS):
    xbmcvfs.mkdirs(LISTAS)



monitor = xbmc.Monitor()


addon = xbmcaddon.Addon()


def obtener_ip():

    ip = xbmc.getInfoLabel(
        "Network.IPAddress"
    )

    if not ip:
        ip = "No disponible"

    return ip


ip=""
def actualizar_config():
    global ip
    ip = obtener_ip()

    addon.setSetting(
        "ip_local",
        ip
    )


actualizar_config()


addon = xbmcaddon.Addon()




puerto = "8090"




#dialog = xbmcgui.Dialog()






'''
dialog.textviewer(
    "Servidor Web M3U",
    mensaje
)
'''
def cerrar_dialogo():
    time.sleep(10)
    xbmc.executebuiltin("Action(Close)")
    xbmc.executebuiltin("Back")
    xbmc.executebuiltin("Dialog.Close(all)")


def iniciar_scraper(nombre, funcion, tiempo):

    def tarea():

        while not monitor.abortRequested():

            try:
                print("-----",funcion,"------")
                xbmc.log(
                    f"Ejecutando {nombre}",
                    xbmc.LOGINFO
                )

                funcion(LISTAS)


            except Exception as e:

                xbmc.log(
                    f"Error {nombre}: {e}",
                    xbmc.LOGERROR
                )


            if monitor.waitForAbort(tiempo):
                break



    threading.Thread(
        target=tarea,
        daemon=True
    ).start()



# ======================
# SERVIDOR HTTP
# ======================

threading.Thread(
    target=iniciar_servidor,
    args=(USERDATA,),
    daemon=True
).start()



# ======================
# SCRAPERS
# ======================
from scrapers.scraper_streamt import crear_lista as crear_streamtp


iniciar_scraper(
    "streamtp",
    crear_streamtp,
    3600
)


from scrapers.scraper_futlibre import crear_lista
iniciar_scraper(
    "Futbol Libre",
    crear_lista,
    7200
)

from scrapers.scraper_canales import crear_lista as crear_canales
iniciar_scraper(
    "Canales",
    crear_canales,
    21600
)

'''

iniciar_scraper(
    "SCRAPER WEB 3",
    web3,
    3600
)


'''
xbmc.log(
    "Servicio M3U iniciado",
    xbmc.LOGINFO
)


listas = []

for archivo in sorted(os.listdir(LISTAS)):
    if archivo.lower().endswith((".m3u", ".m3u8")):
        listas.append(f"http://{ip}:{puerto}/listas/{archivo}")





mensaje = "LISTAS DISPONIBLES\n\n"

if listas:
    mensaje += "\n".join(listas)
else:
    mensaje += "No se encontraron listas."
    
threading.Thread(target=cerrar_dialogo, daemon=True).start()


xbmcgui.Dialog().textviewer(
    "Servidor Web M3U",
    mensaje
)

while not monitor.abortRequested():

    monitor.waitForAbort(10)