
ENTRADA = "tvp.m3u"
SALIDA = "lista_nueva.m3u"

with open(ENTRADA, "r", encoding="utf-8") as f:
    lineas = f.readlines()
fo=open( SALIDA,"w",encoding="utf-8")
for linea in lineas:
    print (linea)
    fo.write(linea.replace("%2Ftvporinternet","%2Flibrefutbol"))
    
fo.close()

