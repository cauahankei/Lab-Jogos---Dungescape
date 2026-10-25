from PPlay.window import Window
from PPlay.scenemanager import SceneManager
from cena_combate import CenaCombate

janela = Window(1280, 720, "DungEscape")

# por enquanto só tem a cena de combate. Menu, mapa e loja entram aqui depois
SceneManager.change_scene(CenaCombate(["goblin"]))

while True:
    SceneManager.run()
    janela.update()
