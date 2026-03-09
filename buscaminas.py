"""
buscaminas.py
=============
Buscaminas en consola con Python puro.
Ejecutar:  python buscaminas.py

Controles:
  Descubrir celda  → escribir:  r c          ej: 3 5
  Poner bandera    → escribir:  f r c        ej: f 3 5
  Quitar bandera   → escribir:  f r c  (otra vez sobre la bandera)
  Salir            → escribir:  q
"""

import random, os, time

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
DIFICULTADES = {
    "1": ("FÁCIL",   9,  9,  10),
    "2": ("MEDIO",  16, 16,  40),
    "3": ("DIFÍCIL",16, 30,  99),
}

# Colores ANSI
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    BLACK  = "\033[30m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN="\033[42m"

NUM_COLORS = {
    1: C.GREEN,
    2: C.CYAN,
    3: C.RED,
    4: C.MAGENTA,
    5: C.YELLOW,
    6: C.BLUE,
    7: C.WHITE,
    8: C.BLACK,
}

# ─── CLASE PRINCIPAL ──────────────────────────────────────────────────────────
class Buscaminas:
    def __init__(self, filas: int, cols: int, minas: int):
        self.filas  = filas
        self.cols   = cols
        self.total_minas = minas
        self.minas_restantes = minas

        # Tablero: -1=mina, 0-8=número de minas vecinas
        self.tablero   = [[0] * cols for _ in range(filas)]
        self.revelado  = [[False] * cols for _ in range(filas)]
        self.bandera   = [[False] * cols for _ in range(filas)]
        self.primer_click = True
        self.game_over = False
        self.ganado    = False
        self.inicio    = None

    # ── Colocar minas después del primer click ────────────────────────────────
    def colocar_minas(self, safe_r: int, safe_c: int):
        seguras = {(safe_r + dr, safe_c + dc)
                   for dr in (-1,0,1) for dc in (-1,0,1)}
        posibles = [
            (r, c) for r in range(self.filas)
                   for c in range(self.cols)
                   if (r, c) not in seguras
        ]
        elegidas = random.sample(posibles, self.total_minas)
        for r, c in elegidas:
            self.tablero[r][c] = -1

        # Calcular números
        for r in range(self.filas):
            for c in range(self.cols):
                if self.tablero[r][c] == -1:
                    continue
                self.tablero[r][c] = sum(
                    1 for dr, dc in self._vecinos()
                    if 0 <= r+dr < self.filas and 0 <= c+dc < self.cols
                    and self.tablero[r+dr][c+dc] == -1
                )

    def _vecinos(self):
        return [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    # ── Revelar celda ─────────────────────────────────────────────────────────
    def revelar(self, r: int, c: int) -> bool:
        """Devuelve False si pisó una mina."""
        if not (0 <= r < self.filas and 0 <= c < self.cols):
            return True
        if self.revelado[r][c] or self.bandera[r][c]:
            return True

        if self.primer_click:
            self.primer_click = False
            self.colocar_minas(r, c)
            self.inicio = time.time()

        if self.tablero[r][c] == -1:
            self.revelado[r][c] = True
            self.game_over = True
            return False

        # BFS flood fill
        cola = [(r, c)]
        while cola:
            cr, cc = cola.pop()
            if self.revelado[cr][cc] or self.bandera[cr][cc]:
                continue
            self.revelado[cr][cc] = True
            if self.tablero[cr][cc] == 0:
                for dr, dc in self._vecinos():
                    nr, nc = cr+dr, cc+dc
                    if 0 <= nr < self.filas and 0 <= nc < self.cols:
                        if not self.revelado[nr][nc]:
                            cola.append((nr, nc))

        self._verificar_victoria()
        return True

    def _verificar_victoria(self):
        sin_revelar = sum(
            1 for r in range(self.filas)
              for c in range(self.cols)
              if not self.revelado[r][c]
        )
        if sin_revelar == self.total_minas:
            self.ganado = True

    # ── Bandera ───────────────────────────────────────────────────────────────
    def toggle_bandera(self, r: int, c: int):
        if not (0 <= r < self.filas and 0 <= c < self.cols):
            return
        if self.revelado[r][c]:
            return
        self.bandera[r][c] = not self.bandera[r][c]
        self.minas_restantes += -1 if self.bandera[r][c] else 1

    # ── Renderizar ────────────────────────────────────────────────────────────
    def render(self, mostrar_todo: bool = False):
        os.system('cls' if os.name == 'nt' else 'clear')

        elapsed = int(time.time() - self.inicio) if self.inicio else 0
        estado  = (f"{C.RED}💥 GAME OVER{C.RESET}" if self.game_over else
                   f"{C.GREEN}🏆 ¡VICTORIA!{C.RESET}" if self.ganado else
                   f"{C.YELLOW}🙂 En juego{C.RESET}")

        print(f"\n  {'─'*4} {C.BOLD}{C.GREEN}BUSCAMINAS{C.RESET} {'─'*4}")
        print(f"  💣 Minas: {C.RED}{self.minas_restantes:>3}{C.RESET}  "
              f"⏱ Tiempo: {C.CYAN}{elapsed:>3}s{C.RESET}  {estado}\n")

        # Cabecera de columnas
        header = "     " + "  ".join(f"{c:2}" for c in range(self.cols))
        print(f"{C.BOLD}{header}{C.RESET}")
        print("     " + "─" * (self.cols * 4))

        for r in range(self.filas):
            fila_str = f"{C.BOLD}{r:3}{C.RESET} │"
            for c in range(self.cols):
                fila_str += " " + self._celda(r, c, mostrar_todo) + " "
            print(fila_str)

        print()

    def _celda(self, r: int, c: int, mostrar_todo: bool) -> str:
        if self.revelado[r][c] or mostrar_todo:
            v = self.tablero[r][c]
            if v == -1:
                # Es mina y fue revelada
                if self.revelado[r][c] and self.game_over:
                    return f"{C.BG_RED}{C.BOLD}💣{C.RESET}"
                return f"{C.RED}💣{C.RESET}"
            elif v == 0:
                return f"{C.BLACK}·{C.RESET}"
            else:
                col = NUM_COLORS.get(v, C.WHITE)
                return f"{col}{C.BOLD}{v}{C.RESET}"
        elif self.bandera[r][c]:
            return f"{C.RED}🚩{C.RESET}"
        else:
            return f"{C.WHITE}#{C.RESET}"

    # ── Mostrar todas las minas al perder ─────────────────────────────────────
    def revelar_todo(self):
        self.render(mostrar_todo=True)


# ─── MENÚ DE DIFICULTAD ───────────────────────────────────────────────────────
def elegir_dificultad() -> tuple:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n  {C.BOLD}{C.GREEN}══ BUSCAMINAS ══{C.RESET}\n")
    for key, (nombre, f, c, m) in DIFICULTADES.items():
        print(f"  {C.YELLOW}[{key}]{C.RESET} {nombre:10}  {f}×{c}  minas={m}")
    print(f"  {C.YELLOW}[4]{C.RESET} Personalizado\n")

    opcion = input("  Elige dificultad (1-4): ").strip()

    if opcion in DIFICULTADES:
        return DIFICULTADES[opcion][1:]
    elif opcion == "4":
        try:
            f = int(input("  Filas  (5-30): "))
            c = int(input("  Cols   (5-50): "))
            m = int(input("  Minas  (1-{}): ".format(f*c-9)))
            f = max(5, min(30, f))
            c = max(5, min(50, c))
            m = max(1, min(f*c-9, m))
            return f, c, m
        except ValueError:
            pass
    return DIFICULTADES["1"][1:]  # default: fácil


# ─── LOOP PRINCIPAL ───────────────────────────────────────────────────────────
def jugar():
    filas, cols, minas = elegir_dificultad()
    juego = Buscaminas(filas, cols, minas)

    while not juego.game_over and not juego.ganado:
        juego.render()
        print("  Comandos: <fila col> para revelar | f <fila col> para bandera | q para salir")
        entrada = input("  > ").strip().lower().split()

        if not entrada:
            continue
        if entrada[0] == 'q':
            print("\n  ¡Hasta la próxima! 👋\n")
            return

        try:
            if entrada[0] == 'f' and len(entrada) == 3:
                r, c = int(entrada[1]), int(entrada[2])
                juego.toggle_bandera(r, c)
            elif len(entrada) == 2:
                r, c = int(entrada[0]), int(entrada[1])
                juego.revelar(r, c)
            else:
                print("  ⚠ Entrada no válida. Intenta de nuevo.")
        except (ValueError, IndexError):
            print("  ⚠ Coordenadas inválidas.")

    # Fin del juego
    juego.revelar_todo()
    if juego.ganado:
        elapsed = int(time.time() - juego.inicio)
        print(f"  {C.BG_GREEN}{C.BLACK} 🏆 ¡GANASTE en {elapsed}s! {C.RESET}\n")
    else:
        print(f"  {C.BG_RED}{C.WHITE} 💥 GAME OVER — pisaste una mina {C.RESET}\n")

    otra = input("  ¿Jugar de nuevo? (s/n): ").strip().lower()
    if otra == 's':
        jugar()
    else:
        print("\n  ¡Gracias por jugar! 👋\n")


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    jugar()
