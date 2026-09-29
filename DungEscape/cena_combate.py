#utilidade
import math
from utils import asset_path
#pplay
from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.uikit import ProgressBar
#autoral
from cartas import criar_corte_basico, criar_escudo
from combatente import Player, Inimigo1
from ator import AtorAnimado
from gerenciador_combate import GerenciadorCombate


# Cena do combate, onde todas as imagens são carregas, é o principal até agora
class CenaCombate:
    def __init__(self, window):
        self.window = window
        self.fundo = GameImage(asset_path("assets", "Background", "background.png"))

        # Linha de chão compartilhada — tudo que "pisa no chão" usa essa referência
        self.chao_y = self.window.altura * 0.85

        # Fichas de combate (dados logicos: vida, escudo, AP, dano)
        self.status_jogador = Player()
        self.status_inimigo1 = Inimigo1()
        self.gerenciador = GerenciadorCombate(
            self.status_jogador, [self.status_inimigo1]
        )


        self.jogador = AtorAnimado("player", self.window.largura * 0.2, self.chao_y)
        self.inimigo1 = AtorAnimado("goblin", self.window.largura * 0.8, self.chao_y, virado_para_esquerda=True)


        self.inimigo1_ativo = True
        self._takehit_pendente = False
        self._timer_takehit = 0.0

        # --- Barras de vida/energia (PPlay.uikit.ProgressBar) ---
        self.barra_vida_jogador = ProgressBar(150, 14, cor_barra=(90, 190, 90), cor_fundo=(35, 20, 20))
        self.barra_vida_jogador.valor_max = self.status_jogador.vida_max

        self.barra_ap_jogador = ProgressBar(90, 10, cor_barra=(80, 140, 230), cor_fundo=(20, 20, 40))
        self.barra_ap_jogador.valor_max = self.status_jogador.ap_max

        self.barra_vida_inimigo1 = ProgressBar(120, 12, cor_barra=(190, 60, 60), cor_fundo=(30, 15, 15))
        self.barra_vida_inimigo1.valor_max = self.status_inimigo1.vida_max

        self._posicionar_barras()

        # passar_turno
        self.botao_passar_turno = GameImage(asset_path("assets","hud","botao_passar_turno_new.png"))
        self.botao_passar_turno.set_position(
            self.window.width - self.botao_passar_turno.width - 30,
            self.window.height - self.botao_passar_turno.height - 10)


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
    # vez que o player ataca ou o inimigo1 reage/morre.
    def _posicionar_barras(self):
        centro_x_jogador = self.jogador.x_centro
        topo_jogador = self.jogador.topo_idle()

        self.barra_vida_jogador.set_position(
            centro_x_jogador - self.barra_vida_jogador.width / 2, topo_jogador - 34)

        self.barra_ap_jogador.set_position(
            centro_x_jogador - self.barra_ap_jogador.width / 2, topo_jogador - 18)

        centro_x_inimigo1 = self.inimigo1.x_centro
        topo_inimigo1 = self.inimigo1.topo_idle()
        self.barra_vida_inimigo1.set_position(
            centro_x_inimigo1 - self.barra_vida_inimigo1.width / 2, topo_inimigo1 - 24
        )

    def passarturno(self):
        if not self.inimigo1_ativo or self.gerenciador.estado != "turno_jogador":
            return

        self.gerenciador.terminar_turno_jogador()
        inimigos_agiram = bool(self.gerenciador.fila)
        self.gerenciador.turno_inimigos()

        if inimigos_agiram and self.status_jogador.is_alive():
            self._takehit_pendente = True
            self._timer_takehit = 0.25

        if inimigos_agiram and self.inimigo1_ativo:
            self.inimigo1.tocar("attack")

    def _mouse_sobre_carta(self, carta):
        mx, my = self.window.mouse.get_position()
        return (
            carta.x <= mx <= carta.x + self.largura_carta
            and carta.y <= my <= carta.y + self.altura_carta
        )

    # aplica o efeito da carta jogada: dispara a animação de ataque do
    # player quando a carta causa dano, aplica o efeito na ficha, e então
    # decide a reação do inimigo1 -- morre (se a vida zerou) ou leva um
    # Take Hit (se sobreviveu ao golpe) -- ao mesmo tempo que o player
    # ainda está no meio do próprio golpe.
    def _jogar_carta(self, carta):
        if (
            not self.inimigo1_ativo
            or self.gerenciador.estado != "turno_jogador"
        ):
            return

        resultado = self.gerenciador.jogar_carta(carta)
        if not resultado["sucesso"]:
            if resultado["motivo"] == "ap_insuficiente":
                print(f"AP insuficiente para jogar {carta.nome}!")
            return

        alvo = resultado["alvo"]

        if carta.dano > 0:
            self.jogador.tocar("attack")

        print(
            f"{carta.nome} usada -> "
            f"Jogador: HP={self.status_jogador.vida}/{self.status_jogador.vida_max} "
            f"Escudo={self.status_jogador.escudo} "
            f"AP={self.status_jogador.ap}/{self.status_jogador.ap_max} | "
            f"Goblin: HP={alvo.vida}/{alvo.vida_max}"
        )

        if carta.dano > 0:
            if not alvo.is_alive():
                self.inimigo1.tocar("death")
                self.inimigo1_ativo = False
            else:
                self.inimigo1.tocar("takehit")

    def draw(self):
        self.fundo.draw()
        dt = self.window.delta_time()

        if self._takehit_pendente:
            self._timer_takehit -= dt
            if self._timer_takehit <= 0:
                self.jogador.tocar("takehit")
                self._takehit_pendente = False

        altura_hover = 40
        velocidade_hover = 12
        for carta in self.mao:
            if (
                self.inimigo1_ativo
                and self.gerenciador.estado == "turno_jogador"
                and not self._takehit_pendente
            ):
                sobre_carta = self._mouse_sobre_carta(carta)
                alvo_y = carta.y_repouso - altura_hover if sobre_carta else carta.y_repouso
                carta.y += (alvo_y - carta.y) * min(1, velocidade_hover * dt)

                if sobre_carta and self.window.mouse.button_down(1):
                    self._jogar_carta(carta)

        mouse = self.window.mouse
        if (
            self.gerenciador.estado == "turno_jogador"
            and not self._takehit_pendente
            and mouse.is_over_object(self.botao_passar_turno)
            and mouse.button_down(mouse.LEFT)
        ):
            self.passarturno()

        self.botao_passar_turno.draw()

        self.jogador.update()
        self.jogador.draw()

        self.inimigo1.update()
        self.inimigo1.draw()

        self.barra_vida_jogador.set_value(self.status_jogador.vida)
        self.barra_ap_jogador.set_value(self.status_jogador.ap)
        self.barra_vida_jogador.draw()
        self.barra_ap_jogador.draw()

        if self.inimigo1_ativo:
            self.barra_vida_inimigo1.set_value(self.status_inimigo1.vida)
            self.barra_vida_inimigo1.draw()

        for carta in self.mao:
            carta.draw()


if __name__ == "__main__":
    janela = Window(1280, 720, "Teste de Composição")
    tela = CenaCombate(janela)

    while True:
        tela.draw()
        janela.update()