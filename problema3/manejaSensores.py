import json
from pathlib import Path

import polars as pl

from utils import Utilidades


class SensoresPolars:
    columnasRequeridas = [
        "sensor",
        "ubicacion",
        "fecha",
        "hora",
        "temperatura",
        "humedad",
    ]

    def __init__(self, archivoCSV, carpetaSalida):
        self.archivoCSV = archivoCSV
        self.carpetaSalida = carpetaSalida
        self.datos = self.leerCSV()
        self.alertas = pl.DataFrame()
        self.resumen = pl.DataFrame()

    def leerCSV(self):
        try:
            datos = pl.read_csv(
                self.archivoCSV,
                has_header=True,
                infer_schema=False,
                try_parse_dates=False,
            )
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"No existe el archivo {self.archivoCSV}."
            ) from error
        except pl.exceptions.PolarsError as error:
            raise ValueError(f"No se pudo leer el archivo CSV: {error}") from error

        columnasFaltantes = [
            columna
            for columna in self.columnasRequeridas
            if columna not in datos.columns
        ]
        if columnasFaltantes:
            raise ValueError(
                f"Faltan columnas requeridas: {', '.join(columnasFaltantes)}."
            )
        return datos.select(self.columnasRequeridas)

    def validarDatos(self):
        cantidadInicial = self.datos.height
        import polars as pl

        datos = self.datos.with_columns(
            [
                pl.col("sensor").cast(pl.String).str.strip_chars(),
                pl.col("ubicacion").cast(pl.String).str.strip_chars(),
                pl.col("fecha").cast(pl.String).str.strip_chars(),
                pl.col("hora").cast(pl.String).str.strip_chars(),
                pl.col("temperatura")
                .cast(pl.String)
                .str.strip_chars()
                .str.replace(",", ".")
                .cast(pl.Float64, strict=False),
                pl.col("humedad")
                .cast(pl.String)
                .str.strip_chars()
                .str.replace(",", ".")
                .cast(pl.Float64, strict=False),
            ]
        )

        datosValidos = datos.filter(
            pl.col("sensor").is_not_null()
            & (pl.col("sensor") != "")
            & pl.col("ubicacion").is_not_null()
            & (pl.col("ubicacion") != "")
            & pl.col("fecha").is_not_null()
            & (pl.col("fecha") != "")
            & pl.col("hora").is_not_null()
            & (pl.col("hora") != "")
            & pl.col("temperatura").is_not_null()
            & pl.col("humedad").is_not_null()
            & pl.col("humedad").is_between(0, 100, closed="both")
        )

        cantidadDescartada = cantidadInicial - datosValidos.height
        if cantidadDescartada:
            Utilidades.advertencia(
                f"Se descartaron {cantidadDescartada} registros incompletos o inválidos."
            )

        sensores = datosValidos.get_column("sensor").to_list()
        sensoresInvalidos = [
            sensor
            for sensor in sensores
            if not isinstance(sensor, str)
            or not sensor.startswith("S")
            or not sensor[1:].isdigit()
        ]
        if sensoresInvalidos:
            datosValidos = datosValidos.filter(
                pl.col("sensor").str.starts_with("S")
                & pl.col("sensor").str.slice(1).str.contains(r"^\d+$")
            )
            Utilidades.advertencia(
                f"Se descartaron {len(sensoresInvalidos)} identificadores de sensor inválidos."
            )

        self.datos = datosValidos
        return self.datos

    def crearColumnasAnalisis(self):
        self.datos = self.datos.with_columns(
            [
                pl.when(
                    (pl.col("temperatura") > 32.0)
                    & (pl.col("humedad") > 80)
                )
                .then(pl.lit("Temperatura y humedad"))
                .when(pl.col("temperatura") > 32.0)
                .then(pl.lit("Temperatura alta"))
                .when(pl.col("humedad") > 80)
                .then(pl.lit("Humedad alta"))
                .otherwise(pl.lit(""))
                .alias("motivo"),
            ]
        ).with_columns(
            pl.when(pl.col("motivo") != "")
            .then(pl.lit("ALERTA"))
            .otherwise(pl.lit("NORMAL"))
            .alias("estado")
        )
        self.alertas = self.datos.filter(pl.col("estado") == "ALERTA")
        return self.datos

    def calcularResumen(self):
        resumenTemperatura = self.datos.group_by("sensor").agg(
            [
                pl.len().alias("cantidadMediciones"),
                pl.col("temperatura").mean().round(2).alias("temperaturaPromedio"),
                pl.col("temperatura").max().alias("temperaturaMaxima"),
                pl.col("temperatura").min().alias("temperaturaMinima"),
            ]
        )
        resumenHumedad = self.datos.group_by(["sensor", "ubicacion"]).agg(
            pl.col("humedad").mean().round(2).alias("humedadPromedio")
        )
        self.resumen = resumenHumedad.join(resumenTemperatura, on="sensor").select(
            [
                "sensor",
                "ubicacion",
                "cantidadMediciones",
                "temperaturaPromedio",
                "temperaturaMaxima",
                "temperaturaMinima",
                "humedadPromedio",
            ]
        ).sort(["sensor", "ubicacion"])
        return self.resumen

    def exportarResultados(self):
        carpeta = Path(self.carpetaSalida)
        carpeta.mkdir(parents=True, exist_ok=True)

        alertas = self.alertas.to_dicts()
        with (carpeta / "alertas.json").open("w", encoding="utf-8") as archivo:
            json.dump(alertas, archivo, indent=4, ensure_ascii=False)

        self.resumen.write_csv(carpeta / "resumen_sensores.csv")
        self.datos.write_json(
            carpeta / "sensores_procesados.json",
        )

        Utilidades.mostrarMensaje(
            "\nArchivos generados: alertas.json, resumen_sensores.csv "
            "y sensores_procesados.json."
        )
