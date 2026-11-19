from PPlay.scenemanager import Scene
from PPlay.uikit import Button
from utils import asset_path
from efeitos_visuais import FundoCombate
from cartas import sortear_recompensa, TAMANHO_CARTA
from hud import centralizado
from fluxo import depois_da_recompensa
import fonte_pixel

ESCALA = 4            # escala inteira, para o pixel art ficar nítido
ESPACO = 80           # espaço entre as cartas
SUBIDA_HOVER = 12     # quanto a carta sobe quando o mouse está em cima


class CenaRecompensa(Scene):
    def __init__(self, player, ao_concluir=None):
        super().__init__()
        self.player = player
        self.ao_concluir = ao_concluir
        self.fundo = FundoCombate(asset_path("assets", "Background", "background.png"))

        self.cartas = sortear_recompensa("normal", 2)
        for carta in self.cartas:
            carta.set_scale(ESCALA, ESCALA)

        self.largura = TAMANHO_CARTA[0] * ESCALA
        self.altura = TAMANHO_CARTA[1] * ESCALA
        total = len(self.cartas) * self.largura + (len(self.cartas) - 1) * ESPACO
        self.x_inicial = (self.janela.width - total) / 2
        self.y = 150

        self.botao_pular = Button(150, 44, "Pular", cor_base=(88, 58, 44), cor_hover=(140, 92, 60))
        self.botao_pular.set_position((self.janela.width - 150) / 2, self.janela.height - 44 - 40)

        self.hover = None     # posição da carta sob o mouse (0, 1...) ou None

    def _x_da_carta(self, i):
        return self.x_inicial + i * (self.largura + ESPACO)

    def loop(self):
        mx, my = self.mouse.get_position()

        self.hover = None
        for i in range(len(self.cartas)):
            x = self._x_da_carta(i)
            if x <= mx <= x + self.largura and self.y <= my <= self.y + self.altura:
                self.hover = i

        self.botao_pular.update()
        if self.botao_pular.is_clicked():
            if self.ao_concluir is None:
                depois_da_recompensa(self.player)
            else:
                self.ao_concluir(self.player)
            return

        if self.hover is not None and self.mouse.button_down(self.mouse.LEFT):
            self.player.baralho.adicionar(self.cartas[self.hover])
            if self.ao_concluir is None:
                depois_da_recompensa(self.player)
            else:
                self.ao_concluir(self.player)

    def draw(self):
        self.fundo.draw()
        centralizado("ESCOLHA UMA CARTA PARA ADICIONAR AO BARALHO", 50, 5, fonte_pixel.CREME)

        for i in range(len(self.cartas)):
            subida = 0
            if i == self.hover:
                subida = SUBIDA_HOVER
            self.cartas[i].set_position(self._x_da_carta(i), self.y - subida)
            self.cartas[i].draw()

        self.botao_pular.draw()
