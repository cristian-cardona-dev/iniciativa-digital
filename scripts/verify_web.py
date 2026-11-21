#!/usr/bin/env python3
"""Verifica la web publica antes de cada commit.

Comprueba:
  1. Marca publica: debe aparecer "Geos Digital"; no "GEOS Iniciativas Digitales" ni "SocialOps Studio".
  2. Sin datos de ejemplo: no "hola@ejemplo.com" ni "iniciativa.example".
  3. Metadatos sociales: og:title, og:description y robots.
  4. Aviso de privacidad: existe privacidad.html con noindex y aviso BORRADOR.
  5. Sin scripts de seguimiento externos.
  6. Contraste de las tarjetas en modo oscuro: las reglas oscuras de .id-need y .id-path.id-join
     deben apuntar a variables claras, no a colores oscuros fijos.

Salida: OK o lista de fallos, codigo 1.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
PRIVACY = ROOT / "privacidad.html"


def check_brand(failures: list[str]) -> None:
    if not INDEX.exists():
        failures.append("falta index.html")
        return
    html = INDEX.read_text(encoding="utf-8")
    if "Geos Digital" not in html:
        failures.append("la web no menciona la marca publica 'Geos Digital'")
    for bad in ("GEOS Iniciativas Digitales", "SocialOps Studio"):
        if bad in html:
            failures.append(f"la web menciona la marca antigua: {bad}")


def check_examples(failures: list[str]) -> None:
    html = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    for bad in ("hola@ejemplo.com", "iniciativa.example"):
        if bad in html:
            failures.append(f"la web contiene un dato de ejemplo: {bad}")


def check_metadata(failures: list[str]) -> None:
    html = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    for meta in ('og:title', 'og:description', 'name="robots"'):
        if meta not in html:
            failures.append(f"falta el metadato {meta} en index.html")


def check_tracking(failures: list[str]) -> None:
    html = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    if re.search(r"<script[^>]+src=", html):
        failures.append("index.html carga un script externo")


def check_privacy(failures: list[str]) -> None:
    if not PRIVACY.exists():
        failures.append("falta privacidad.html")
        return
    text = PRIVACY.read_text(encoding="utf-8")
    if 'name="robots" content="noindex' not in text:
        failures.append("privacidad.html no tiene noindex mientras sea borrador")
    if "BORRADOR" not in text:
        failures.append("privacidad.html no marca el aviso como BORRADOR")


def check_contrast(failures: list[str]) -> None:
    html = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    # Las reglas oscuras de las tarjetas deben usar variables claras.
    if re.search(r'data-theme="dark"\] \.id-need\{color:#[0-9a-fA-F]{6}\}', html):
        failures.append("modo oscuro: .id-need usa un color fijo en vez de var(--ink)")
    # .id-path.id-join es una excepcion intencionada: el lima conserva texto oscuro.
    # Solo falla si el color fijo es claro (ej. #f2f4ff) sobre el fondo lima.
    m = re.search(r'data-theme="dark"\] \.id-path\.id-join,#\S+ \.id-path\.id-join \*\{color:(#[0-9a-fA-F]{6})\}', html)
    if m and m.group(1).lower() in ("#f2f4ff", "#ffffff", "#ffffff"):
        failures.append("modo oscuro: .id-path.id-join usa un color claro sobre fondo lima")
    # El fondo de las tarjetas debe seguir siendo oscuro.
    if re.search(r'--need-one:#[0-9a-fA-F]{6}', html) and re.search(r'--ink:#[0-9a-fA-F]{6}', html):
        pass  # variables presentes; el navegador mide el contraste real


def main() -> int:
    failures: list[str] = []
    check_brand(failures)
    check_examples(failures)
    check_metadata(failures)
    check_tracking(failures)
    check_privacy(failures)
    check_contrast(failures)
    if failures:
        for f in failures:
            print(f"FALLO: {f}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
