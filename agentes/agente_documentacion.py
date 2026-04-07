"""
Agente de Documentación: genera un PDF profesional con la documentación del proyecto.
"""

import io
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem,
)


def generar_documentacion_pdf(estado: dict, ruta_proyecto: Path, veredicto_qa: dict) -> str:
    """Genera un PDF de documentación profesional del proyecto.
    Retorna la ruta del PDF generado.
    """
    print("\n📄 Generando documentación PDF...")

    descripcion = estado.get("input_usuario", "Proyecto web")[:500]
    tipo = estado.get("tipo_proyecto", "landing_page")
    archivos = list(estado.get("archivos_generados", {}).keys())
    reqs = estado.get("requerimientos", {})

    pdf_path = ruta_proyecto / "DOCUMENTACION.pdf"
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=60, leftMargin=60,
        topMargin=50, bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    styles.add(ParagraphStyle(
        name="TituloDoc",
        parent=styles["Title"],
        fontSize=24,
        textColor=HexColor("#1a1a2e"),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Subtitulo",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=HexColor("#16213e"),
        spaceBefore=16,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="SeccionTitulo",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=HexColor("#0f3460"),
        spaceBefore=20,
        spaceAfter=10,
        borderWidth=1,
        borderColor=HexColor("#0f3460"),
        borderPadding=4,
    ))
    styles.add(ParagraphStyle(
        name="TextoNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Codigo",
        parent=styles["Code"],
        fontSize=9,
        backColor=HexColor("#f4f4f4"),
        borderWidth=1,
        borderColor=HexColor("#dddddd"),
        borderPadding=6,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Fecha",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#666666"),
        spaceAfter=20,
    ))

    elements = []

    # === PORTADA ===
    elements.append(Spacer(1, 80))
    elements.append(Paragraph("📋 Documentación del Proyecto", styles["TituloDoc"]))
    elements.append(HRFlowable(width="100%", color=HexColor("#0f3460"), thickness=2))
    elements.append(Spacer(1, 12))

    desc_corta = descripcion.split("\n")[0][:120] if descripcion else "Proyecto generado"
    elements.append(Paragraph(desc_corta, styles["Subtitulo"]))
    elements.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} | Tipo: {tipo}",
        styles["Fecha"],
    ))
    elements.append(Spacer(1, 20))

    # === 1. DESCRIPCIÓN DEL PROYECTO ===
    elements.append(Paragraph("1. Descripción del Proyecto", styles["SeccionTitulo"]))
    # Limpiar descripcion para evitar XML issues
    desc_limpia = descripcion.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for parrafo in desc_limpia.split("\n")[:10]:
        if parrafo.strip():
            elements.append(Paragraph(parrafo.strip(), styles["TextoNormal"]))

    # === 2. ESTRUCTURA DE ARCHIVOS ===
    elements.append(Paragraph("2. Estructura de Archivos", styles["SeccionTitulo"]))
    elements.append(Paragraph(
        "El proyecto contiene los siguientes archivos:",
        styles["TextoNormal"],
    ))

    tabla_archivos = [["Archivo", "Tipo", "Descripción"]]
    desc_archivos = {
        "index.html": ("HTML", "Página principal del sitio"),
        "css/styles.css": ("CSS", "Estilos y diseño responsive"),
        "js/main.js": ("JavaScript", "Interactividad y animaciones"),
        "README.md": ("Markdown", "Documentación técnica"),
        "vercel.json": ("JSON", "Configuración de despliegue Vercel"),
        ".env.example": ("ENV", "Variables de entorno de ejemplo"),
        "Dockerfile": ("Docker", "Configuración para contenedores"),
        "render.yaml": ("YAML", "Configuración de despliegue Render"),
        "DOCUMENTACION.pdf": ("PDF", "Este documento"),
    }
    for archivo in sorted(archivos):
        tipo_arch, desc_arch = desc_archivos.get(archivo, ("Otro", "Archivo del proyecto"))
        tabla_archivos.append([archivo, tipo_arch, desc_arch])

    t = Table(tabla_archivos, colWidths=[2.2 * inch, 1 * inch, 3.3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0f3460")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8f8f8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)

    # === 3. GUÍA DE PERSONALIZACIÓN ===
    elements.append(Paragraph("3. Guía de Personalización", styles["SeccionTitulo"]))

    elements.append(Paragraph("<b>Cambiar imágenes:</b>", styles["TextoNormal"]))
    items_img = [
        ListItem(Paragraph("Reemplazar los archivos en la carpeta <b>img/</b> (si existe) o agregar imágenes directamente", styles["TextoNormal"])),
        ListItem(Paragraph("En <b>index.html</b>, buscar las etiquetas <b>&lt;img src=\"...\"&gt;</b> y cambiar la ruta", styles["TextoNormal"])),
        ListItem(Paragraph("Usar imágenes optimizadas (WebP o JPG comprimido) para mejor rendimiento", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_img, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Cambiar colores:</b>", styles["TextoNormal"]))
    items_colores = [
        ListItem(Paragraph("Abrir <b>css/styles.css</b> y buscar la sección <b>:root</b> al inicio", styles["TextoNormal"])),
        ListItem(Paragraph("Modificar las variables CSS: <b>--primary</b>, <b>--secondary</b>, <b>--dark</b>, etc.", styles["TextoNormal"])),
        ListItem(Paragraph("Los cambios se aplican automáticamente en toda la página", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_colores, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Cambiar textos:</b>", styles["TextoNormal"]))
    items_textos = [
        ListItem(Paragraph("Editar directamente <b>index.html</b> con cualquier editor de texto", styles["TextoNormal"])),
        ListItem(Paragraph("Los títulos están en etiquetas <b>&lt;h1&gt;</b>, <b>&lt;h2&gt;</b>, etc.", styles["TextoNormal"])),
        ListItem(Paragraph("Los párrafos están en etiquetas <b>&lt;p&gt;</b>", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_textos, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Cambiar fuentes:</b>", styles["TextoNormal"]))
    items_fuentes = [
        ListItem(Paragraph("En <b>css/styles.css</b>, buscar el <b>@import</b> de Google Fonts al inicio", styles["TextoNormal"])),
        ListItem(Paragraph("Elegir una fuente en <b>fonts.google.com</b> y reemplazar la URL", styles["TextoNormal"])),
        ListItem(Paragraph("Cambiar <b>font-family</b> en el <b>body</b>", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_fuentes, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Cambiar el logo:</b>", styles["TextoNormal"]))
    items_logo = [
        ListItem(Paragraph("En <b>index.html</b>, buscar la clase <b>logo</b> dentro del <b>&lt;nav&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Si es texto, simplemente reemplazar el contenido", styles["TextoNormal"])),
        ListItem(Paragraph("Para usar una imagen como logo: reemplazar el texto por <b>&lt;img src=\"img/logo.png\" alt=\"Mi Logo\"&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Tamaño recomendado del logo: 150x50 píxeles en formato PNG con fondo transparente", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_logo, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Agregar una nueva sección:</b>", styles["TextoNormal"]))
    items_seccion = [
        ListItem(Paragraph("En <b>index.html</b>, copiar un bloque <b>&lt;section&gt;...&lt;/section&gt;</b> existente", styles["TextoNormal"])),
        ListItem(Paragraph("Pegarlo donde desee la nueva sección y cambiar el <b>id</b> (ej: id=\"nueva-seccion\")", styles["TextoNormal"])),
        ListItem(Paragraph("Modificar el título y contenido dentro de la sección", styles["TextoNormal"])),
        ListItem(Paragraph("Agregar un enlace en el menú de navegación: <b>&lt;li&gt;&lt;a href=\"#nueva-seccion\"&gt;Nueva Sección&lt;/a&gt;&lt;/li&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("El smooth scroll funcionará automáticamente con el nuevo enlace", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_seccion, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Agregar redes sociales:</b>", styles["TextoNormal"]))
    items_redes = [
        ListItem(Paragraph("En <b>index.html</b>, buscar el <b>&lt;footer&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Agregar enlaces con íconos: <b>&lt;a href=\"https://facebook.com/tu-pagina\"&gt;Facebook&lt;/a&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Para íconos visuales, usar Font Awesome: agregar en el &lt;head&gt; el CDN de Font Awesome", styles["TextoNormal"])),
        ListItem(Paragraph("Luego usar: <b>&lt;i class=\"fab fa-facebook\"&gt;&lt;/i&gt;</b>, <b>&lt;i class=\"fab fa-instagram\"&gt;&lt;/i&gt;</b>, etc.", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_redes, bulletType="bullet", start="•"))

    elements.append(Paragraph("<b>Modificar el formulario de contacto:</b>", styles["TextoNormal"]))
    items_form = [
        ListItem(Paragraph("En <b>index.html</b>, buscar la etiqueta <b>&lt;form&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Para agregar un campo: copiar una línea <b>&lt;input&gt;</b> y cambiar el <b>placeholder</b> y <b>type</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Tipos comunes: <b>text</b> (texto), <b>email</b> (correo), <b>tel</b> (teléfono), <b>number</b> (número)", styles["TextoNormal"])),
        ListItem(Paragraph("Para conectar el formulario a un servicio real, usar <b>Formspree.io</b>: cambiar <b>&lt;form&gt;</b> por <b>&lt;form action=\"https://formspree.io/f/TU_ID\" method=\"POST\"&gt;</b>", styles["TextoNormal"])),
        ListItem(Paragraph("Para eliminar un campo, simplemente borrar la línea <b>&lt;input&gt;</b> correspondiente", styles["TextoNormal"])),
    ]
    elements.append(ListFlowable(items_form, bulletType="bullet", start="•"))

    # === 4. CÓMO EJECUTAR ===
    elements.append(Paragraph("4. Cómo Ejecutar el Proyecto", styles["SeccionTitulo"]))
    elements.append(Paragraph("<b>Opción 1 — Abrir directamente:</b>", styles["TextoNormal"]))
    elements.append(Paragraph("Hacer doble clic en <b>index.html</b> para abrir en el navegador.", styles["TextoNormal"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>Opción 2 — Servidor local:</b>", styles["TextoNormal"]))
    elements.append(Paragraph("python -m http.server 8000", styles["Codigo"]))
    elements.append(Paragraph("Luego abrir <b>http://localhost:8000</b> en el navegador.", styles["TextoNormal"]))

    # === 5. DESPLIEGUE ===
    elements.append(Paragraph("5. Despliegue (Deploy)", styles["SeccionTitulo"]))
    if tipo == "landing_page":
        elements.append(Paragraph(
            "El proyecto incluye <b>vercel.json</b> para despliegue rápido en Vercel:",
            styles["TextoNormal"],
        ))
        pasos_deploy = [
            ListItem(Paragraph("Crear cuenta en <b>vercel.com</b>", styles["TextoNormal"])),
            ListItem(Paragraph("Subir el proyecto a un repositorio de GitHub", styles["TextoNormal"])),
            ListItem(Paragraph("Importar el repositorio en Vercel", styles["TextoNormal"])),
            ListItem(Paragraph("El sitio estará en línea automáticamente", styles["TextoNormal"])),
        ]
        elements.append(ListFlowable(pasos_deploy, bulletType="1", start="1"))
    else:
        elements.append(Paragraph(
            "El proyecto incluye archivos de configuración para despliegue en la nube.",
            styles["TextoNormal"],
        ))

    # === 6. QA ===
    if veredicto_qa and veredicto_qa.get("verdict") != "SKIPPED":
        elements.append(Paragraph("6. Resultado de Calidad (QA)", styles["SeccionTitulo"]))
        elements.append(Paragraph(
            f"Veredicto: <b>{veredicto_qa.get('verdict', 'N/A')}</b>",
            styles["TextoNormal"],
        ))
        elements.append(Paragraph(
            f"Tasa de aprobación: <b>{veredicto_qa.get('pass_rate', 0)}%</b>",
            styles["TextoNormal"],
        ))
        if veredicto_qa.get("warnings"):
            elements.append(Paragraph("<b>Observaciones:</b>", styles["TextoNormal"]))
            for w in veredicto_qa["warnings"][:5]:
                elements.append(Paragraph(f"⚠️ {w}", styles["TextoNormal"]))

    # === PIE ===
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", color=HexColor("#cccccc"), thickness=1))
    elements.append(Paragraph(
        f"Documento generado automáticamente por el Gemelo Digital — {datetime.now().strftime('%Y')}",
        styles["Fecha"],
    ))

    doc.build(elements)
    print(f"   📄 PDF generado: {pdf_path}")
    return str(pdf_path)
