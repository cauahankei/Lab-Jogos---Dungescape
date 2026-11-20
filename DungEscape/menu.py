import pygame
from PPlay.scenemanager import Scene, SceneManager
from PPlay.sprite import Sprite
from PPlay.uikit import Button, ProgressBar
from PPlay.window import Window
from utils import asset_path
from efeitos_visuais import FundoCombate, pixelizar_imagem
from sons import (
    definir_volume_geral,
    iniciar_musica_menu,
    obter_volume_geral,
    parar_musica_menu,
)
from hud import centralizado
import fonte_pixel


class CenaComBackground(Scene):
    def __init__(self, caminho_background=None, pixelizado=False):
        super().__init__()
        caminho_background = caminho_background or asset_path(
            "assets", "Background", "background.png"
        )
        if pixelizado:
            imagem = pygame.image.load(caminho_background).convert_alpha()
            imagem = pixelizar_imagem(imagem, FundoCombate.FATOR_PIXELACAO)
            self.background = pygame.transform.scale(
                imagem, (self.janela.largura, self.janela.altura)
            )
        else:
            self.background = Sprite(caminho_background)
            self.background.set_position(0, 0)
            self.background.set_scale(
                self.janela.largura / self.background.width,
                self.janela.altura / self.background.height,
            )

    def desenhar_background(self):
        if isinstance(self.background, pygame.Surface):
            Window.get_screen().blit(self.background, (0, 0))
        else:
            self.background.draw()


def criar_botao(texto, x, y):
    botao = Button(220, 48, texto, (40, 44, 58), (72, 78, 98))
    botao.set_position(x, y)
    return botao


class BotaoImagem(Button):
    ESCALA = 2

    def __init__(self, caminho):
        self.imagem = pygame.image.load(caminho).convert_alpha()
        largura, altura = self.imagem.get_size()
        super().__init__(largura * self.ESCALA, altura * self.ESCALA)

    def draw(self):
        escala = 0.96 if self.pressed else 1.06 if self.hovered else 1
        tamanho = (
            max(1, int(self.width * escala)),
            max(1, int(self.height * escala)),
        )
        imagem = pygame.transform.scale(self.imagem, tamanho)

        if self.pressed:
            imagem.fill((205, 205, 205), special_flags=pygame.BLEND_RGB_MULT)
        elif self.hovered:
            imagem.fill((20, 20, 20), special_flags=pygame.BLEND_RGB_ADD)

        retangulo = imagem.get_rect(
            center=(self.x + self.width / 2, self.y + self.height / 2)
        )
        Window.get_screen().blit(imagem, retangulo)


class CenaMenu(CenaComBackground):
    ignorar_esc_menu = True

    def __init__(self):
        super().__init__(
            asset_path("assets", "Background", "Fundo_menu2.png"),
            pixelizado=True,
        )
        iniciar_musica_menu()
        self.janela = Window.get_instance()
        self.logo = Sprite(asset_path("assets", "Background", "logo.png"))
        self.logo.set_scale(2.5, 2.5)
        self.logo.set_position(
            (self.janela.largura - self.logo.width * 2.5) / 2,
            self.janela.altura * 0.12,
        )

        self.jogar = BotaoImagem(
            asset_path("assets", "Background", "Play.png")
        )
        self.configuracoes = BotaoImagem(
            asset_path("assets", "Background", "Gear.png")
        )
        self.sair = BotaoImagem(
            asset_path("assets", "Background", "Exit.png")
        )
        self.botoes = [self.jogar, self.configuracoes, self.sair]
        y = self.janela.altura * 0.42
        for indice, botao in enumerate(self.botoes):
            botao.set_position(
                (self.janela.largura - botao.width) / 2,
                y + indice * (botao.height + 10),
            )

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