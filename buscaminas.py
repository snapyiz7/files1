import random, os, time

# ─── CONFIGURACIÓN ─────────────────────────────────────────
DIFICULTADES = {
    "1": ("FÁCIL",   9,  9,  10),
    "2": ("MEDIO",  16, 16,  40),
    "3": ("DIFÍCIL",16, 30,  99),
}

# ─── COLORES ANSI ──────────────────────────────────────────
class C:
    RESET="\033[0m"; BOLD="\033[1m"
    RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
    BLUE="\033[94m"; MAGENTA="\033[95m"; CYAN="\033[96m"
    WHITE="\033[97m"; BLACK="\033[30m"
    BG_RED="\033[41m"; BG_GREEN="\033[42m"

NUM_COLORS = {
    1:C.GREEN,2:C.CYAN,3:C.RED,4:C.MAGENTA,
    5:C.YELLOW,6:C.BLUE,7:C.WHITE,8:C.BLACK
}

# ─── CLASE JUEGO ───────────────────────────────────────────
class Buscaminas:

    def __init__(self, filas, cols, minas):

        self.filas = filas
        self.cols = cols
        self.total_minas = minas
        self.minas_restantes = minas

        self.tablero=[[0]*cols for _ in range(filas)]
        self.revelado=[[False]*cols for _ in range(filas)]
        self.bandera=[[False]*cols for _ in range(filas)]

        self.primer_click=True
        self.game_over=False
        self.ganado=False
        self.inicio=None
        self.pausado=False
        self.tiempo_pausa=0

    # ─── VECINOS ───────────────────────────────────────────
    def _vecinos(self):
        return [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    # ─── COLOCAR MINAS ─────────────────────────────────────
    def colocar_minas(self, safe_r, safe_c):

        seguras={(safe_r+dr,safe_c+dc) for dr in(-1,0,1) for dc in(-1,0,1)}

        posibles=[(r,c)
            for r in range(self.filas)
            for c in range(self.cols)
            if (r,c) not in seguras]

        for r,c in random.sample(posibles,self.total_minas):
            self.tablero[r][c]=-1

        for r in range(self.filas):
            for c in range(self.cols):

                if self.tablero[r][c]==-1: continue

                self.tablero[r][c]=sum(
                    1 for dr,dc in self._vecinos()
                    if 0<=r+dr<self.filas and
                       0<=c+dc<self.cols and
                       self.tablero[r+dr][c+dc]==-1
                )

    # ─── REVELAR ───────────────────────────────────────────
    def revelar(self,r,c):

        if not (0<=r<self.filas and 0<=c<self.cols): return True
        if self.revelado[r][c] or self.bandera[r][c]: return True

        if self.primer_click:
            self.primer_click=False
            self.colocar_minas(r,c)
            self.inicio=time.time()

        if self.tablero[r][c]==-1:
            self.revelado[r][c]=True
            self.game_over=True
            return False

        cola=[(r,c)]

        while cola:
            cr,cc=cola.pop()

            if self.revelado[cr][cc] or self.bandera[cr][cc]:
                continue

            self.revelado[cr][cc]=True

            if self.tablero[cr][cc]==0:

                for dr,dc in self._vecinos():

                    nr,nc=cr+dr,cc+dc

                    if 0<=nr<self.filas and 0<=nc<self.cols:
                        if not self.revelado[nr][nc]:
                            cola.append((nr,nc))

        self._verificar_victoria()
        return True

    # ─── VICTORIA ──────────────────────────────────────────
    def _verificar_victoria(self):

        ocultas=sum(
            1 for r in range(self.filas)
              for c in range(self.cols)
              if not self.revelado[r][c]
        )

        if ocultas==self.total_minas:
            self.ganado=True

    # ─── BANDERA ───────────────────────────────────────────
    def toggle_bandera(self,r,c):

        if not(0<=r<self.filas and 0<=c<self.cols): return
        if self.revelado[r][c]: return

        self.bandera[r][c]=not self.bandera[r][c]
        self.minas_restantes+= -1 if self.bandera[r][c] else 1

    # ─── SUGERENCIA ────────────────────────────────────────
    def sugerencia(self):

        seguras=[(r,c)
            for r in range(self.filas)
            for c in range(self.cols)
            if not self.revelado[r][c] and self.tablero[r][c]!=-1]

        if not seguras: return None

        return random.choice(seguras)

    # ─── PAUSA ─────────────────────────────────────────────
    def pausar(self):

        if not self.inicio: return

        if not self.pausado:
            self.tiempo_pausa=time.time()
            self.pausado=True
        else:
            pausa=time.time()-self.tiempo_pausa
            self.inicio+=pausa
            self.pausado=False

    # ─── RENDER ────────────────────────────────────────────
    def render(self,mostrar_todo=False):

        os.system('cls' if os.name=='nt' else 'clear')

        elapsed=int(time.time()-self.inicio) if self.inicio else 0

        estado = (
            f"{C.RED}💥 GAME OVER{C.RESET}" if self.game_over else
            f"{C.GREEN}🏆 ¡VICTORIA!{C.RESET}" if self.ganado else
            f"{C.YELLOW}🙂 En juego{C.RESET}"
        )

        print(f"\n  {C.BOLD}{C.GREEN}BUSCAMINAS{C.RESET}")
        print(f"  💣 Minas:{self.minas_restantes}  ⏱ {elapsed}s  {estado}\n")

        header="    "+" ".join(f"{c:2}" for c in range(self.cols))
        print(header)

        for r in range(self.filas):

            fila=f"{r:2} |"

            for c in range(self.cols):
                fila+=self._celda(r,c,mostrar_todo)+" "

            print(fila)

        print()

    def _celda(self,r,c,mostrar):

        if self.revelado[r][c] or mostrar:

            v=self.tablero[r][c]

            if v==-1: return f"{C.RED}💣{C.RESET}"
            if v==0: return "·"

            col=NUM_COLORS.get(v,C.WHITE)
            return f"{col}{v}{C.RESET}"

        if self.bandera[r][c]:
            return f"{C.YELLOW}🚩{C.RESET}"

        return "#"

    def revelar_todo(self):
        self.render(True)

# ─── JUEGO ────────────────────────────────────────────────
def jugar():

    filas,cols,minas=DIFICULTADES["1"][1:]

    juego=Buscaminas(filas,cols,minas)

    while not juego.game_over and not juego.ganado:

        juego.render()

        print("comandos:")
        print("  fila col → revelar")
        print("  f fila col → bandera")
        print("  s → sugerencia")
        print("  p → pausa")
        print("  h → ayuda")
        print("  q → salir")

        cmd=input("> ").split()

        if not cmd: continue

        if cmd[0]=="q":
            return

        if cmd[0]=="h":
            input("\nDescubre todas las casillas sin minas.\nLos números indican minas cercanas.\nENTER...")
            continue

        if cmd[0]=="p":
            juego.pausar()
            continue

        if cmd[0]=="s":
            sug=juego.sugerencia()
            if sug:
                print(f"Sugerencia: {sug}")
                time.sleep(2)
            continue

        try:

            if cmd[0]=="f":
                r,c=int(cmd[1]),int(cmd[2])
                juego.toggle_bandera(r,c)

            else:
                r,c=int(cmd[0]),int(cmd[1])
                juego.revelar(r,c)

        except:
            pass

    juego.revelar_todo()

    if juego.ganado:
        print("\n🏆 GANASTE\n")
    else:
        print("\n💥 GAME OVER\n")


if __name__=="__main__":
    jugar()