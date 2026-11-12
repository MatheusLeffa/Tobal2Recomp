"""Automação de teste do Tobal2Recomp via servidor de debug TCP (porta 4370).

Uso:
    python tools/nav.py title          # pula o FMV e para na tela de título
    python tools/nav.py fight          # desde o boot: título -> Torneio -> 1ª luta
    python tools/nav.py menus          # já no título: Torneio -> 1ª luta
    python tools/nav.py state          # mostra o modo de vídeo atual
    python tools/nav.py shot ARQ.png   # print do quadro como o jogador vê

O jogo precisa ter sido aberto com PSX_DEBUG_SERVER=1.
"""
import json
import socket
import sys
import time

PORT = 4370

# Máscara invertida do controle do PS1 (0 = apertado).
BTN = {
    "select": 0, "start": 3, "up": 4, "right": 5, "down": 6, "left": 7,
    "l2": 8, "r2": 9, "l1": 10, "r1": 11,
    "triangle": 12, "circle": 13, "cross": 14, "square": 15,
}


def cmd(payload, timeout=10.0):
    with socket.create_connection(("127.0.0.1", PORT), timeout=timeout) as s:
        s.sendall((json.dumps(payload) + "\n").encode())
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode().strip().splitlines()[-1])


def press(name, frames=6):
    mask = 0xFFFF & ~(1 << BTN[name])
    cmd({"cmd": "press", "buttons": mask, "frames": frames})


def state():
    st = cmd({"cmd": "gpu_state"})
    return {k: st.get(k) for k in ("width", "height", "depth", "display_x", "display_y")}


def wait_until(pred, timeout, step=0.5, poke=None):
    end = time.time() + timeout
    while time.time() < end:
        st = state()
        if pred(st):
            return st
        if poke:
            poke()
        time.sleep(step)
    raise SystemExit(f"timeout esperando condição; último estado: {state()}")


def to_title():
    # Espera o servidor subir.
    end = time.time() + 30
    while True:
        try:
            state()
            break
        except OSError:
            if time.time() > end:
                raise
            time.sleep(0.5)
    # Espera o FMV (24 bits) começar, depois aperta Start até sair dele.
    wait_until(lambda s: s["depth"] == 24, 60)
    wait_until(lambda s: s["depth"] == 15, 120, step=1.0, poke=lambda: press("start", 4))
    time.sleep(3)
    # Se o FMV ainda estiver acabando, a tela de título aparece em seguida.
    return state()


def to_fight(from_title=False):
    if not from_title:
        to_title()
    for _ in range(3):  # Torneio -> seleção -> confirma personagem
        press("circle")
        time.sleep(4)
    time.sleep(8)
    return state()


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "state"
    if what == "title":
        print(to_title())
    elif what == "fight":
        print(to_fight())
    elif what == "menus":  # já está na tela de título
        print(to_fight(from_title=True))
    elif what == "state":
        print(state())
    elif what == "shot":
        print(cmd({"cmd": "present_shot", "path": sys.argv[2]}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
