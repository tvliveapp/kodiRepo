#instalar_modulos.py
import sys
import subprocess
import xbmc


def instalar_paquete(paquete, modulo=None):

    if modulo is None:
        modulo = paquete


    try:

        __import__(modulo)

        xbmc.log(
            f"Modulo OK: {modulo}",
            xbmc.LOGINFO
        )

        return True


    except ImportError:


        xbmc.log(
            f"Instalando modulo: {paquete}",
            xbmc.LOGINFO
        )


        try:

            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    paquete
                ]
            )


            xbmc.log(
                f"Instalado: {paquete}",
                xbmc.LOGINFO
            )


            return True


        except Exception as e:


            xbmc.log(
                f"Error instalando {paquete}: {e}",
                xbmc.LOGERROR
            )


            return False



def instalar_dependencias():


    paquetes = [

        ("requests", "requests"),

        ("beautifulsoup4", "bs4")

    ]


    resultado = True


    for paquete, modulo in paquetes:

        if not instalar_paquete(
            paquete,
            modulo
        ):

            resultado = False



    return resultado