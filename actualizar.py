import json
import re
import requests

ARCHIVO_JSON = "canales.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extraer_de_tvabierta():
    """Extrae enlaces .m3u8 desde tvabierta.net"""
    urls = {}
    try:
        res = requests.get("https://tvabierta.net/", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            matches = re.findall(r'https?://[^\s<>"]+?\.m3u8[^\s<>"]*', res.text)
            for match in matches:
                if "tvabierta.net" in match or "ds.tvabierta.net" in match:
                    match_num = re.search(r'/0*(\d+)\.m3u8', match)
                    if match_num:
                        num = str(int(match_num.group(1)))
                        urls[num] = match
    except Exception as e:
        print(f"Error al rastrear tvabierta.net: {e}")
    return urls

def extraer_de_dominicanchannels():
    """Extrae enlaces .m3u8 desde dominicanchannels.com"""
    urls = {}
    try:
        res = requests.get("https://dominicanchannels.com/", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            # Rastrear coincidencias directas de listas HLS (.m3u8) en la página principal o iFrames
            matches = re.findall(r'https?://[^\s<>"]+?\.m3u8[^\s<>"]*', res.text)
            for match in matches:
                # Filtrar enlaces m3u8 limpios encontrados
                if "m3u8" in match:
                    # Mapeo según patrones comunes
                    urls["general"] = match
    except Exception as e:
        print(f"Error al rastrear dominicanchannels.com: {e}")
    return urls

def verificar_url(url):
    """Comprueba si la URL del streaming está activa."""
    try:
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        if res.status_code in [200, 301, 302]:
            return True
        res_get = requests.get(url, headers=HEADERS, timeout=5, stream=True)
        return res_get.status_code in [200, 301, 302]
    except Exception:
        return False

def procesar():
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            canales = json.load(f)
    except Exception as e:
        print(f"Error al abrir {ARCHIVO_JSON}: {e}")
        return

    print("Obteniendo enlaces de fuentes externas...")
    fuentes_tvabierta = extraer_de_tvabierta()
    fuentes_domchannels = extraer_de_dominicanchannels()

    print(f"Verificando {len(canales)} canales...")

    for canal in canales:
        nombre = canal.get("nombre", "Sin nombre")
        numero = str(canal.get("numero", ""))
        url_actual = canal.get("url", "")

        # 1. Intentar actualizar desde TVAbierta si coincide el número
        if numero in fuentes_tvabierta and fuentes_tvabierta[numero] != url_actual:
            print(f"[ACTUALIZADO] {nombre} obtuvo nueva URL desde TVAbierta.")
            canal["url"] = fuentes_tvabierta[numero]
            url_actual = canal["url"]

        # 2. Comprobar estado de la transmisión
        if verificar_url(url_actual):
            print(f"[OK] {nombre} activo.")
        else:
            print(f"[CAÍDO] {nombre} no responde.")

    # Guardar cambios
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(canales, f, ensure_ascii=False, indent=2)

    print("Proceso completado.")

if __name__ == "__main__":
    procesar()
