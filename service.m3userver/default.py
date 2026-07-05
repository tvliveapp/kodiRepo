import xbmc
import xbmcgui
import xbmcplugin
import sys
import xbmcvfs
import os
import xbmcaddon
import urllib.parse

addon = xbmcaddon.Addon()

PLUGIN_HANDLE = int(sys.argv[1])

USERDATA = xbmcvfs.translatePath("special://userdata")
LISTAS = os.path.join(USERDATA, "listas")


# ==========================
# IP LOCAL
# ==========================
def obtener_ip():
    ip = xbmc.getInfoLabel("Network.IPAddress")
    return ip if ip else "No detectada"


ip = obtener_ip()
puerto = addon.getSetting("puerto") or "8090"


# ==========================
# OBTENER LISTAS
# ==========================
def obtener_listas():
    if not os.path.exists(LISTAS):
        return []

    return [
        f for f in sorted(os.listdir(LISTAS))
        if f.lower().endswith((".m3u", ".m3u8"))
    ]


# ==========================
# PARSE M3U
# ==========================
def parse_m3u(file_path):
    canales = []

    if not os.path.exists(file_path):
        return canales

    nombre = None

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if line.startswith("#EXTINF"):
                nombre = line.split(",")[-1].strip()

            elif line and not line.startswith("#"):
                canales.append({
                    "name": nombre or line,
                    "url": line
                })
                nombre = None

    return canales


# ==========================
# MOSTRAR CANALES
# ==========================
def mostrar_canales(file):

    ruta = os.path.join(LISTAS, file)

    canales = parse_m3u(ruta)

    if not canales:
        xbmcgui.Dialog().textviewer(
            "Lista vacía",
            "No se encontraron canales"
        )
        return

    for c in canales:

        item = xbmcgui.ListItem(label=c["name"])

        item.setInfo("video", {
            "title": c["name"],
            "plot": c["url"]
        })

        item.setProperty("IsPlayable", "true")

        xbmcplugin.addDirectoryItem(
            handle=PLUGIN_HANDLE,
            url=c["url"],
            listitem=item,
            isFolder=False
        )


# ==========================
# ROUTER
# ==========================
params = urllib.parse.parse_qs(sys.argv[2][1:]) if len(sys.argv) > 2 else {}

action = params.get("action", [""])[0]
file = params.get("file", [""])[0]


# ▶ CANALES DIRECTO
if action == "channels" and file:
    mostrar_canales(file)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
    raise SystemExit


# ==========================
# SERVIDOR ROOT
# ==========================
item = xbmcgui.ListItem(label="Servidor M3U Activo")

item.setInfo("video", {
    "plot": f"""
IP: {ip}
Puerto: {puerto}
URL: http://{ip}:{puerto}/
Estado: ONLINE
""",
    "genre": "Servidor IPTV",
    "studio": "Local"
})

xbmcplugin.addDirectoryItem(
    handle=PLUGIN_HANDLE,
    url="",
    listitem=item,
    isFolder=False
)


# ==========================
# LISTAS (ENTER → CANALES)
# ==========================
listas = obtener_listas()

for lista in listas:

    url_http = f"http://{ip}:{puerto}/listas/{lista}"
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url_http}"

    item = xbmcgui.ListItem(label=lista)

    item.setInfo("video", {
        "plot": f"Lista IPTV\nArchivo: {lista}\nURL: {url_http}",
        "genre": "Lista M3U",
        "studio": "IPTV Local"
    })

    item.setArt({
        "thumb": qr
    })

    # ✔ ENTER DIRECTO A CANALES
    url = f"plugin://service.m3userver/?action=channels&file={lista}"

    xbmcplugin.addDirectoryItem(
        handle=PLUGIN_HANDLE,
        url=url,
        listitem=item,
        isFolder=True
    )


xbmcplugin.endOfDirectory(PLUGIN_HANDLE)