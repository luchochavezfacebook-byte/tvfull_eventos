#!/usr/bin/env python3
"""Valida eventos.json antes de publicarlo para las TV de TV FULL PRO.

Uso:  python3 tools/validar_eventos.py [eventos.json]

Sin dependencias externas. Si algo falla, imprime cada problema y termina
con código 1: GitHub no publica el archivo y las TV siguen con el anterior.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TIPOS = {
    "futbol", "automovilismo", "boxeo", "mma", "basquet", "tenis", "musica",
    "otros",
}
CAMPOS_RAIZ = {"version", "semana", "actualizado", "eventos"}
CAMPOS_EVENTO = {
    "id", "titulo", "competencia", "tipo", "inicio", "fin", "canales",
    "palabras", "destacado", "imagen",
}
MAX_EVENTOS = 300
MAX_BYTES = 300 * 1024
MAX_DURACION = timedelta(hours=12)
ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HORA_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z$")
IMAGEN = re.compile(
    r"^imagenes/[a-z0-9][a-z0-9_-]*(/[a-z0-9][a-z0-9_-]*)?\.(jpg|jpeg|png|webp)$"
)
# Las TV tienen poca memoria: imágenes livianas y pocas por semana.
MAX_BYTES_IMAGEN = 150 * 1024
MAX_EVENTOS_CON_IMAGEN = 12
FIRMAS = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
}
ENLACE = re.compile(r"(https?://|www\.|\.m3u8?\b|\.ts\b)", re.IGNORECASE)


def _hora(valor: object) -> datetime | None:
    if not isinstance(valor, str) or not HORA_UTC.match(valor):
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None


def _texto(valor: object, minimo: int, maximo: int) -> bool:
    return isinstance(valor, str) and minimo <= len(valor.strip()) <= maximo


def _lista_textos(valor: object, maximo: int, largo: int) -> bool:
    return (
        isinstance(valor, list)
        and len(valor) <= maximo
        and all(_texto(v, 2, largo) for v in valor)
    )


def validar_imagen(ruta: Path) -> str | None:
    """Problema de un archivo de imagenes/, o None si está bien."""
    tam = ruta.stat().st_size
    if tam > MAX_BYTES_IMAGEN:
        return f"{ruta.as_posix()}: pesa {tam // 1024} KB (máximo {MAX_BYTES_IMAGEN // 1024} KB)."
    cabeza = ruta.read_bytes()[:12]
    es_webp = cabeza[:4] == b"RIFF" and cabeza[8:12] == b"WEBP"
    if not es_webp and not any(cabeza.startswith(f) for f in FIRMAS):
        return f"{ruta.as_posix()}: no es una imagen JPG, PNG o WEBP válida."
    return None


def validar_imagenes(raiz: Path) -> list[str]:
    errores = []
    carpeta = raiz / "imagenes"
    if not carpeta.is_dir():
        return errores
    for ruta in sorted(carpeta.rglob("*")):
        if not ruta.is_file() or ruta.name == ".gitkeep" or ruta.name.lower() == "leeme.md":
            continue
        relativa = ruta.relative_to(raiz).as_posix()
        if not IMAGEN.match(relativa):
            errores.append(f"{relativa}: nombre no permitido (minúsculas, números y guiones; .jpg, .png o .webp; una subcarpeta como máximo).")
            continue
        problema = validar_imagen(ruta)
        if problema:
            errores.append(problema)
    return errores


def validar(datos: object, bytes_archivo: int = 0, raiz: Path | None = None) -> list[str]:
    errores: list[str] = []
    con_imagen = 0
    if bytes_archivo > MAX_BYTES:
        errores.append(f"El archivo pesa {bytes_archivo} bytes (máximo {MAX_BYTES}).")
    if not isinstance(datos, dict):
        return errores + ["La raíz tiene que ser un objeto JSON."]

    sobrantes = set(datos) - CAMPOS_RAIZ
    if sobrantes:
        errores.append(f"Campos desconocidos en la raíz: {sorted(sobrantes)}.")
    if datos.get("version") != 1:
        errores.append("`version` tiene que ser 1.")

    semana = None
    if not isinstance(datos.get("semana"), str) or not FECHA.match(datos["semana"]):
        errores.append("`semana` tiene que ser una fecha AAAA-MM-DD.")
    else:
        try:
            semana = date.fromisoformat(datos["semana"])
            if semana.weekday() != 0:
                errores.append("`semana` tiene que ser un lunes.")
        except ValueError:
            errores.append("`semana` no es una fecha válida.")
    if _hora(datos.get("actualizado")) is None:
        errores.append("`actualizado` tiene que ser una hora UTC terminada en Z.")

    eventos = datos.get("eventos")
    if not isinstance(eventos, list):
        return errores + ["`eventos` tiene que ser una lista."]
    if len(eventos) > MAX_EVENTOS:
        errores.append(f"Hay {len(eventos)} eventos (máximo {MAX_EVENTOS}).")

    desde = hasta = None
    if semana is not None:
        lunes = datetime(semana.year, semana.month, semana.day, tzinfo=timezone.utc)
        desde, hasta = lunes - timedelta(days=7), lunes + timedelta(days=14)

    vistos: set[str] = set()
    for i, ev in enumerate(eventos):
        nombre = f"Evento {i + 1}"
        if not isinstance(ev, dict):
            errores.append(f"{nombre}: tiene que ser un objeto.")
            continue
        if isinstance(ev.get("id"), str):
            nombre = f"Evento {i + 1} ({ev['id']})"
        sobrantes = set(ev) - CAMPOS_EVENTO
        if sobrantes:
            errores.append(f"{nombre}: campos desconocidos {sorted(sobrantes)}.")

        ident = ev.get("id")
        if not isinstance(ident, str) or not ID.match(ident):
            errores.append(f"{nombre}: `id` inválido (minúsculas, números y guiones).")
        elif ident in vistos:
            errores.append(f"{nombre}: `id` repetido.")
        else:
            vistos.add(ident)

        if not _texto(ev.get("titulo"), 3, 80):
            errores.append(f"{nombre}: `titulo` de 3 a 80 caracteres.")
        if "competencia" in ev and not _texto(ev["competencia"], 2, 60):
            errores.append(f"{nombre}: `competencia` de 2 a 60 caracteres.")
        if ev.get("tipo") not in TIPOS:
            errores.append(f"{nombre}: `tipo` tiene que ser uno de {sorted(TIPOS)}.")

        inicio, fin = _hora(ev.get("inicio")), _hora(ev.get("fin"))
        if inicio is None:
            errores.append(f"{nombre}: `inicio` tiene que ser una hora UTC terminada en Z.")
        if fin is None:
            errores.append(f"{nombre}: `fin` tiene que ser una hora UTC terminada en Z.")
        if inicio and fin:
            if not inicio < fin:
                errores.append(f"{nombre}: `inicio` tiene que ser anterior a `fin`.")
            elif fin - inicio > MAX_DURACION:
                errores.append(f"{nombre}: dura más de 12 horas.")
            if desde and hasta and not (desde <= inicio <= hasta):
                errores.append(
                    f"{nombre}: `inicio` fuera del rango de la semana "
                    f"({desde.date()} a {hasta.date()})."
                )

        canales = ev.get("canales", [])
        palabras = ev.get("palabras", [])
        if not _lista_textos(canales, 12, 40):
            errores.append(f"{nombre}: `canales` es una lista de hasta 12 nombres (2 a 40 caracteres).")
            canales = []
        if not _lista_textos(palabras, 6, 30):
            errores.append(f"{nombre}: `palabras` es una lista de hasta 6 palabras (2 a 30 caracteres).")
            palabras = []
        if not canales and not palabras:
            errores.append(f"{nombre}: necesita `canales` o `palabras`.")
        if "destacado" in ev and not isinstance(ev["destacado"], bool):
            errores.append(f"{nombre}: `destacado` tiene que ser true o false.")
        if "imagen" in ev:
            imagen = ev["imagen"]
            if not isinstance(imagen, str) or not IMAGEN.match(imagen):
                errores.append(f"{nombre}: `imagen` tiene que ser una ruta dentro de imagenes/.")
            elif raiz is not None and not (raiz / imagen).is_file():
                errores.append(f"{nombre}: no existe {imagen}.")
            con_imagen += 1

        for campo in ("titulo", "competencia"):
            if isinstance(ev.get(campo), str) and ENLACE.search(ev[campo]):
                errores.append(f"{nombre}: `{campo}` no puede tener enlaces.")
        for valor in [*canales, *palabras]:
            if ENLACE.search(valor):
                errores.append(f"{nombre}: `canales` y `palabras` no pueden tener enlaces.")
                break
    if con_imagen > MAX_EVENTOS_CON_IMAGEN:
        errores.append(f"Hay {con_imagen} eventos con imagen (máximo {MAX_EVENTOS_CON_IMAGEN}): dejala sólo en los destacados.")
    if raiz is not None:
        errores.extend(validar_imagenes(raiz))
    return errores


def main(argv: list[str]) -> int:
    ruta = Path(argv[1] if len(argv) > 1 else "eventos.json")
    try:
        crudo = ruta.read_bytes()
        datos = json.loads(crudo.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"No se pudo leer {ruta}: {error}")
        return 1
    errores = validar(datos, len(crudo), ruta.parent)
    if errores:
        print(f"{ruta}: {len(errores)} problema(s)")
        for error in errores:
            print(f"  - {error}")
        return 1
    print(f"{ruta}: OK, {len(datos['eventos'])} eventos para la semana del {datos['semana']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
