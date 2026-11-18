from PPlay.scenemanager import Scene
from PPlay.sprite import Sprite
from PPlay.uikit import Button
from PPlay.window import Window
from utils import asset_path
from sons import iniciar_musica_menu, parar_musica_menu


class CenaComBackground(Scene):
    def __init__(self):
        super().__init__()
        self.background = Sprite(
            asset_path("assets", "Background", "background.png")
        )
        self.background.set_position(0, 0)
        self.background.set_scale(
            self.janela.largura / self.background.width,
            self.janela.altura / self.background.height,
        )

    def desenhar_background(self):
        self.background.draw()


def criar_botao(texto, x, y):
    botao = Button(220, 48, texto, (40, 44, 58), (72, 78, 98))
    botao.set_position(x, y)
    return botao


class CenaMenu(CenaComBackground):
    def __init__(self):
        super().__init__()
        iniciar_musica_menu()
        self.janela = Window.get_instance()
        self.logo = Sprite(asset_path("assets", "Background", "logo.png"))
        self.logo.set_scale(2.5, 2.5)
        self.logo.set_position(
            (self.janela.largura - self.logo.width * 2.5) / 2,
            self.janela.altura * 0.12,
        )

        x = (self.janela.largura - 220) / 2
        self.jogar = criar_botao("JOGAR", x, self.janela.altura / 2)
        self.sair = criar_botao("SAIR", x, self.janela.altura / 2 + 64)
        self.botoes = [self.jogar, self.sair]

    def loop(self):
        for botao in self.botoes:
            botao.update()

        if self.jogar.is_clicked():
            parar_musica_menu()
            from fluxo import iniciar_jornada
            iniciar_jornada()

        elif self.sair.is_clicked():
            self.janela.close()

    def draw(self):
        self.desenhar_background()
        self.logo.draw()
        for botao in self.botoes:
            botao.draw()