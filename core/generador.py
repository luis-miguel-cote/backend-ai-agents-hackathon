import re
import time
from core.progreso import progreso
from core.llm import llamar_llm


def _llamar_llm(prompt: str) -> str:
    return llamar_llm(prompt, temperature=0.7, agente="generador")


def _reparar_html(html: str) -> str:
    """Asegura que el HTML generado sea completo y tenga cabeza, viewport y enlaces."""
    html = html.strip()
    if not html:
        return html

    if "<!doctype html>" not in html.lower():
        html = "<!DOCTYPE html>\n" + html

    if "<html" not in html.lower():
        html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n<html lang=\"es\">\n", 1)
        if "</html>" not in html.lower():
            html = html + "\n</html>"
    elif "</html>" not in html.lower():
        html += "\n</html>"

    if "<head" not in html.lower():
        if "<html" in html.lower():
            html = re.sub(
                r'(<html[^>]*>)',
                r"\1\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Proyecto web</title>\n    <link rel=\"stylesheet\" href=\"css/styles.css\">\n</head>",
                html,
                flags=re.IGNORECASE,
                count=1,
            )
        else:
            html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Proyecto web</title>\n    <link rel=\"stylesheet\" href=\"css/styles.css\">\n</head>\n", 1)

    if "<body" not in html.lower():
        if "</head>" in html.lower():
            html = re.sub(r'(</head>)', r"\1\n<body>\n", html, flags=re.IGNORECASE, count=1)
        else:
            html = html.replace("</html>", "<body>\n</body>\n</html>")

    if "</body>" not in html.lower():
        if "</html>" in html.lower():
            html = re.sub(r'(</html>)', r"</body>\n\1", html, flags=re.IGNORECASE, count=1)
        else:
            html += "\n</body>"

    if "<meta charset" not in html.lower():
        html = re.sub(
            r'(<head[^>]*>)',
            r"\1\n    <meta charset=\"UTF-8\">",
            html,
            flags=re.IGNORECASE,
            count=1,
        )
    if "name=\"viewport\"" not in html.lower() and "name='viewport'" not in html.lower():
        html = re.sub(
            r'(<head[^>]*>)',
            r"\1\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            html,
            flags=re.IGNORECASE,
            count=1,
        )
    if "<title" not in html.lower():
        html = re.sub(
            r'(<head[^>]*>)',
            r"\1\n    <title>Proyecto web</title>",
            html,
            flags=re.IGNORECASE,
            count=1,
        )

    if "css/styles.css" not in html.lower():
        if "</head>" in html.lower():
            html = re.sub(r'(</head>)', r'    <link rel="stylesheet" href="css/styles.css">\n\1', html, flags=re.IGNORECASE, count=1)
        elif "<head" in html.lower():
            html = re.sub(r'(<head[^>]*>)', r"\1\n    <link rel=\"stylesheet\" href=\"css/styles.css\">", html, flags=re.IGNORECASE, count=1)

    if "js/main.js" not in html.lower():
        if "</body>" in html.lower():
            html = re.sub(r'(</body>)', r'    <script src="js/main.js"></script>\n\1', html, flags=re.IGNORECASE, count=1)
        elif "</html>" in html.lower():
            html = re.sub(r'(</html>)', r'    <script src="js/main.js"></script>\n</body>\n\1', html, flags=re.IGNORECASE, count=1)
        else:
            html += "\n    <script src=\"js/main.js\"></script>"

    if "</html>" not in html.lower():
        html += "\n</html>"

    return html


def generar_archivo_individual(ruta: str, descripcion: str, tipo: str, sistema_aprendizaje, archivos_previos: dict = None) -> str:
    """Genera contenido con prompts especificos para mejor calidad.
    archivos_previos: dict con archivos ya generados (ej: {"index.html": "<html>..."})
    para que CSS/JS usen las mismas clases del HTML.
    """
    progreso.iniciar_generacion_archivo(ruta)
    time.sleep(0.3)
    contexto = sistema_aprendizaje.obtener_contexto_aprendizaje(descripcion)
    if archivos_previos is None:
        archivos_previos = {}

    html_generado = archivos_previos.get("index.html", "")

    if ruta == "index.html":
        prompt = f"""Eres un disenador web EXPERTO. Genera un HTML COMPLETO y PROFESIONAL.

DESCRIPCION DEL PROYECTO:
{descripcion[:400]}

{contexto}

REQUISITO ABSOLUTAMENTE OBLIGATORIO:
1. Debes generar el HTML COMPLETO desde <!DOCTYPE html> hasta </html>
2. Usa la estructura SEMANTICA: <header>, <nav>, <main>, <section>, <footer>
3. Los estilos DEBEN estar enlazados con: <link rel="stylesheet" href="css/styles.css">
4. El JavaScript DEBE estar enlazado con: <script src="js/main.js"></script>
5. NO incluir CSS dentro del HTML (ni <style>)
6. NO incluir explicaciones, SOLO el codigo HTML
7. Diseno MODERNO con paleta de colores atractiva
8. Incluye clases CSS para todos los elementos

Genera SOLO el HTML:"""
        contenido = _llamar_llm(prompt)
        if not contenido:
            print("    LLM no disponible, usando plantilla de respaldo...")
            contenido = _obtener_plantilla_respaldo(ruta, descripcion)
        else:
            html_match = re.search(r'<!DOCTYPE html>.*?</html>', contenido, re.DOTALL | re.IGNORECASE)
            if html_match:
                contenido = html_match.group(0)
            contenido = _reparar_html(contenido)
            if "<html" not in contenido.lower() or "<head" not in contenido.lower() or "<body" not in contenido.lower() or "</html>" not in contenido.lower():
                print("    HTML incompleto, usando plantilla de respaldo...")
                contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    elif ruta == "css/styles.css":

        # Extraer clases del HTML para que el CSS las use
        clases_html = ""
        if html_generado:
            clases_encontradas = re.findall(r'class="([^"]+)"', html_generado)
            clases_unicas = sorted(set(" ".join(clases_encontradas).split()))
            clases_html = f"\n\nCLASES CSS USADAS EN EL HTML (debes estilizar TODAS estas):\n{', '.join('.' + c for c in clases_unicas)}"

        prompt = f"""Eres un disenador CSS EXPERTO. Genera CSS COMPLETO y PROFESIONAL.

DESCRIPCION:
{descripcion[:300]}

{contexto}
{clases_html}

{"HTML DE REFERENCIA (usa EXACTAMENTE estas clases):" if html_generado else ""}
{html_generado[:2000] if html_generado else ""}

REQUISITOS OBLIGATORIOS:
1. Estiliza TODAS las clases que aparecen en el HTML
2. Diseno RESPONSIVE con media queries (mobile-first: 768px, 1024px)
3. Variables CSS con :root para colores segun la descripcion del usuario
4. Usa CSS Grid y/o Flexbox para layouts
5. Efectos HOVER en botones, cards y enlaces
6. Animaciones suaves (transitions)
7. Tipografia moderna con Google Fonts (@import al inicio)
8. NO incluir bloques de codigo markdown (sin ```)
9. NO incluir explicaciones, SOLO CSS puro

Genera SOLO el CSS:"""
        contenido = _llamar_llm(prompt)
        if not contenido:
            print("    LLM no disponible, usando plantilla respaldo...")
            contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    elif ruta == "js/main.js":
        # Extraer IDs y clases del HTML para JS preciso
        ids_html = ""
        if html_generado:
            ids_encontrados = re.findall(r'id="([^"]+)"', html_generado)
            if ids_encontrados:
                ids_html = f"\n\nIDs EN EL HTML: {', '.join('#' + i for i in ids_encontrados)}"

        prompt = f"""Genera JavaScript INTERACTIVO para:

{descripcion[:300]}
{ids_html}

{"HTML DE REFERENCIA (usa los selectores exactos de este HTML):" if html_generado else ""}
{html_generado[:1500] if html_generado else ""}

REQUISITOS:
1. Smooth scroll para navegacion usando los IDs del HTML
2. Validacion de formulario (si existe form en el HTML)
3. Menu hamburguesa para movil (toggle de clase 'active')
4. Animaciones al hacer scroll (IntersectionObserver)
5. NO jQuery, solo Vanilla JS
6. Codigo dentro de DOMContentLoaded
7. NO incluir bloques de codigo markdown (sin ```)

Genera SOLO el JavaScript:"""
        contenido = _llamar_llm(prompt)
        if not contenido:
            print("    LLM no disponible, usando plantilla respaldo...")
            contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    elif ruta == "README.md":
        prompt = f"""Genera README.md profesional para:
{descripcion[:300]}

Incluye: titulo, descripcion, tecnologias, instalacion, uso, estructura del proyecto.

Genera SOLO markdown:"""
        contenido = _llamar_llm(prompt)
        if not contenido:
            print("    LLM no disponible, usando plantilla respaldo...")
            contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    else:
        prompt = f"""Genera el contenido del archivo '{ruta}' para el proyecto:
{descripcion[:300]}

Genera SOLO el codigo, sin explicaciones:"""
        contenido = _llamar_llm(prompt)
        if not contenido:
            print("    LLM no disponible, usando plantilla respaldo...")
            contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    # Limpiar bloques markdown (```css, ```js, ```html, etc.)
    contenido = contenido.strip()
    contenido = re.sub(r'^\s*```\w*\s*\n', '', contenido)
    contenido = re.sub(r'\n\s*```\s*$', '', contenido)
    contenido = contenido.strip()

    # Validar contenido minimo
    if not contenido or len(contenido.strip()) < 100:
        print(f"     Contenido muy corto, usando plantilla de respaldo")
        contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    # Validacion especifica para CSS
    if ruta == "css/styles.css":
        if ":root" not in contenido or "media" not in contenido:
            print(f"    Mejorando CSS con colores y responsive...")
            contenido = _obtener_plantilla_respaldo(ruta, descripcion)

    # Validar enlace a CSS en HTML
    if ruta == "index.html" and "css/styles.css" not in contenido:
        print(f"    Corrigiendo enlace a CSS...")
        contenido = contenido.replace('</head>', '<link rel="stylesheet" href="css/styles.css">\n</head>')

    preview = contenido[:100].replace('\n', ' ')
    progreso.completar_archivo(ruta, len(contenido), preview)
    return contenido


def _obtener_plantilla_respaldo(ruta: str, descripcion: str) -> str:
    """Plantillas de respaldo de alta calidad."""
    if ruta == "index.html":
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{descripcion[:40]}</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <div class="logo">{descripcion[:25]}</div>
            <ul class="nav-links">
                <li><a href="#inicio">Inicio</a></li>
                <li><a href="#productos">Productos</a></li>
                <li><a href="#galeria">Galeria</a></li>
                <li><a href="#contacto">Contacto</a></li>
            </ul>
            <button class="menu-toggle"></button>
        </div>
    </nav>
    <section id="inicio" class="hero">
        <div class="container">
            <h1>{descripcion[:50]}</h1>
            <p>{descripcion[:150]}</p>
            <a href="#productos" class="btn">Ver Productos</a>
        </div>
    </section>
    <section id="productos" class="productos">
        <div class="container">
            <h2>Nuestros Productos</h2>
            <div class="productos-grid">
                <div class="card"><h3>Producto 1</h3><p>Descripcion del producto</p></div>
                <div class="card"><h3>Producto 2</h3><p>Descripcion del producto</p></div>
                <div class="card"><h3>Producto 3</h3><p>Descripcion del producto</p></div>
            </div>
        </div>
    </section>
    <section id="contacto" class="contacto">
        <div class="container">
            <h2>Contacto</h2>
            <form>
                <input type="text" placeholder="Nombre">
                <input type="email" placeholder="Email">
                <textarea placeholder="Mensaje"></textarea>
                <button type="submit">Enviar</button>
            </form>
        </div>
    </section>
    <footer class="footer">
        <div class="container"><p>2026 Todos los derechos reservados.</p></div>
    </footer>
    <script src="js/main.js"></script>
</body>
</html>"""

    elif ruta == "css/styles.css":
        return """:root {
    --primary: #8B4513;
    --primary-dark: #6B3410;
    --secondary: #D4A574;
    --light: #FFF8F0;
    --dark: #2C1810;
    --white: #ffffff;
    --shadow: 0 4px 15px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Poppins', sans-serif; line-height: 1.6; color: #333; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
.navbar { position: fixed; top: 0; width: 100%; background: var(--white); box-shadow: var(--shadow); z-index: 1000; padding: 1rem 0; }
.navbar .container { display: flex; justify-content: space-between; align-items: center; }
.nav-links { display: flex; list-style: none; gap: 2rem; }
.nav-links a { text-decoration: none; color: var(--dark); font-weight: 500; transition: var(--transition); }
.nav-links a:hover { color: var(--primary); }
.menu-toggle { display: none; background: none; border: none; font-size: 1.5rem; cursor: pointer; }
.hero { padding: 180px 0 100px; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: var(--white); text-align: center; }
.hero h1 { font-size: 3rem; margin-bottom: 1rem; }
.btn { display: inline-block; padding: 12px 30px; background: var(--white); color: var(--primary); border-radius: 30px; text-decoration: none; font-weight: 600; transition: var(--transition); }
.btn:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
.productos, .contacto { padding: 80px 0; }
.productos h2, .contacto h2 { text-align: center; font-size: 2.5rem; margin-bottom: 3rem; color: var(--primary); }
.productos-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }
.card { background: var(--light); padding: 2rem; border-radius: 15px; text-align: center; transition: var(--transition); }
.card:hover { transform: translateY(-10px); box-shadow: var(--shadow); }
.contacto form { max-width: 600px; margin: 0 auto; display: flex; flex-direction: column; gap: 1rem; }
input, textarea { padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 1rem; }
input:focus, textarea:focus { outline: none; border-color: var(--primary); }
button[type="submit"] { background: var(--primary); color: var(--white); border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: 600; }
button[type="submit"]:hover { background: var(--primary-dark); }
.footer { background: var(--dark); color: var(--white); text-align: center; padding: 2rem 0; }
@media (max-width: 768px) {
    .nav-links { display: none; flex-direction: column; position: absolute; top: 70px; left: 0; width: 100%; background: var(--white); padding: 1rem; }
    .nav-links.active { display: flex; }
    .menu-toggle { display: block; }
    .hero h1 { font-size: 2rem; }
}"""

    elif ruta == "js/main.js":
        return """document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });
    // Menu hamburguesa
    var menuToggle = document.querySelector('.menu-toggle');
    var navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() { navLinks.classList.toggle('active'); });
    }
    // Formulario
    var form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var inputs = form.querySelectorAll('input, textarea');
            var valid = true;
            inputs.forEach(function(input) { if (!input.value.trim()) { valid = false; } });
            if (!valid) { alert('Por favor, completa todos los campos'); return; }
            alert('Mensaje enviado. Gracias por contactarnos.');
            form.reset();
        });
    }
    // Animaciones al scroll
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.card').forEach(function(el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
});"""

    elif ruta == "README.md":
        return f"""# {descripcion[:50]}

## Descripcion
{descripcion[:200]}

## Tecnologias
- HTML5
- CSS3 (Flexbox, Grid, Variables CSS)
- JavaScript (Vanilla)

## Instalacion
1. Clonar el repositorio
2. Abrir index.html en el navegador

## Uso
Abrir el archivo index.html o servir con:
`ash
python -m http.server 8000
`
"""

    return f"# {ruta}\n\n{descripcion[:200]}"
