from PPlay.window import Window
from PPlay.scenemanager import SceneManager
from cena_combate import CenaCombate
from encontros import sortear_encontro

janela = Window(1280, 720, "DungEscape")

# por enquanto só tem a cena de combate. Menu, mapa e loja entram aqui depois
SceneManager.change_scene(CenaCombate(sortear_encontro("normal")))

while True:
    SceneManager.run()
    janela.update()
