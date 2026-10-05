#!/usr/bin/env python3

import subprocess
import random
import string
import sys
import time

# ==========================
# Colores ANSI
# ==========================

CYAN = "\033[96m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
RED = "\033[91m"
RESET = "\033[0m"

# Caracteres para el efecto cyberpunk
CHARS = string.ascii_letters + string.digits + "@#$%&*+=!?<>"

# ==========================
# Fastfetch
# ==========================

def obtener_fastfetch():
    salida = subprocess.check_output(
        ["fastfetch", "--logo", "none", "--pipe"],
        text=True
    )

    datos = {}

    for linea in salida.splitlines():
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            datos[clave.strip()] = valor.strip()

    return datos

# ==========================
# Animación Cyberpunk
# ==========================

def cyberprint(prefijo, texto, color=RESET, velocidad=0.015, iteraciones=8):
    longitud = len(texto)

    for _ in range(iteraciones):

        falso = "".join(
            random.choice(CHARS) if c != " " else " "
            for c in texto
        )

        sys.stdout.write(f"\r{color}{prefijo}{RESET}{falso}")
        sys.stdout.flush()
        time.sleep(velocidad)

    # Revelado letra por letra
    revelado = list(texto)

    for i in range(longitud):
        parcial = ""

        for j in range(longitud):
            if j <= i:
                parcial += revelado[j]
            else:
                parcial += random.choice(CHARS) if revelado[j] != " " else " "

        sys.stdout.write(f"\r{color}{prefijo}{RESET}{parcial}")
        sys.stdout.flush()
        time.sleep(velocidad)

    print()

# ==========================
# Información
# ==========================

def fish_greeting():

    datos = obtener_fastfetch()

    cpu = " ".join(datos.get("CPU", "").split()[:3])

    cyberprint("  OS:       ", datos.get("OS", ""), CYAN)
    cyberprint("  Kernel:   ", datos.get("Kernel", ""), GREEN)
    cyberprint("󰻠  CPU:      ", cpu, MAGENTA)
    cyberprint("󰍛  Memory:   ", datos.get("Memory", ""), RED)


if __name__ == "__main__":
    fish_greeting()
