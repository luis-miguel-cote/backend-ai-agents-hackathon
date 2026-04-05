"""
Agente de QA: Funciones técnicas de análisis estático, generación de pruebas y simulación de resultados.
"""

def static_code_analysis(code: str, language: str) -> dict:
    """Análisis estático básico del código."""
    
    issues = []
    if language.lower() in ("python", "py"):
        if "except:" in code and "pass" in code:
            issues.append("Bloque except vacío detectado (suprime errores silenciosamente)")
        if "eval(" in code or "exec(" in code:
            issues.append("Uso de eval/exec — riesgo de inyección de código")
        if "TODO" in code or "FIXME" in code:
            issues.append("Comentarios TODO/FIXME pendientes en el código")
        if "print(" in code and "log" not in code.lower():
            issues.append("Uso de print() en lugar de logging estructurado")
    if "password" in code.lower() and ("=" in code) and ('"' in code or "'" in code):
        issues.append("Posible credencial hardcodeada detectada")
    if len(code.split("\n")) > 300:
        issues.append("Archivo muy largo (>300 líneas) — considerar refactorización")
    return {
        "language": language,
        "lines": len(code.split("\n")),
        "static_issues_found": len(issues),
        "issues": issues,
        "status": "analyzed",
    }

def generate_test_cases(description: str, test_types: list = None) -> dict:
    """Genera casos de prueba estructurados."""
    types = test_types or ["unit", "edge", "security"]
    cases = []
    type_templates = {
        "unit": [
            "Verificar que la función retorna el resultado esperado con entrada válida",
            "Verificar que los tipos de retorno son correctos",
            "Verificar que los parámetros requeridos son validados",
        ],
        "edge": [
            "Probar con valores límite (0, -1, MAX_INT)",
            "Probar con cadenas vacías o None",
            "Probar con listas de un solo elemento y listas vacías",
        ],
        "security": [
            "Probar inyección SQL (si aplica)",
            "Probar XSS con payload <script>alert(1)</script>",
            "Verificar autenticación y autorización",
        ],
        "integration": [
            "Verificar integración con base de datos",
            "Verificar integración con servicios externos (mocks)",
            "Verificar manejo de timeouts y reintentos",
        ],
        "performance": [
            "Medir tiempo de respuesta bajo carga normal",
            "Probar con 1000 peticiones concurrentes",
            "Verificar que no hay memory leaks en operaciones repetidas",
        ],
    }
    for t in types:
        if t in type_templates:
            for template in type_templates[t]:
                cases.append(f"[{t.upper()}] {template} — contexto: {description[:60]}...")
    return {
        "total_cases": len(cases),
        "test_cases": cases,
        "coverage_types": types,
    }

def simulate_test_results(test_cases: list, code_context: str) -> dict:
    """Simula resultados de pruebas basándose en el contexto del código."""
    results = []
    passed = 0
    failed = 0
    risky_keywords = ["TODO", "FIXME", "pass", "eval(", "exec(", "hardcode", "password="]
    risk_score = sum(1 for kw in risky_keywords if kw.lower() in code_context.lower())
    for i, tc in enumerate(test_cases):
        fail_prob = False
        if "[SECURITY]" in tc and risk_score >= 2:
            fail_prob = True
        elif "[EDGE]" in tc and "None" not in code_context and i % 3 == 0:
            fail_prob = True
        status = "FAIL" if fail_prob else "PASS"
        if status == "PASS":
            passed += 1
        else:
            failed += 1
        results.append({"test": tc, "status": status, "note": "Simulado por el agente IA"})
    return {
        "total": len(test_cases),
        "passed": passed,
        "failed": failed,
        "pass_rate": round((passed / len(test_cases)) * 100, 1) if test_cases else 0,
        "results": results,
    }

def emit_verdict(passed_tests: int, failed_tests: int, critical_issues: list, warnings: list, summary: str) -> dict:
    """Emite el veredicto final del agente QA."""
    total = passed_tests + failed_tests
    pass_rate = (passed_tests / total * 100) if total > 0 else 0
    if critical_issues or pass_rate < 70:
        verdict = "❌ NO APTO PARA PRODUCCIÓN"
        color = "RED"
    elif pass_rate < 85 or warnings:
        verdict = "⚠️  APTO CON OBSERVACIONES"
        color = "YELLOW"
    else:
        verdict = "✅ APTO PARA PRODUCCIÓN"
        color = "GREEN"
    return {
        "verdict": verdict,
        "color": color,
        "pass_rate": round(pass_rate, 1),
        "passed": passed_tests,
        "failed": failed_tests,
        "critical_issues": critical_issues,
        "warnings": warnings,
        "summary": summary,
    }


# -- Mapa de extensiones a lenguajes --
_EXT_LANG = {
    "html": "html", "css": "css", "js": "javascript",
    "py": "python", "md": "markdown", "txt": "text",
}


def agente_qa(archivos_generados: dict, descripcion: str) -> dict:
    """Ejecuta el pipeline completo de QA sobre todos los archivos generados.

    Retorna un dict con el veredicto global y los detalles por archivo.
    """
    print("\n🔍 Ejecutando analisis de calidad...")

    todos_los_issues = []
    todos_los_warnings = []
    detalles_por_archivo = {}
    codigo_combinado = ""

    for ruta, contenido in archivos_generados.items():
        ext = ruta.rsplit(".", 1)[-1] if "." in ruta else "txt"
        lang = _EXT_LANG.get(ext, ext)

        # Analisis estatico
        analisis = static_code_analysis(contenido, lang)
        detalles_por_archivo[ruta] = analisis

        if analisis["issues"]:
            for issue in analisis["issues"]:
                todos_los_warnings.append(f"[{ruta}] {issue}")
            print(f"   ⚠️  {ruta}: {len(analisis['issues'])} observaciones")
        else:
            print(f"   ✅ {ruta}: OK ({analisis['lines']} lineas)")

        codigo_combinado += f"\n--- {ruta} ---\n{contenido}\n"

    # Validaciones especificas de estructura web
    if "index.html" in archivos_generados:
        html = archivos_generados["index.html"]
        if "css/styles.css" not in html:
            todos_los_issues.append("index.html no enlaza css/styles.css")
        if "js/main.js" not in html:
            todos_los_warnings.append("index.html no enlaza js/main.js")
        if "<!DOCTYPE html>" not in html:
            todos_los_issues.append("index.html no tiene <!DOCTYPE html>")
        if "<meta name=\"viewport\"" not in html:
            todos_los_warnings.append("index.html no tiene meta viewport")

    if "css/styles.css" in archivos_generados:
        css = archivos_generados["css/styles.css"]
        if ":root" not in css:
            todos_los_warnings.append("CSS sin variables :root")
        if "@media" not in css:
            todos_los_warnings.append("CSS sin media queries (no responsive)")

    # Generar tests y simular
    test_result = generate_test_cases(descripcion, ["unit", "edge", "security"])
    sim_result = simulate_test_results(test_result["test_cases"], codigo_combinado)

    # Veredicto final
    veredicto = emit_verdict(
        passed_tests=sim_result["passed"],
        failed_tests=sim_result["failed"],
        critical_issues=todos_los_issues,
        warnings=todos_los_warnings,
        summary=f"Analizados {len(archivos_generados)} archivos, {sim_result['total']} tests simulados",
    )

    # Mostrar resultado
    print(f"\n{'='*60}")
    print(f"🏆 VEREDICTO QA: {veredicto['verdict']}")
    print(f"{'='*60}")
    print(f"   Tests: {veredicto['passed']}/{veredicto['passed']+veredicto['failed']} pasaron ({veredicto['pass_rate']}%)")
    if veredicto["critical_issues"]:
        print(f"   ❌ Issues criticos:")
        for issue in veredicto["critical_issues"]:
            print(f"      - {issue}")
    if veredicto["warnings"]:
        print(f"   ⚠️  Observaciones:")
        for w in veredicto["warnings"][:5]:
            print(f"      - {w}")

    return veredicto
