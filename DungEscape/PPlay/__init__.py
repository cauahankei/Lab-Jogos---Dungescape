import os

# 1. Verifica integridade da Engine Nova
COMPONENTES_VITAIS =[
    "window.py", "sprite.py", "physics.py", "gameimage.py", 
    "camera.py", "collision.py", "animation.py"
]

def verificar_integridade():
    diretorio_atual = os.path.dirname(__file__)
    faltando =[]
    for arquivo in COMPONENTES_VITAIS:
        if not os.path.exists(os.path.join(diretorio_atual, arquivo)):
            faltando.append(arquivo)
    if faltando:
        print(f"ERRO DE INTEGRIDADE: Faltando {faltando}")

verificar_integridade()

# =========================================================
__all__ = [
    "window", "sprite", "physics", "gameimage",
    "camera", "collision", "animation", "object_group",
    "keyboard", "mouse", "sound", "effects",
    "uikit", "timer", "navigation", "tween", "parallax",
    "tilemap", "particles", "scenemanager", "gameobject", "point",
]