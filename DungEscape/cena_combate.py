#utilidade
import math
from utils import asset_path
#pplay
from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.uikit import ProgressBar
#autoral
from cartas import criar_corte_basico, criar_escudo
from combatente import Player, Goblin
from ator import AtorAnimado

# quanto a carta sobe (em pixels) e quao rapido ela sobe/desce quando o mouse passa por cima
ALTURA_HOVER = 40
VELOCIDADE_HOVER = 12

# Cena do combate, onde todas as imagens são carregas, é o principal até agora
class CenaCombate:
    def __init__(self, window):
        self.window = window
        self.fundo = GameImage(asset_path("assets", "Background", "background.png"))

        # Linha de chão compartilhada — tudo que "pisa no chão" usa essa referência
        self.chao_y = self.window.altura * 0.85

        # Fichas de combate (dados logicos: vida, escudo, AP, dano)
        self.status_jogador = Player()
        self.status_goblin = Goblin()


        self.jogador = AtorAnimado("player", self.window.largura * 0.2, self.chao_y)
        self.goblin = AtorAnimado("goblin", self.window.largura * 0.8, self.chao_y, virado_para_esquerda=True)


        self.goblin_ativo = True

        # --- Barras de vida/energia (PPlay.uikit.ProgressBar) ---
        self.barra_vida_jogador = ProgressBar(150, 14, cor_barra=(90, 190, 90), cor_fundo=(35, 20, 20))
        self.barra_vida_jogador.valor_max = self.status_jogador.vida_max

        self.barra_ap_jogador = ProgressBar(90, 10, cor_barra=(80, 140, 230), cor_fundo=(20, 20, 40))
        self.barra_ap_jogador.valor_max = self.status_jogador.ap_max

        self.barra_vida_goblin = ProgressBar(120, 12, cor_barra=(190, 60, 60), cor_fundo=(30, 15, 15))
        self.barra_vida_goblin.valor_max = self.status_goblin.vida_max

        self._posicionar_barras()

        # --- Visual Mão de cartas ---
        ESCALA_CARTA = 1.5
        ESPACAMENTO_EXTRA = 20

        self.mao = [
            criar_corte_basico(),
            criar_escudo(),
        ]


        self.largura_carta = self.mao[0].width * ESCALA_CARTA
        self.altura_carta = self.mao[0].height * ESCALA_CARTA
        espacamento = self.largura_carta + ESPACAMENTO_EXTRA
        largura_total_mao = (len(self.mao) - 1) * espacamento + self.largura_carta
        margem_esquerda = self.window.largura / 2 - largura_total_mao / 2
        topo_mao = self.window.altura - 100

        #posicionamento das cartas, ancorado a uma "linha" superior
        for i, carta in enumerate(self.mao):
            x = margem_esquerda + i * espacamento
            angulo = ((x + self.largura_carta / 2)- (margem_esquerda + largura_total_mao / 2)) * -0.05

            theta = math.radians(abs(angulo))
            altura_rotacionada = (self.largura_carta * math.sin(theta) + self.altura_carta * math.cos(theta))

            y = topo_mao + (altura_rotacionada - self.altura_carta) / 2

            carta.set_scale(ESCALA_CARTA, ESCALA_CARTA)
            carta.set_position(x, y)
            carta.set_rotation(angulo)
            carta.y_repouso = topo_mao



    # Posição das barras é FIXA (baseada no Idle de cada um) -- não usa a
    # altura da animação atual, senão elas ficariam pulando de lugar toda
    # vez que o player ataca ou o goblin reage/morre.
    def _posicionar_barras(self):
        centro_x_jogador = self.jogador.x_centro
        topo_jogador = self.jogador.topo_idle()

        self.barra_vida_jogador.set_position(
            centro_x_jogador - self.barra_vida_jogador.width / 2, topo_jogador - 34)

        self.barra_ap_jogador.set_position(
            centro_x_jogador - self.barra_ap_jogador.width / 2, topo_jogador - 18)

        centro_x_goblin = self.goblin.x_centro
        topo_goblin = self.goblin.topo_idle()
        self.barra_vida_goblin.set_position(
            centro_x_goblin - self.barra_vida_goblin.width / 2, topo_goblin - 24
        )

    def _mouse_sobre_carta(self, carta):
        mx, my = self.window.mouse.get_position()
        return (
            carta.x <= mx <= carta.x + self.largura_carta
            and carta.y <= my <= carta.y + self.altura_carta
        )

    # aplica o efeito da carta jogada: dispara a animação de ataque do
    # player quando a carta causa dano, aplica o efeito na ficha, e então
    # decide a reação do Goblin -- morre (se a vida zerou) ou leva um
    # Take Hit (se sobreviveu ao golpe) -- ao mesmo tempo que o player
    # ainda está no meio do próprio golpe.
    def _jogar_carta(self, carta):
        if not self.goblin_ativo:
            return  # combate encerrado (goblin morto/morrendo): nada mais pode ser jogado

        if not self.status_jogador.gasta_ap(carta.custo):
            print(f"AP insuficiente para jogar {carta.nome}!")
            return

        if carta.dano > 0:
            self.jogador.tocar("attack")

        carta.usar(self.status_jogador, self.status_goblin)

        print(
            f"{carta.nome} usada -> "
            f"Jogador: HP={self.status_jogador.vida}/{self.status_jogador.vida_max} "
            f"Escudo={self.status_jogador.escudo} "
            f"AP={self.status_jogador.ap}/{self.status_jogador.ap_max} | "
            f"Goblin: HP={self.status_goblin.vida}/{self.status_goblin.vida_max}"
        )

        if carta.dano > 0:
            if not self.status_goblin.is_alive():
                self.goblin.tocar("death")
                self.goblin_ativo = False
            else:
                self.goblin.tocar("takehit")

    def draw(self):
        self.fundo.draw()
        dt = self.window.delta_time()

        # --- Processa o input das cartas PRIMEIRO: se algo mudar aqui
        # (dano, animação de ataque/reação/morte), o resto do draw() já
        # desenha o estado atualizado neste MESMO frame, sem 1 frame de
        # atraso nas animações/barras (o desenho das cartas em si fica lá
        # embaixo, por cima de tudo). ---
        for carta in self.mao:
            if self.goblin_ativo:
                sobre_carta = self._mouse_sobre_carta(carta)
                alvo_y = carta.y_repouso - ALTURA_HOVER if sobre_carta else carta.y_repouso
                carta.y += (alvo_y - carta.y) * min(1, VELOCIDADE_HOVER * dt)

                if sobre_carta and self.window.mouse.button_down(1):
                    self._jogar_carta(carta)

        self.jogador.update()
        self.jogador.draw()

        self.goblin.update()
        self.goblin.draw()
        
        # --- Barras de vida/energia ---
        self.barra_vida_jogador.set_value(self.status_jogador.vida)
        self.barra_ap_jogador.set_value(self.status_jogador.ap)
        self.barra_vida_jogador.draw()
        self.barra_ap_jogador.draw()

        if self.goblin_ativo:
            self.barra_vida_goblin.set_value(self.status_goblin.vida)
            self.barra_vida_goblin.draw()

        # --- Cartas: só o desenho agora (o input já foi tratado lá em cima) ---
        for carta in self.mao:
            carta.draw()

        #teste para achar posições de cada pixel, não é parte do jogo, apenas para debug
        if self.window.mouse.button_down(1):
            x, y = self.window.mouse.get_position()
            print(f"Clique em: ({x}, {y})")


if __name__ == "__main__":
    janela = Window(1280, 720, "Teste de Composição")
    tela = CenaCombate(janela)

    while True:
        tela.draw()
        janela.update()