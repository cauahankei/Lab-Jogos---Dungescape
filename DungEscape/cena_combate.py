# biblioteca q não sei mto bem como funciona, mas resolve 
# os problemas de achar as imagens
from pathlib import Path

from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.animation import Animation

from cartas import Carta


BASE_DIR = Path(__file__).resolve().parent
def asset_path(*parts):
    return str(BASE_DIR.joinpath(*parts))

# Cena do combate, onde todas as imagens são carregas, é o principal até agora
class CenaCombate:
    def __init__(self, window):
        self.window = window
        self.fundo = GameImage(asset_path("assets", "Background", "fundoteste01.jpeg"))

        # Linha de chão compartilhada — tudo que "pisa no chão" usa essa referência
        self.chao_y = self.window.height * 0.85

        # --- Visual Jogador ---
        NUM_FRAMES_JOGADOR = 8
        ESCALA_JOGADOR = 6.0

        self.jogador = Animation(asset_path("assets", "Player", "Idle.png"), NUM_FRAMES_JOGADOR)
        self.jogador.set_total_duration(600)
        self.jogador.set_scale(ESCALA_JOGADOR, ESCALA_JOGADOR)

        # .width/.height são do frame único e NÃO refletem a escala 
        # tem que multiplicar manualmente
        largura_final_jogador = self.jogador.width * ESCALA_JOGADOR
        altura_final_jogador = self.jogador.height * ESCALA_JOGADOR

        x_jogador = self.window.width * 0.2 - largura_final_jogador / 2
        y_jogador = self.chao_y - altura_final_jogador
        self.jogador.set_position(x_jogador, y_jogador)

        # --- Visual Inimigo ---
        NUM_FRAMES_INIMIGO = 4
        ESCALA_INIMIGO = 6.0

        self.inimigo = Animation(asset_path("assets", "Goblin", "Idle.png"), NUM_FRAMES_INIMIGO)
        self.inimigo.set_total_duration(600)
        self.inimigo.set_scale(ESCALA_INIMIGO, ESCALA_INIMIGO)

        largura_final_inimigo = self.inimigo.width * ESCALA_INIMIGO
        altura_final_inimigo = self.inimigo.height * ESCALA_INIMIGO

        x_inimigo = self.window.width * 0.8 - largura_final_inimigo / 2
        y_inimigo = self.chao_y - altura_final_inimigo
        self.inimigo.set_position(x_inimigo, y_inimigo)

        # --- Visual Mão de cartas ---
        ESCALA_CARTA = 1.5
        ESPACAMENTO_EXTRA = 20

        self.mao = [
            Carta(asset_path("assets", "Cartas", "carta1.png"), "Golpear", 1, 5),
            Carta(asset_path("assets", "Cartas", "carta2.png"), "Defender", 1, 0),
            Carta(asset_path("assets", "Cartas", "carta3.png"), "Bola de Fogo", 2, 12),
        ]

        for carta in self.mao:
            carta.set_scale(ESCALA_CARTA, ESCALA_CARTA)

        # Mesma regra vale pra carta: .width não reflete escala, multiplica manualmente
        largura_carta = self.mao[0].width * ESCALA_CARTA
        espacamento = largura_carta + ESPACAMENTO_EXTRA
        largura_total_mao = (len(self.mao) - 1) * espacamento + largura_carta
        margem_esquerda = self.window.width / 2 - largura_total_mao / 2
        altura_mao = self.window.height - 100

        for i, carta in enumerate(self.mao):
            carta.set_position(margem_esquerda + i * espacamento, altura_mao)

    def draw(self):
        self.fundo.draw()

        self.jogador.update()
        self.inimigo.update()

        self.inimigo.draw()
        self.jogador.draw()

        for carta in self.mao:
            carta.draw()

        #teste para achar posições de cada pixel, não é parte do jogo, apenas para debug
        if self.window.mouse.button_down(1):
            x, y = self.window.mouse.get_position()
            print(f"Clique em: ({x}, {y})")


janela = Window(1280, 720, "Teste de Composição")
tela = CenaCombate(janela)

while True:
    tela.draw()
    janela.update()