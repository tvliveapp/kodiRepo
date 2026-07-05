import re
import requests
import base64
#import xbmc

def decode_nested_atob(texto):
    # Extrae el contenido entre comillas
    m = re.search(r'"([^"]+)"', texto)
    if not m:
        return None

    dato = m.group(1)

    # Cuenta cuántos atob hay
    veces = len(re.findall(r'atob\s*\(', texto))

    # Decodifica tantas veces como sea necesario
    for _ in range(veces):
        dato = base64.b64decode(dato).decode("utf-8")
        pass
    return dato


def extraer_playback(url,referer="https://futbol-libres.su/"):
    
    try:
    
        r = requests.get(
            url,
            headers={
                "User-Agent":"Mozilla/5.0",
                "referer":referer
            },
            timeout=15
        )
        
        html = r.text

        print(html)
        patrones = [

            r'playbackURL\s*=\s*["\'](.*?)["\']',

            r'playbackUrl\s*=\s*["\'](.*?)["\']',

            r'sourceUrl\s*[:=]\s*["\'](.*?)["\']',
            r'var src\s*[:=]\s*["\'](.*?)["\']',
            r'playbackURL\s*=\s*(atob\s*\(.+?\));'
             

        ]


        for patron in patrones:

            m = re.search(
                patron,
                html,
                re.IGNORECASE
            )

            if m:
                
                
                m=m.group(1)
                
                if m.find("atob")>-1:
                    m=decode_nested_atob(m)
                return m.replace("\/", "/")



        # respaldo buscando cualquier m3u8

        m3u = re.search(
            r'https?://[^"\']+\.m3u8[^"\']*',
            html
        )


        if m3u:

            m3u=m3u.group(0)
            
            return m3u.replace("\/", "/")


    
    except Exception as e:

        print(
            "SCRAPER ERROR:",
            e
        )
    

    return None

#print(extraer_playback("https://latamvidzs.org/canal.php?stream=dsports","https://futbol-libres.su/"))

#print(extraer_playback("https://streamtpday1.xyz/global1.php?stream=espn","https://streamtpday1.xyz/"))
#print(extraer_playback("https://deportes.ksdjugfsddeports.com/stream.php?canal=goldenedge&target=1",""))
print(extraer_playback("https://deportes.ksdjugfsddeports.com/librefutbol3.php?stream=34_",""))
print("---------------------------------------------------------------------------------")