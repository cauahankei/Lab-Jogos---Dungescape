from PPlay.window import Window
from PPlay.scenemanager import SceneManager
from menu import CenaMenu

janela = Window(1280, 720, "DungEscape")

SceneManager.change_scene(CenaMenu())

while True:
    SceneManager.run()
    janela.update()