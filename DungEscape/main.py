from PPlay.window import Window
from PPlay.scenemanager import SceneManager
from fluxo import iniciar_combate

janela = Window(1280, 720, "DungEscape")

iniciar_combate()

while True:
    SceneManager.run()
    janela.update()