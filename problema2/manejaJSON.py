import csv
import json

from utils import Utilidades


class ProductosJSON:
    def __init__(self, archivo_json):
        self.archivo_json = archivo_json
        self.datos = self.leerJson()

    def leerJson(self):
        try:
            with self.archivo_json.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError as error:
            raise FileNotFoundError(f"No existe el archivo {self.archivo_json}.") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"El archivo {self.archivo_json} no contiene JSON válido.") from error
        if not isinstance(datos, list):
            raise ValueError("El inventario debe ser una lista de productos.")
        return datos

    def eliminarDuplicados(self):
        productosUnicos = {}
        duplicados = 0

        for producto in self.datos:
            codigo = producto.get("codigo", "").strip()
            if codigo in productosUnicos:
                duplicados += 1
                continue
            productosUnicos[codigo] = producto

        self.datos = list(productosUnicos.values())
        if duplicados:
            Utilidades.advertencia(
                f"Se encontraron {duplicados} productos duplicados y se filtraron correctamente."
            )

    def calcularValorTotalInventario(self):
        return sum(producto["cantidad"] * producto["precio"] for producto in self.datos)

    def productosMenorCantidad(self):
        return [producto for producto in self.datos if producto["cantidad"] < 15]

    def guardarInventarioActualizado(self, movimientos):
        carpeta = self.archivo_json.parent
        with (carpeta / "inventario_actualizado.json").open("w", encoding="utf-8") as archivo:
            json.dump(self.datos, archivo, indent=4, ensure_ascii=False)

        with (carpeta / "inventario.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(
                archivo, fieldnames=("codigo", "producto", "cantidad", "precio")
            )
            escritor.writeheader()
            escritor.writerows(self.datos)

        with (carpeta / "movimientos.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(
                archivo,
                fieldnames=("codigo", "tipo", "cantidad", "existencia_final"),
            )
            escritor.writeheader()
            escritor.writerows(movimientos)
