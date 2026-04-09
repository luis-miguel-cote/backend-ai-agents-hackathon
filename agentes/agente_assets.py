import os
import re
import requests


def buscar_imagenes_pexels(query: str, per_page: int = 10) -> list:
    api_key = os.environ.get("PEXELS_API_KEY")

    if not api_key:
        print("⚠️ No se encontró PEXELS_API_KEY")
        return []

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": per_page}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        fotos = response.json().get("photos", [])
        return [foto["src"]["large"] for foto in fotos]

    except Exception as e:
        print(f"❌ Error en Pexels: {e}")
        return []


def buscar_imagenes_freepik(query: str, limit: int = 10) -> list:
    api_key = os.environ.get("FREEPIK_API_KEY")

    if not api_key:
        print("⚠️ No se encontró FREEPIK_API_KEY")
        return []

    url = "https://api.freepik.com/v1/resources"
    headers = {"x-freepik-api-key": api_key}
    params = {"term": query, "limit": limit}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json().get("data", [])
        return [img["image"]["source"]["url"] for img in data if "image" in img]

    except Exception as e:
        print(f"❌ Error en Freepik: {e}")
        return []


def buscar_imagenes(query: str, cantidad: int = 10) -> list:
    # 1️⃣ Intentar Pexels
    imagenes = buscar_imagenes_pexels(query, cantidad)

    if imagenes:
        print(f"✅ Pexels devolvió {len(imagenes)} imágenes")
        return imagenes

    # 2️⃣ Respaldo con Freepik
    print("🔄 Usando Freepik como respaldo...")
    imagenes = buscar_imagenes_freepik(query, cantidad)

    if imagenes:
        print(f"✅ Freepik devolvió {len(imagenes)} imágenes")
        return imagenes

    print("⚠️ No se encontraron imágenes en ninguna API")
    return []


def descargar_imagenes_proyecto(ruta_proyecto: str, descripcion: str):
    imagenes = buscar_imagenes(descripcion, cantidad=20)

    if not imagenes:
        print("⚠️ No se encontraron imágenes")
        return

    index_path = os.path.join(ruta_proyecto, "index.html")

    if not os.path.exists(index_path):
        print("⚠️ No existe index.html")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    rutas_unicas = []
    for ruta in re.findall(r'images/[^\"]+\.(?:jpg|png|jpeg)', html):
        if ruta not in rutas_unicas:
            rutas_unicas.append(ruta)

    for i, ruta in enumerate(rutas_unicas):
        if i < len(imagenes):
            html = html.replace(ruta, imagenes[i])

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"🖼️ Reemplazadas {len(rutas_unicas)} imágenes")