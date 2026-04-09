from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime

def generar_log_pdf(logs, ruta_proyecto: Path):
    """Genera un PDF con el historial completo de logs del pipeline."""
    pdf_path = Path(ruta_proyecto) / "LOGS_PIPELINE.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=60, leftMargin=60, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="LogTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=HexColor("#1a1a2e"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="LogLine",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="LogTime",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#888888"),
        spaceAfter=10,
    ))
    elements = []
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("📝 Historial Completo del Pipeline", styles["LogTitle"]))
    elements.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["LogTime"]))
    elements.append(Spacer(1, 12))
    for log in logs:
        # Colorear según tipo de log
        color = "#222"
        if "error" in log.lower() or "❌" in log:
            color = "#c0392b"
        elif "completado" in log.lower() or "✅" in log:
            color = "#27ae60"
        elif "advertencia" in log.lower() or "⚠️" in log:
            color = "#f39c12"
        elif "generando" in log.lower() or "iniciando" in log.lower():
            color = "#2980b9"
        elif "descargando" in log.lower() or "assets" in log.lower():
            color = "#8e44ad"
        elif "qa" in log.lower():
            color = "#16a085"
        elif "devops" in log.lower():
            color = "#34495e"
        elif "documentación" in log.lower():
            color = "#2d3436"
        elements.append(Paragraph(f'<font color="{color}">{log}</font>', styles["LogLine"]))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Documento generado automáticamente por el Gemelo Digital", styles["LogTime"]))
    doc.build(elements)
    return str(pdf_path)
