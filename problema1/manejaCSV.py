import csv
import datetime
import json
from pathlib import Path

from problema1.estudiantes import Estudiante
from utils import Utilidades

def validarRegistro(fila, cedulas_existentes):
    # Limpiamos los espacios alrededor de la cédula
    cedula = fila['cedula'].strip()
    
    if cedula in cedulas_existentes:
        return False, f"Registro duplicado: La cédula {cedula} ya existe."
    
    try:
        # Convertimos las notas soportando comas y espacios
        notas = [
            float(str(fila['parcial1']).strip().replace(',', '.')),
            float(str(fila['parcial2']).strip().replace(',', '.')),
            float(str(fila['proyecto']).strip().replace(',', '.'))
        ]
        if any(nota < 0 or nota > 100 for nota in notas):
            return False, f"Registro inválido: Las notas deben estar entre 0 y 100."
    except ValueError:
        return False, f"Registro inválido: Las notas deben ser números válidos."
    except KeyError as e:
        return False, f"Registro inválido: Falta la columna {e} en el archivo CSV."
    
    cedulas_existentes.add(cedula)
    return True, "Registro válido."


class EstudianteCSV:
    def __init__(self, archivoCSV, archivoJSON):
        self.archivo = archivoCSV
        self.archivoJSON = archivoJSON
        self.cedulas_existentes = set()
        self.cantAprobados = 0
        self.cantReprobados = 0
        self.datos = self.leerCSV(self.cedulas_existentes)
    
    def leerCSV(self, cedulasExistentes):
        datos = []
        with open(self.archivo, mode='r', encoding='utf-8-sig') as archivo:
            # Lee el archivo CSV usando DictReader para obtener un diccionario por fila
            lector = csv.DictReader(archivo)
            
            # Quita espacios e invisibles (\n, \r) de los encabezados
            if lector.fieldnames:
                lector.fieldnames = [campo.strip() for campo in lector.fieldnames]
            
            for fila in lector:
                # Limpia los espacios alrededor de las llaves y valores de cada fila
                fila_limpia = {k.strip(): v.strip() for k, v in fila.items() if k is not None}
                
                es_valido, mensaje = validarRegistro(fila_limpia, cedulasExistentes)
                if es_valido:
                    datos.append(fila_limpia)
                else:
                    # No hago print porque es mala práctica y devuelvo el mensaje de error para que el usuario lo maneje
                    Utilidades.advertencia(mensaje)
                    
        return datos

    def extraerCampoCompleto(self, campo):
        return [fila[campo] for fila in self.datos if campo in fila]
    
    def escribirJSON(self, datos=None):
        datos_a_guardar = datos if datos is not None else self.datos
        for fila in datos_a_guardar:
            estudiante = Estudiante(
                fila['cedula'],
                fila['nombre'],
                float(fila['parcial1']),
                float(fila['parcial2']),
                float(fila['proyecto'])
            )
            fila['promedio_general'] = estudiante.calcularPromedioGeneral()
            fila['estado'] = estudiante.determinarEstado()
            if fila['estado'] == "Aprobado":
                self.cantAprobados += 1
            else:
                self.cantReprobados += 1
            fila['nota_final'] = estudiante.calcularNotaFinal()
            fila['mayor_nota'] = estudiante.mayorNota()
            fila['menor_nota'] = estudiante.menorNota()
            
        with open(self.archivoJSON, 'w', encoding='utf-8') as archivo:
            json.dump(datos_a_guardar, archivo, indent=4, ensure_ascii=False)
            
    def escribirResumenTXT(self):
        ruta_resumen = Path(self.archivoJSON).parent / 'resumen.txt'
        with open(ruta_resumen, 'w', encoding='utf-8') as archivo:
            archivo.write("Resumen de Estudiantes\n")
            archivo.write("======================\n")
            archivo.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            archivo.write(f"Cantidad de registros procesados: {len(self.datos)}\n")
            archivo.write(f"Cantidad de aprobados: {self.cantAprobados}\n")
            archivo.write(f"Cantidad de reprobados: {self.cantReprobados}\n")
