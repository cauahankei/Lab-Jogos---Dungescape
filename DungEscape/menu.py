import pygame

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
        x = (self.janela.largura - 220) / 2
        self.jogar = criar_botao("JOGAR", x, self.janela.altura / 2)
        self.sair = criar_botao("SAIR", x, self.janela.altura / 2 + 64)
        self.botoes = [self.jogar, self.sair]
        self.fonte_titulo = pygame.font.SysFont("Arial", 64, bold=True)

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
        titulo = self.fonte_titulo.render("DUNGESCAPE", True, (242, 230, 201))
        titulo_rect = titulo.get_rect(
            center=(self.janela.largura / 2, self.janela.altura / 2 - 100)
        )
        self.janela.screen.blit(titulo, titulo_rect)
        for botao in self.botoes:
            botao.draw()