import os


def unir_listas_m3u(carpeta):

    contenido_final = []


    # encabezado único
    contenido_final.append("#EXTM3U\n")


    for root, _, files in os.walk(carpeta):

        for file in files:
            print(file)

            if file.endswith(".m3u") and file.find("unicalista.m3u")==-1 :


                path = os.path.join(root, file)


                try:

                    with open(path, "r", encoding="utf-8") as f:

                        lines = f.readlines()


                        for line in lines:


                            line = line.strip()


                            if not line:

                                continue


                            # eliminar encabezados repetidos
                            if line.startswith("#EXTM3U"):
                                continue


                            contenido_final.append(line + "\n")



                except Exception as e:

                    print("Error leyendo lista:", file, e)


    
    return "".join(contenido_final)