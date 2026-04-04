class ProgresoVisual:
    def __init__(self):
        self.etapa_actual = None
        self.detalle = None
        self.total_archivos = 0
        self.archivos_generados = 0
    def actualizar_etapa(self, etapa, detalle=None):
        self.etapa_actual = etapa
        self.detalle = detalle
        if detalle:
            print(f"\n🔄 {etapa}: {detalle}")
        else:
            print(f"\n🔄 {etapa}")
    def iniciar_generacion_archivo(self, archivo):
        print(f"   ⏳ Generando archivo: {archivo}")
        self.archivos_generados += 1
        self.mostrar_progreso()
    def completar_archivo(self, archivo, longitud, preview):
        print(f"   ✅ Archivo generado: {archivo} ({longitud} caracteres)")
        print(f"      Preview: {preview}")
        self.mostrar_progreso()
    def mostrar_progreso(self):
        if self.total_archivos:
            porcentaje = (self.archivos_generados / self.total_archivos) * 100
            print(f"      Progreso: {self.archivos_generados}/{self.total_archivos} archivos ({porcentaje:.1f}%)")
        else:
            print(f"      Progreso: {self.archivos_generados} archivos generados")

progreso = ProgresoVisual()
