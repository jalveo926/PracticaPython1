import sys
from pathlib import Path

carpeta_proyecto = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(carpeta_proyecto))

from problema2.manejaJSON import ProductosJSON
from problema2.servicios.menuService import MenuProductos


def leerEntero(mensaje):
    """Solicita una cantidad entera y evita aceptar valores no válidos."""
    while True:
        try:
            cantidad = int(input(mensaje))
            if cantidad <= 0:
                print("La cantidad debe ser un número entero positivo.")
                continue
            return cantidad
        except ValueError:
            print("Ingrese un número entero válido.")


def mostrarResumen(manejador):
    print(f"\nValor total del inventario: ${manejador.calcularValorTotalInventario():,.2f}")
    productos_bajos = manejador.productosMenorCantidad()
    print(f"Productos con menos de 15 unidades: {len(productos_bajos)}")
    for producto in productos_bajos:
        print(f"- {producto['codigo']}: {producto['producto']} ({producto['cantidad']} unidades)")


def ejecutarMenu():
    archivo_json = carpeta_proyecto / "inventario.json"
    manejador = ProductosJSON(archivo_json)
    manejador.eliminarDuplicados()

    if len(manejador.datos) < 20:
        raise ValueError("inventario.json debe contener al menos 20 productos.")
    MenuProductos.validarCodigos(manejador.datos)
    menu = MenuProductos(manejador.datos)

    while True:
        print(
            "\n===== GESTIÓN DE INVENTARIO =====\n"
            "1. Listar productos\n"
            "2. Buscar producto por código\n"
            "3. Registrar entrada\n"
            "4. Registrar salida\n"
            "5. Mostrar resumen del inventario\n"
            "6. Guardar y salir\n"
            "7. Salir sin guardar"
        )
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu.mostrarProductos()
        elif opcion == "2":
            codigo = input("Código del producto: ").strip().upper()
            menu.mostrarProductoPorCodigo(codigo)
        elif opcion in ("3", "4"):
            codigo = input("Código del producto: ").strip().upper()
            cantidad = leerEntero("Cantidad del movimiento: ")
            if opcion == "3":
                menu.registrarEntrada(codigo, cantidad)
            else:
                menu.registrarSalida(codigo, cantidad)
        elif opcion == "5":
            mostrarResumen(manejador)
        elif opcion == "6":
            manejador.guardarInventarioActualizado(menu.movimientos)
            print("\nCambios guardados en inventario_actualizado.json, inventario.csv y movimientos.csv.")
            break
        elif opcion == "7":
            print("\nSaliendo sin guardar los cambios.")
            break
        else:
            print("Opción inválida. Seleccione un número del 1 al 7.")


if __name__ == "__main__":
    try:
        ejecutarMenu()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
