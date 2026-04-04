import re
import time
from core.progreso import progreso


def _llamar_llm(prompt: str) -> str:
    """Llama al LLM (Google GenAI) y retorna el texto de respuesta."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.7)
    response = llm.invoke(prompt)
    return response.content


def generar_archivo_individual(ruta: str, descripcion: str, tipo: str, sistema_aprendizaje) -> str:
    """Genera contenido con prompts especificos para mejor calidad."""
    progreso.iniciar_generacion_archivo(ruta)
    time.sleep(0.3)
    contexto = sistema_aprendizaje.obtener_contexto_aprendizaje(descripcion)

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
        html_match = re.search(r'<!DOCTYPE html>.*?</html>', contenido, re.DOTALL)
        if html_match:
            contenido = html_match.group(0)

    elif ruta == "css/styles.css":
        prompt = f"""Eres un disenador CSS EXPERTO. Genera CSS COMPLETO y PROFESIONAL.

DESCRIPCION:
{descripcion[:300]}

{contexto}

REQUISITOS OBLIGATORIOS:
1. Diseno RESPONSIVE con media queries (mobile, tablet, desktop)
2. Usa CSS Grid y/o Flexbox para layouts
3. Variables CSS con :root para colores (paleta armoniosa)
4. Efectos HOVER en botones y cards
5. Animaciones suaves (transitions)
6. Tipografia moderna (Google Fonts)
7. NO incluir explicaciones, SOLO CSS

Genera SOLO el CSS:"""
        contenido = _llamar_llm(prompt)

    elif ruta == "js/main.js":
        prompt = f"""Genera JavaScript INTERACTIVO para:

{descripcion[:300]}

REQUISITOS:
1. Smooth scroll para navegacion
2. Validacion de formulario
3. Menu hamburguesa para movil
4. Animaciones al hacer scroll (IntersectionObserver)
5. NO jQuery, solo Vanilla JS
6. Codigo dentro de DOMContentLoaded

Genera SOLO el JavaScript:"""
        contenido = _llamar_llm(prompt)

    elif ruta == "README.md":
        prompt = f"""Genera README.md profesional para:
{descripcion[:300]}

Incluye: titulo, descripcion, tecnologias, instalacion, uso, estructura del proyecto.

Genera SOLO markdown:"""
        contenido = _llamar_llm(prompt)

    else:
        prompt = f"""Genera el contenido del archivo '{ruta}' para el proyecto:
{descripcion[:300]}

Genera SOLO el codigo, sin explicaciones:"""
        contenido = _llamar_llm(prompt)

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
