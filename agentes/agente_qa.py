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
