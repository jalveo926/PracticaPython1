# Laboratorio 2 por Jesús Alveo 1GS131

import sys
from pathlib import Path

carpeta_proyecto = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(carpeta_proyecto))

from problema1.manejaCSV import EstudianteCSV
#EJECUTAR ESTE ARCHIVO PARA PROBAR PROBLEMA 1
#abrir el proyecto principal para que detecte los datos en la carpeta mayor

archivoCSV = carpeta_proyecto / 'estudiantes.csv'
archivoJSON = carpeta_proyecto / 'estudiantes.json'

manejadorCSV = EstudianteCSV(archivoCSV, archivoJSON)
manejadorCSV.escribirJSON()
manejadorCSV.escribirResumenTXT()
