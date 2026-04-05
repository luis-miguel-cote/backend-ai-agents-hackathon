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


def descargar_imagenes_proyecto(ruta_proyecto: str, descripcion: str):
    imagenes = buscar_imagenes_pexels(descripcion, per_page=20)

    if not imagenes:
        print("⚠️ No se encontraron imágenes")
        return

    index_path = os.path.join(ruta_proyecto, "index.html")

    if not os.path.exists(index_path):
        print("⚠️ No existe index.html")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Busca TODAS las rutas locales de imágenes
    rutas_locales = re.findall(r'images/[^\"]+\.(jpg|png|jpeg)', html)

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