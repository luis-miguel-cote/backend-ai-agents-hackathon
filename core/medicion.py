import time
from datetime import datetime

class MedidorTiempos:
    """Mide y registra tiempos de ejecución de cada fase"""
    def __init__(self):
        self.tiempos = {}
        self.inicio_total = None
        self.fin_total = None
        self.fase_actual = None
        self.inicio_fase = None
    def iniciar_total(self):
        self.inicio_total = time.time()
        print(f"\n⏱️  INICIO DEL PROCESO: {datetime.now().strftime('%H:%M:%S')}")
    def finalizar_total(self):
        self.fin_total = time.time()
        total = self.obtener_total()
        print(f"\n⏱️  FIN DEL PROCESO: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        print(f"📊 TIEMPO TOTAL: {total:.1f} segundos ({total/60:.1f} minutos)")
        print(f"{'='*60}")
        return total
    def iniciar_fase(self, nombre_fase: str):
        if self.fase_actual and self.inicio_fase:
            self.finalizar_fase()
        self.fase_actual = nombre_fase
        self.inicio_fase = time.time()
        print(f"\n▶️  INICIO: {nombre_fase}")
    def finalizar_fase(self):
        if self.fase_actual and self.inicio_fase:
            duracion = time.time() - self.inicio_fase
            self.tiempos[self.fase_actual] = duracion
            print(f"✅ FINALIZADO: {self.fase_actual} - {duracion:.1f} segundos")
            self.fase_actual = None
            self.inicio_fase = None
    def obtener_total(self) -> float:
        if self.inicio_total and self.fin_total:
            return self.fin_total - self.inicio_total
        return 0
    def obtener_tiempo_fase(self, nombre_fase: str) -> float:
        return self.tiempos.get(nombre_fase, 0)
    def mostrar_resumen_tiempos(self):
        print(f"\n{'='*60}")
        print("📊 RESUMEN DE TIEMPOS DE EJECUCIÓN")
        print(f"{'='*60}")
        tiempos_ordenados = sorted(self.tiempos.items(), key=lambda x: x[1], reverse=True)
        for fase, tiempo in tiempos_ordenados:
            porcentaje = (tiempo / self.obtener_total()) * 100
            barra = "█" * int(porcentaje / 2) + "░" * (50 - int(porcentaje / 2))
            print(f"   {fase:20} : {tiempo:6.1f}s ({porcentaje:5.1f}%) {barra}")
        print(f"{'='*60}")
        print(f"   {'TOTAL':20} : {self.obtener_total():6.1f}s (100.0%)")
        print(f"{'='*60}")
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Fase más lenta: {max(self.tiempos, key=self.tiempos.get)} ({max(self.tiempos.values()):.1f}s)")
        print(f"   Fase más rápida: {min(self.tiempos, key=self.tiempos.get)} ({min(self.tiempos.values()):.1f}s)")
        print(f"   Total fases: {len(self.tiempos)}")

medidor = MedidorTiempos()
