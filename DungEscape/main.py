from PPlay.window import Window
from PPlay.scenemanager import SceneManager
from fluxo import iniciar_combate
from color_quantization import ColorQuantizer

filtro_cores = ColorQuantizer((1280, 720), levels=6, strength=0.25)
janela = Window(1280, 720, "DungEscape", frame_processor=filtro_cores.apply)

iniciar_combate()

while True:
    SceneManager.run()
    janela.update()