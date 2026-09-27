# biblioteca q não sei mto bem como funciona, mas resolve 
# os problemas de achar as imagens
import math
from pathlib import Path

from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.animation import Animation
from PPlay.uikit import ProgressBar

from cartas import criar_corte_basico, criar_escudo
from combatente import Player, Goblin
from animacao_direcional import AnimacaoDirecional


BASE_DIR = Path(__file__).resolve().parent
def asset_path(*parts):
    return str(BASE_DIR.joinpath(*parts))

# quanto a carta sobe (em pixels) e quao rapido ela sobe/desce quando o
# mouse passa por cima - estilo Slay the Spire
ALTURA_HOVER = 40
VELOCIDADE_HOVER = 12

ESCALA_JOGADOR = 6.0
ESCALA_INIMIGO = 6.0

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

        # Visual Jogador: Idle (padrão) + Ataque (Corte Básico)
        # O player fica do lado ESQUERDO da arena e olha pra DIREITA (pro
        # inimigo) é a direção padrão do spritesheet, então nenhum dos
        # dois precisa ser espelhado.
        self.jogador_idle = Animation(asset_path("assets", "Player", "Idle.png"), 8)
        self.jogador_idle.set_total_duration(600)
        self.jogador_idle.set_scale(ESCALA_JOGADOR, ESCALA_JOGADOR)

        self.jogador_attack = Animation(asset_path("assets", "Player", "Attack1.png"), 4, loop=False)
        self.jogador_attack.set_total_duration(400)
        self.jogador_attack.set_scale(ESCALA_JOGADOR, ESCALA_JOGADOR)
        self.jogador_attack.rodando = False  # só liga quando o Corte Básico for jogado

        self.estado_jogador = "idle"  # idle | atacando
        self._posicionar_jogador()

        # --- Visual Inimigo: Idle + Take Hit (reação) + Morte
        # O Goblin fica do lado DIREITO da arena e precisa olhar pra
        # ESQUERDA (pro jogador) -- o spritesheet dele também vem virado
        # pra direita por padrão, então as TRÊS animações do Goblin usam
        # AnimacaoDirecional com virado_para_esquerda=True. As três
        # precisam ser espelhadas juntas: se só a morte fosse espelhada,
        # ele ficaria olhando pra um lado no Idle e pro outro ao morrer.
        self.goblin_idle = AnimacaoDirecional(
            asset_path("assets", "Goblin", "Idle.png"), 4, virado_para_esquerda=False
        )
        self.goblin_idle.set_total_duration(600)
        self.goblin_idle.set_scale(ESCALA_INIMIGO, ESCALA_INIMIGO)

        self.goblin_takehit = AnimacaoDirecional(
            asset_path("assets", "Goblin", "TakeHit.png"), 4, loop=False, virado_para_esquerda=True
        )
        self.goblin_takehit.set_total_duration(300)
        self.goblin_takehit.set_scale(ESCALA_INIMIGO, ESCALA_INIMIGO)
        self.goblin_takehit.rodando = False

        self.goblin_death = AnimacaoDirecional(
            asset_path("assets", "Goblin", "Death.png"), 4, loop=False, virado_para_esquerda=True
        )
        self.goblin_death.set_total_duration(600)
        self.goblin_death.set_scale(ESCALA_INIMIGO, ESCALA_INIMIGO)
        self.goblin_death.rodando = False

        self.estado_goblin = "idle"  # idle | recebendo_dano | morrendo | morto (removido da cena)
        # trava usada pelas cartas: assim que a morte começa, o combate
        # acabou e nenhuma carta pode mais ser jogada (nem a de escudo)
        self.goblin_ativo = True
        self._posicionar_goblin()

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

    # -- Posicionamento (ancorado no chão) -----------------------------------
    def _posicionar_jogador(self):
        anim = self.jogador_attack if self.estado_jogador == "atacando" else self.jogador_idle
        largura_final = anim.width * ESCALA_JOGADOR
        altura_final = anim.height * ESCALA_JOGADOR
        x = self.window.largura * 0.2 - largura_final / 2
        y = self.chao_y - altura_final
        anim.set_position(x, y)

    def _posicionar_goblin(self):
        if self.estado_goblin == "morrendo":
            anim = self.goblin_death
        elif self.estado_goblin == "recebendo_dano":
            anim = self.goblin_takehit
        else:
            anim = self.goblin_idle
        largura_final = anim.width * ESCALA_INIMIGO
        altura_final = anim.height * ESCALA_INIMIGO
        x = self.window.largura * 0.8 - largura_final / 2
        y = self.chao_y - altura_final
        anim.set_position(x, y)

    # Posição das barras é FIXA (baseada no Idle de cada um) -- não usa a
    # altura da animação atual, senão elas ficariam pulando de lugar toda
    # vez que o player ataca ou o goblin reage/morre.
    def _posicionar_barras(self):
        centro_x_jogador = self.window.largura * 0.2
        topo_jogador = self.chao_y - self.jogador_idle.height * ESCALA_JOGADOR
        self.barra_vida_jogador.set_position(
            centro_x_jogador - self.barra_vida_jogador.width / 2, topo_jogador - 34
        )
        self.barra_ap_jogador.set_position(
            centro_x_jogador - self.barra_ap_jogador.width / 2, topo_jogador - 18
        )

        centro_x_goblin = self.window.largura * 0.8
        topo_goblin = self.chao_y - self.goblin_idle.height * ESCALA_INIMIGO
        self.barra_vida_goblin.set_position(
            centro_x_goblin - self.barra_vida_goblin.width / 2, topo_goblin - 24
        )

    # -- Gatilhos de animação -------------------------------------------------
    def _iniciar_ataque_jogador(self):
        self.jogador_attack.set_curr_frame(0)
        self.jogador_attack.rodando = True
        self.estado_jogador = "atacando"
        self._posicionar_jogador()

    def _iniciar_takehit_goblin(self):
        self.goblin_takehit.set_curr_frame(0)
        self.goblin_takehit.rodando = True
        self.estado_goblin = "recebendo_dano"
        self._posicionar_goblin()

    def _iniciar_morte_goblin(self):
        self.goblin_death.set_curr_frame(0)
        self.goblin_death.rodando = True
        self.estado_goblin = "morrendo"
        self._posicionar_goblin()
        # trava as cartas JÁ no momento da morte (não só depois da animação
        # acabar) -- evita qualquer chance de jogar outra carta contra um
        # inimigo que já está caindo
        self.goblin_ativo = False

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
            self._iniciar_ataque_jogador()

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
                self._iniciar_morte_goblin()
            else:
                self._iniciar_takehit_goblin()

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

        # --- Jogador: Idle ou Ataque ---
        if self.estado_jogador == "atacando":
            self.jogador_attack.update()
            self.jogador_attack.draw()
            if not self.jogador_attack.rodando:
                self.estado_jogador = "idle"
                self._posicionar_jogador()
        else:
            self.jogador_idle.update()
            self.jogador_idle.draw()

        # --- Goblin: Idle, Take Hit, Morrendo, ou Morto (removido) ---
        if self.estado_goblin == "idle":
            self.goblin_idle.update()
            self.goblin_idle.draw()
        elif self.estado_goblin == "recebendo_dano":
            self.goblin_takehit.update()
            self.goblin_takehit.draw()
            if not self.goblin_takehit.rodando:
                self.estado_goblin = "idle"
                self._posicionar_goblin()
        elif self.estado_goblin == "morrendo":
            self.goblin_death.update()
            self.goblin_death.draw()
            if not self.goblin_death.rodando:
                self.estado_goblin = "morto"
        # "morto": não desenha mais nada -- o goblin foi removido da cena

        # --- Barras de vida/energia ---
        self.barra_vida_jogador.set_value(self.status_jogador.vida)
        self.barra_ap_jogador.set_value(self.status_jogador.ap)
        self.barra_vida_jogador.draw()
        self.barra_ap_jogador.draw()

        if self.estado_goblin != "morto":
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
