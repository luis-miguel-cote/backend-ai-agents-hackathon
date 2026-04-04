from pathlib import Path
import docx
import PyPDF2
from core.progreso import progreso

def procesar_input(texto_libre: str = None, ruta_documento: str = None) -> str:
    contenido = ""
    if texto_libre:
        contenido = texto_libre
        progreso.actualizar_etapa("📝 Procesando input", f"{len(contenido)} caracteres")
    elif ruta_documento:
        progreso.actualizar_etapa("📄 Leyendo documento", ruta_documento)
        ext = Path(ruta_documento).suffix.lower()
        try:
            if ext == '.pdf':
                with open(ruta_documento, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    contenido = "\n".join([page.extract_text() for page in reader.pages])
            elif ext in ['.docx', '.doc']:
                doc = docx.Document(ruta_documento)
                contenido = "\n".join([para.text for para in doc.paragraphs])
            else:
                with open(ruta_documento, 'r', encoding='utf-8') as f:
                    contenido = f.read()
        except Exception as e:
            progreso.actualizar_etapa("❌ Error", str(e))
    return contenido
