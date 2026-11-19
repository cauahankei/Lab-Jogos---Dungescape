import pygame
from PPlay.window import Window
from PPlay.effects import LightingSystem
import math

class FundoCombate:
    FATOR_PIXELACAO = 4

    def __init__(self, caminho):
        imagem = pygame.image.load(caminho).convert_alpha()
        largura, altura = imagem.get_size()
        tamanho_reduzido = (
            max(1, largura // self.FATOR_PIXELACAO),
            max(1, altura // self.FATOR_PIXELACAO),
        )
        reduzida = pygame.transform.scale(imagem, tamanho_reduzido)
        self.imagem = pygame.transform.scale(reduzida, (largura, altura))

        self.iluminacao = LightingSystem()

        self.tempo = 0.0

    def draw(self):
        Window.get_screen().blit(self.imagem, (0, 0))

        self.tempo += Window.get_instance().delta_time()

        intensidade_esquerda = int(15 + 7 * math.sin(self.tempo * 4))
        intensidade_direita = int(15 + 7 * math.sin(self.tempo * 3.3 + 1.2))

        self.iluminacao.lights = [
            (480, 300, 200, intensidade_esquerda),
            (830, 300, 200, intensidade_direita),
        ]
        self.iluminacao.draw_glow()
