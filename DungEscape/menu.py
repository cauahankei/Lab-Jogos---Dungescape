from PPlay.scenemanager import Scene, SceneManager
from PPlay.sprite import Sprite
from PPlay.uikit import Button, ProgressBar
from PPlay.window import Window
from utils import asset_path
from sons import (
    definir_volume_geral,
    iniciar_musica_menu,
    obter_volume_geral,
    parar_musica_menu,
)
from hud import centralizado
import fonte_pixel


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
        self.configuracoes = criar_botao(
            "CONFIGURACOES", x, self.janela.altura / 2 + 64
        )
        self.sair = criar_botao("SAIR", x, self.janela.altura / 2 + 128)
        self.botoes = [self.jogar, self.configuracoes, self.sair]

    def loop(self):
        for botao in self.botoes:
            botao.update()

        if self.jogar.is_clicked():
            parar_musica_menu()
            from fluxo import iniciar_jornada
            iniciar_jornada()

        elif self.configuracoes.is_clicked():
            SceneManager.change_scene(CenaConfiguracoes())

        elif self.sair.is_clicked():
            self.janela.close()

    def draw(self):
        self.desenhar_background()
        self.logo.draw()
        for botao in self.botoes:
            botao.draw()


class CenaConfiguracoes(CenaComBackground):
    PASSO_VOLUME = 10

    def __init__(self):
        super().__init__()
        self.janela = Window.get_instance()
        self.volume = obter_volume_geral()

        largura_barra = 400
        x_barra = (self.janela.largura - largura_barra) / 2
        self.barra_volume = ProgressBar(
            largura_barra, 24, cor_barra=fonte_pixel.DOURADO,
            cor_fundo=(45, 35, 35),
        )
        self.barra_volume.set_position(x_barra, 340)

        self.botao_diminuir = Button(64, 48, "-", (88, 58, 44), (140, 92, 60))
        self.botao_diminuir.set_position(x_barra - 80, 328)
        self.botao_aumentar = Button(64, 48, "+", (88, 58, 44), (140, 92, 60))
        self.botao_aumentar.set_position(x_barra + largura_barra + 16, 328)
        self.botao_voltar = criar_botao(
            "VOLTAR", (self.janela.largura - 220) / 2, 500
        )

    def loop(self):
        self.botao_diminuir.update()
        self.botao_aumentar.update()
        self.botao_voltar.update()

        if self.botao_diminuir.is_clicked():
            self.volume = max(0, self.volume - self.PASSO_VOLUME)
            definir_volume_geral(self.volume)
        elif self.botao_aumentar.is_clicked():
            self.volume = min(100, self.volume + self.PASSO_VOLUME)
            definir_volume_geral(self.volume)
        elif self.botao_voltar.is_clicked():
            SceneManager.change_scene(CenaMenu())

    def draw(self):
        self.desenhar_background()
        centralizado("CONFIGURACOES", 200, 5, fonte_pixel.DOURADO)
        centralizado("VOLUME GERAL", 280, 3, fonte_pixel.CREME)
        self.barra_volume.set_value(self.volume)
        self.barra_volume.draw()
        centralizado(f"{self.volume}%", 390, 3, fonte_pixel.CREME)
        self.botao_diminuir.draw()
        self.botao_aumentar.draw()
        self.botao_voltar.draw()