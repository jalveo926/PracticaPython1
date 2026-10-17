import sys
from pathlib import Path

carpetaProyecto = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(carpetaProyecto))

from problema3.manejaSensores import SensoresPolars


def mostrarResumen(procesador):
    print("\n===== RESUMEN DE SENSORES =====")
    print(procesador.resumen)
    print(f"\nCantidad de alertas: {procesador.alertas.height}")
    if procesador.alertas.height:
        print("\n===== ALERTAS =====")
        print(
            procesador.alertas.select(
                ["sensor", "ubicacion", "fecha", "hora", "motivo"]
            )
        )


def ejecutarPrograma():
    archivoCSV = carpetaProyecto / "sensores.csv"
    carpetaSalida = carpetaProyecto / "problema3"
    procesador = SensoresPolars(archivoCSV, carpetaSalida)
    procesador.validarDatos()
    procesador.crearColumnasAnalisis()
    procesador.calcularResumen()
    mostrarResumen(procesador)
    procesador.exportarResultados()


if __name__ == "__main__":
    try:
        ejecutarPrograma()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

