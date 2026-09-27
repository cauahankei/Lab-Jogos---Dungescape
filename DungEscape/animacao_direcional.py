# Extensão da Animation da engine pra suportar espelhamento horizontal
# (personagem virado pra esquerda). A PPlay não tem esse recurso pronto
# -- Animation.draw() não aceita flip, e usar escala negativa pra
# "inverter" quebra o pygame.transform.scale() por dentro (ele espera
# tamanhos positivos). Então resolvemos por fora, sem editar a PPlay:
# herdamos de Animation e sobrescrevemos só o draw(), copiando a lógica
# original e inserindo o pygame.transform.flip() antes de desenhar.
import pygame
from PPlay.animation import Animation
from PPlay.window import Window
from PPlay.camera import Camera


class AnimacaoDirecional(Animation):
    def __init__(self, caminho_imagem, total_frames, loop=True, virado_para_esquerda=False):
        super().__init__(caminho_imagem, total_frames, loop=loop)
        self.virado_para_esquerda = virado_para_esquerda

    def draw(self):
        # sem espelhamento, usa o draw() normal da engine sem modificação
        if not self.virado_para_esquerda:
            super().draw()
            return

        cam = Camera.get_instance()
        draw_x = cam.transform_x(self.x) if cam else self.x
        draw_y = cam.transform_y(self.y) if cam else self.y

        area_corte = pygame.Rect(self.frame_atual * self.width, 0, self.width, self.height)
        frame_surface = self.image.subsurface(area_corte).copy()
        frame_surface.set_alpha(self.transparency)

        if self.rotation != 0:
            frame_surface = pygame.transform.rotate(frame_surface, self.rotation)

        if self.scale_x != 1.0 or self.scale_y != 1.0:
            nova_w = max(1, int(self.width * self.scale_x))
            nova_h = max(1, int(self.height * self.scale_y))
            frame_surface = pygame.transform.scale(frame_surface, (nova_w, nova_h))

        # a única linha nova em relação ao draw() original: espelha
        # horizontalmente (True, False = espelha em X, não em Y)
        frame_surface = pygame.transform.flip(frame_surface, True, False)

        Window.get_screen().blit(frame_surface, (draw_x, draw_y))
