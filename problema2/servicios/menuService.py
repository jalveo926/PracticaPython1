from utils import Utilidades


class MenuProductos:
    def __init__(self, productos):
        self.productos = productos
        self.movimientos = []

    @staticmethod
    def validarCodigos(productos):
        codigos = [producto.get("codigo", "").strip() for producto in productos]
        if any(not codigo for codigo in codigos):
            raise ValueError("Todos los productos deben tener un código.")
        if len(codigos) != len(set(codigos)):
            raise ValueError("No se permiten códigos de producto duplicados.")

    def mostrarProductos(self):
        if not self.productos:
            print("\nNo hay productos registrados en el inventario.")
            return
        print("\n" + "=" * 76)
        print(f"{'CÓDIGO':<8} | {'PRODUCTO':<32} | {'CANTIDAD':>8} | {'PRECIO':>12}")
        print("-" * 76)
        for producto in self.productos:
            print(
                f"{producto['codigo']:<8} | {producto['producto']:<32} | "
                f"{producto['cantidad']:>8} | ${producto['precio']:>11.2f}"
            )
        print("=" * 76)

    def buscarPorCodigo(self, codigo):
        return next(
            (producto for producto in self.productos if producto["codigo"] == codigo),
            None,
        )

    def mostrarProductoPorCodigo(self, codigo):
        producto = self.buscarPorCodigo(codigo)
        if producto is None:
            print(f"No se encontró ningún producto con el código '{codigo}'.")
            return
        print(
            f"\nCódigo: {producto['codigo']}\n"
            f"Producto: {producto['producto']}\n"
            f"Existencia: {producto['cantidad']}\n"
            f"Precio unitario: ${producto['precio']:.2f}"
        )

    def registrarMovimiento(self, codigo, tipo, cantidad):
        producto = self.buscarPorCodigo(codigo)
        if producto is None:
            print(f"No se encontró ningún producto con el código '{codigo}'.")
            return False
        if not Utilidades.esPositivo(cantidad):
            print("La cantidad del movimiento debe ser positiva.")
            return False
        if tipo == "salida" and cantidad > producto["cantidad"]:
            print(
                f"Existencias insuficientes. Disponibles: {producto['cantidad']}."
            )
            return False

        producto["cantidad"] += cantidad if tipo == "entrada" else -cantidad
        self.movimientos.append(
            {
                "codigo": codigo,
                "tipo": tipo,
                "cantidad": cantidad,
                "existencia_final": producto["cantidad"],
            }
        )
        print(f"Movimiento registrado. Existencia final: {producto['cantidad']}.")
        return True

    def registrarEntrada(self, codigo, cantidad):
        return self.registrarMovimiento(codigo, "entrada", cantidad)

    def registrarSalida(self, codigo, cantidad):
        return self.registrarMovimiento(codigo, "salida", cantidad)
