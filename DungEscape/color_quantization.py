import pygame


class ColorQuantizer:
    """Reduz as cores de uma superfície para uma paleta RGB uniforme."""

    def __init__(self, size, levels=5, strength=0.2):
        if isinstance(levels, bool) or not isinstance(levels, int) or not 2 <= levels <= 6:
            raise ValueError("levels deve ser um inteiro entre 2 e 6")
        if isinstance(strength, bool) or not isinstance(strength, (int, float)) or not 0 <= strength <= 1:
            raise ValueError("strength deve ser um número entre 0 e 1")

        channel_values = [
            round(index * 255 / (levels - 1))
            for index in range(levels)
        ]
        palette = [
            (red, green, blue)
            for red in channel_values
            for green in channel_values
            for blue in channel_values
        ]
        palette.extend([(0, 0, 0)] * (256 - len(palette)))

        self._palette = palette
        self.strength = strength
        self._indexed_surface = self._create_indexed_surface(size)
        self._quantized_surface = pygame.Surface(size)
        self._quantized_surface.set_alpha(round(strength * 255))
        self._surface = pygame.Surface(size)

    def _create_indexed_surface(self, size):
        surface = pygame.Surface(size, depth=8)
        surface.set_palette(self._palette)
        return surface

    def apply(self, source):
        if source.get_size() != self._surface.get_size():
            size = source.get_size()
            self._indexed_surface = self._create_indexed_surface(size)
            self._quantized_surface = pygame.Surface(size)
            self._quantized_surface.set_alpha(round(self.strength * 255))
            self._surface = pygame.Surface(size)

        self._indexed_surface.blit(source, (0, 0))
        self._quantized_surface.blit(self._indexed_surface, (0, 0))
        self._surface.blit(source, (0, 0))
        self._surface.blit(self._quantized_surface, (0, 0))
        return self._surface
