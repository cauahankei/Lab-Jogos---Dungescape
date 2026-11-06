import math

import pygame


class IluminacaoTochas:
    def __init__(self, largura, altura, raio=230):
        self.largura = largura
        self.altura = altura
        self.raio = raio
        self.tempo = 0.0
        self._halo = self._criar_halo()
        self._halos_por_tamanho = {self._halo.get_size(): self._halo}
        self._fontes = (
            (478 / 1280, 282 / 720, 0.0),
            (831 / 1280, 282 / 720, 1.8),
        )

    def _criar_halo(self):
        diametro = self.raio * 2
        halo = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        centro = (self.raio, self.raio)

        for raio in range(self.raio, 0, -4):
            distancia = 1 - raio / self.raio
            alpha = round(58 * distancia * distancia)
            pygame.draw.circle(halo, (255, 158, 66, alpha), centro, raio)

        return halo

    def update(self, delta_time):
        self.tempo += delta_time

    def draw(self, surface):
        escala_x = surface.get_width() / 1280
        escala_y = surface.get_height() / 720
        escala_raio = min(escala_x, escala_y)
        tamanho = max(1, round(self.raio * 2 * escala_raio))
        tamanho_halo = (tamanho, tamanho)
        halo = self._halos_por_tamanho.get(tamanho_halo)
        if halo is None:
            halo = pygame.transform.smoothscale(self._halo, tamanho_halo)
            self._halos_por_tamanho[tamanho_halo] = halo

        for x_relativo, y_relativo, fase in self._fontes:
            oscilacao = (
                0.78
                + 0.13 * math.sin(self.tempo * 11.0 + fase)
                + 0.09 * math.sin(self.tempo * 23.0 + fase * 1.7)
            )
            halo.set_alpha(round(255 * oscilacao))
            x = round(x_relativo * surface.get_width() - tamanho / 2)
            y = round(y_relativo * surface.get_height() - tamanho / 2)
            surface.blit(halo, (x, y))
