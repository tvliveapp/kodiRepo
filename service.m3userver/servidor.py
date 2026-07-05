import os
import http.server
import socketserver

from urllib.parse import urlparse, parse_qs, unquote
from scrapers.playback import extraer_playback
from scrapers.merge_lists import unir_listas_m3u

import xbmc


PORT = 8090


class Handler(
    http.server.SimpleHTTPRequestHandler
):


    def __init__(
        self,
        *args,
        directory=None,
        **kwargs
    ):

        super().__init__(
            *args,
            directory=directory,
            **kwargs
        )

    import mimetypes
    def log_message(
        self,
        format,
        *args
    ):

        xbmc.log(
            format % args,
            xbmc.LOGINFO
        )



    def do_GET(self):

        ruta = urlparse(self.path)


        # ==========================
        # PROXY PERSONALIZADO
        # ==========================
        '''
        if ruta.path == "/unicalista.m3u":
            contenido = unir_listas_m3u(self.directory)
            self.send_response(200)
           
            self.send_header(
                "Content-Type",
                "application/vnd.apple.mpegurl"
            )

            self.end_headers()
            print(contenido)
            self.wfile.write(
                contenido.encode("utf-8")
            )
            return
        '''
        if ruta.path == "/proxy":


            parametros = parse_qs(
                ruta.query
            )


            url = parametros.get("url", [None])[0]
            if url:
                url = unquote(url)
            referer = parametros.get("referer", [None])[0]
            if referer:
                referer = unquote(referer)


            if url:


                xbmc.log(
                    "Extrayendo stream: " + url,
                    xbmc.LOGINFO
                )


                stream = extraer_playback(
                    url,referer
                )


                if stream:


                    xbmc.log(
                        "Stream encontrado: " + stream,
                        xbmc.LOGINFO
                    )


                    self.send_response(
                        302
                    )


                    self.send_header(
                        "Location",
                        stream
                    )


                    self.end_headers()

                    return



                else:


                    self.send_response(
                        404
                    )


                    self.send_header(
                        "Content-Type",
                        "text/plain"
                    )


                    self.end_headers()


                    self.wfile.write(
                        b"No se encontro stream"
                    )

                    return



        # ==========================
        # SERVIDOR NORMAL
        # ==========================

        super().do_GET()



def iniciar_servidor(carpeta):


    socketserver.TCPServer.allow_reuse_address = True


    with socketserver.TCPServer(
        ("", PORT),
        lambda *args, **kwargs:
            Handler(
                *args,
                directory=carpeta,
                **kwargs
            )

    ) as servidor:


        xbmc.log(
            f"Servidor HTTP activo puerto {PORT}",
            xbmc.LOGINFO
        )


        servidor.serve_forever()