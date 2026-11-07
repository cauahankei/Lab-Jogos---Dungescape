from PPlay.scenemanager import Scene
from PPlay.sprite import Sprite
from PPlay.uikit import Button
from PPlay.window import Window
from utils import asset_path


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
        self.janela = Window.get_instance()
        self.logo = Sprite(asset_path("assets", "Background", "logo.png"))
        escala_logo = min(
            self.janela.largura * 0.7 / self.logo.width,
            self.janela.altura * 0.32 / self.logo.height,
        )
        self.logo.set_scale(escala_logo, escala_logo)
        self.logo.set_position(
            (self.janela.largura - self.logo.width * escala_logo) / 2,
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
            from fluxo import iniciar_combate
            iniciar_combate()

        elif self.sair.is_clicked():
            self.janela.close()

    def draw(self):
        self.desenhar_background()
        self.logo.draw()
        for botao in self.botoes:
            botao.draw()