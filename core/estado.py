from typing import TypedDict, List, Dict

class EstadoProyecto(TypedDict):
    input_usuario: str
    tipo_proyecto: str
    estructura_archivos: Dict[str, Dict]
    archivos_generados: Dict[str, str]
    archivos_por_generar: List[str]
    errores: List[str]
    revision_aprobada: bool
    logs: List[str]
