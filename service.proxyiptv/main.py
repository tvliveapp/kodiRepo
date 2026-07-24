import xbmc
import time

# Código de inicialización de tu servidor proxy aquí

xbmc.log("[service.proxyiptv] Servicio Proxy IPTV Iniciado", xbmc.LOGINFO)

# Bucle principal para mantener el servicio activo en segundo plano
monitor = xbmc.Monitor()

while not monitor.abortRequested():
    # Aquí puedes colocar tareas repetitivas si las necesitas
    # O simplemente dejar que tu servidor web corra en un hilo separado
    time.sleep(1)

xbmc.log("[service.proxyiptv] Servicio Proxy IPTV Detenido", xbmc.LOGINFO)
