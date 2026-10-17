import json
import requests

# Nombre de tu archivo JSON en el repositorio
ARCHIVO_JSON = "canales.json"

def verificar_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # Petición rápida para verificar si la transmisión responde
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
        # Si HEAD no funciona, intentamos un GET corto
        response = requests.get(url, headers=headers, timeout=5, stream=True)
        return response.status_code in [200, 301, 302]
    except Exception:
        return False

def procesar_canales():
    with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
        canales = json.load(f)

    print(f"Verificando {len(canales)} canales...")

    for canal in canales:
        nombre = canal.get("nombre", "Sin nombre")
        url = canal.get("url", "")

        activo = verificar_url(url)
        
        if activo:
            print(f"[OK] {nombre} está activo.")
        else:
            print(f"[CAÍDO] {nombre} no responde.")

    # Guardamos los cambios manteniendo el formato JSON limpio
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(canales, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    procesar_canales()