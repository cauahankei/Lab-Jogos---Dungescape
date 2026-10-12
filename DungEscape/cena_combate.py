#utilidade
import math
import pygame
from utils import asset_path
#pplay
from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.uikit import ProgressBar, Button
from PPlay.tween import Tween
#autoral
import fonte_pixel
from cartas import Baralho, criar_ataque, criar_defesa
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
        deck = [criar_ataque() for _ in range(5)] + [criar_defesa() for _ in range(4)]
        self.status_jogador = Player(baralho=Baralho(deck))
        self.status_inimigo1 = Inimigo1()
        self.gerenciador = GerenciadorCombate(
            self.status_jogador, [self.status_inimigo1]
        )


        self.jogador = AtorAnimado("player", self.window.largura * 0.2, self.chao_y)
        self.inimigo1 = AtorAnimado("goblin", self.window.largura * 0.8, self.chao_y, virado_para_esquerda=True)


        self.inimigo1_ativo = True
        self._takehit_pendente = False
        self._timer_takehit = 0.0

        # pilhas: aberta = None/"compra"/"descarte"; pedida = clique que abre no fim do frame
        self.pilha_aberta = None
        self._pilha_pedida = None
        self.pilha_scroll = 0
        self.pilha_alpha = 0

        # --- Barras de vida/energia (PPlay.uikit.ProgressBar) ---
        self.barra_vida_jogador = ProgressBar(150, 14, cor_barra=(90, 190, 90), cor_fundo=(35, 20, 20))
        self.barra_vida_jogador.valor_max = self.status_jogador.vida_max

        self.barra_vida_inimigo1 = ProgressBar(120, 12, cor_barra=(190, 60, 60), cor_fundo=(30, 15, 15))
        self.barra_vida_inimigo1.valor_max = self.status_inimigo1.vida_max

        self._posicionar_barras()

        # passar_turno
        self.botao_passar_turno = GameImage(asset_path("assets","hud","botao_passar_turno_new.png"))
        margem = 24
        self.pilha_compra = GameImage(asset_path("assets", "hud", "pilha_compra.png"))
        self.pilha_descarte = GameImage(asset_path("assets", "hud", "pilha_descarte.png"))
        self.y_pilhas = self.window.height - self.pilha_compra.height - margem
        self.pilha_compra.set_position(margem, self.y_pilhas)
        self.pilha_descarte.set_position(self.window.width - self.pilha_descarte.width - margem, self.y_pilhas)

        self.orbe = GameImage(asset_path("assets", "hud", "energia_fundo.png"))
        self.orbe.set_scale(2, 2)
        self.orbe.set_position(14, self.y_pilhas - 100 - 6)
        self._ap_desenhado = None
        self._texto_orbe = None
        self.icone_escudo = GameImage(asset_path("assets", "hud", "escudo_icone.png"))

        self.botao_passar_turno.set_position(
            self.pilha_descarte.x - self.botao_passar_turno.width - 16,
            self.window.height - self.botao_passar_turno.height - margem)

        # grade da tela de pilha (cartas em escala 2 pra manter o pixel art nitido)
        self.GRID_COLS = 6
        self.GRID_ESCALA = 2
        self.GRID_GAP = 24
        self.GRID_TOPO = 120
        self.btn_voltar = Button(150, 44, "Voltar", cor_base=(88, 58, 44), cor_hover=(140, 92, 60))
        self.btn_voltar.set_position(self.window.width - 150 - margem, self.window.height - 44 - margem)


        # --- Visual Mão de cartas ---
        self.ESCALA_CARTA = 1.5
        self.ESPACAMENTO_EXTRA = 20
        self.largura_carta = deck[0].width * self.ESCALA_CARTA
        centro = self.window.largura / 2
        x_min = self.pilha_compra.x + self.pilha_compra.width + 16
        x_max = self.botao_passar_turno.x - 16
        self.area_mao = 2 * min(centro - x_min, x_max - centro)
        self.altura_carta = deck[0].height * self.ESCALA_CARTA
        self._assinatura_mao = None
        self._organizar_mao()

    # posiciona a mao em leque. roda sozinha sempre que a mao muda (ver draw)
    def _organizar_mao(self):
        mao = self.status_jogador.baralho.mao
        self._assinatura_mao = tuple(id(c) for c in mao)
        if not mao:
            return

        espacamento = self.largura_carta + self.ESPACAMENTO_EXTRA
        if len(mao) > 1:
            # mao grande: as cartas se sobrepoem em vez de invadir os botoes
            espacamento = min(espacamento, (self.area_mao - self.largura_carta) / (len(mao) - 1))
        largura_total_mao = (len(mao) - 1) * espacamento + self.largura_carta
        margem_esquerda = self.window.largura / 2 - largura_total_mao / 2
        topo_mao = self.window.altura - 100

        for i, carta in enumerate(mao):
            x = margem_esquerda + i * espacamento
            angulo = ((x + self.largura_carta / 2) - (margem_esquerda + largura_total_mao / 2)) * -0.05

            theta = math.radians(abs(angulo))
            altura_rotacionada = (self.largura_carta * math.sin(theta) + self.altura_carta * math.cos(theta))
            y = topo_mao + (altura_rotacionada - self.altura_carta) / 2

            carta.set_scale(self.ESCALA_CARTA, self.ESCALA_CARTA)
            carta.set_position(x, y)
            carta.set_rotation(angulo)
            carta.angulo_repouso = angulo
            carta.y_repouso = topo_mao

    # Posição das barras é FIXA (baseada no Idle de cada um) -- não usa a
    # altura da animação atual, senão elas ficariam pulando de lugar toda
    # vez que o player ataca ou o inimigo1 reage/morre.
    def _posicionar_barras(self):
        centro_x_jogador = self.jogador.x_centro
        topo_jogador = self.jogador.topo_idle()

        self.barra_vida_jogador.set_position(
            centro_x_jogador - self.barra_vida_jogador.width / 2, topo_jogador - 24)

        centro_x_inimigo1 = self.inimigo1.x_centro
        topo_inimigo1 = self.inimigo1.topo_idle()
        self.barra_vida_inimigo1.set_position(
            centro_x_inimigo1 - self.barra_vida_inimigo1.width / 2, topo_inimigo1 - 24
        )

    # barra de vida normal + escudo por cima: a parte cinza cobre a barra da esquerda
    # pra direita, proporcional a vida maxima (escudo >= vida max = barra toda cinza)
    # PENSANDO EM MUDAR PRA FICAR IGUAL SLAY THE SPIRE ( barra fica cinza toda )
    def _desenhar_barra_vida(self, barra, status):
        barra.set_value(status.vida)
        barra.draw()
        if status.escudo <= 0:
            return

        tela = self.window.screen
        largura = barra.width * min(1, status.escudo / status.vida_max)
        pygame.draw.rect(tela, (150, 160, 178), (barra.x, barra.y, largura, barra.height))
        pygame.draw.rect(tela, (205, 214, 228), (barra.x, barra.y, largura, 2))
        pygame.draw.rect(tela, (215, 222, 235), (barra.x, barra.y, barra.width, barra.height), 1)

        # escudo com o valor, no canto esquerdo da barra
        icone = self.icone_escudo
        icone.set_position(barra.x - icone.width - 4, barra.y + barra.height / 2 - icone.height / 2)
        icone.draw()
        txt = str(status.escudo)
        w = fonte_pixel.largura(txt, 2)
        fonte_pixel.desenhar(tela, int(icone.x + (icone.width - w) // 2), int(icone.y + icone.height // 2 - 5),
                             txt, (20, 22, 34), esc=2)

    # orbe de energia com "AP/AP max" no meio. o texto so e remontado quando muda
    def _desenhar_orbe(self):
        ap, ap_max = self.status_jogador.ap, self.status_jogador.ap_max
        if self._ap_desenhado != (ap, ap_max):
            self._ap_desenhado = (ap, ap_max)
            txt, esc, pad = f"{ap}/{ap_max}", 3, 6
            w, h = fonte_pixel.largura(txt, esc), 5 * esc
            self._texto_orbe = pygame.Surface((w + 2 * pad, h + 2 * pad), pygame.SRCALPHA)
            for dx in (-esc, 0, esc):
                for dy in (-esc, 0, esc):
                    if dx or dy:
                        fonte_pixel.desenhar(self._texto_orbe, pad + dx, pad + dy, txt, (0, 0, 0), esc=esc)
            fonte_pixel.desenhar(self._texto_orbe, pad, pad, txt, fonte_pixel.BRANCO, esc=esc)

        self.orbe.draw()
        cx, cy = self.orbe.x + 50, self.orbe.y + 50
        self.window.screen.blit(self._texto_orbe, (cx - self._texto_orbe.get_width() // 2,
                                                   cy - self._texto_orbe.get_height() // 2))

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

    def _sobre_pilha(self, icone):
        mx, my = self.window.mouse.get_position()
        return (icone.x <= mx <= icone.x + icone.width
                and self.y_pilhas <= my <= self.y_pilhas + icone.height)

    # icone da pilha com o contador no selo; sobe um pouquinho no hover
    def _desenhar_pilha(self, icone, quantidade):
        icone.y = self.y_pilhas - (4 if self._sobre_pilha(icone) else 0)
        icone.draw()
        texto = str(quantidade)
        w = fonte_pixel.largura(texto, 2)
        fonte_pixel.desenhar(self.window.screen, icone.x + 42 - w // 2, icone.y + 45,
                             texto, fonte_pixel.BRANCO, esc=2)

    # tira um "print" da tela ja desenhada e borra pra servir de fundo
    def _abrir_pilha(self, nome):
        tela = self.window.screen
        w, h = tela.get_size()
        self.pilha_fundo = tela.copy()
        borrada = pygame.transform.smoothscale(tela, (w // 6, h // 6))
        self.pilha_borrada = pygame.transform.smoothscale(borrada, (w, h))
        escuro = pygame.Surface((w, h))
        escuro.fill((8, 6, 14))
        escuro.set_alpha(150)
        self.pilha_borrada.blit(escuro, (0, 0))
        self.pilha_faixa = pygame.Surface((w, self.GRID_TOPO - 10))
        self.pilha_faixa.fill((10, 8, 16))
        self.pilha_faixa.set_alpha(235)

        self.pilha_aberta = nome
        self.pilha_scroll = 0
        self.pilha_alpha = 0
        Tween.to(self, "pilha_alpha", 255, 0.2, "ease_out")

    def _fechar_pilha(self):
        self.pilha_aberta = None
        self.pilha_fundo = self.pilha_borrada = self.pilha_faixa = None

    def _draw_pilha(self):
        tela = self.window.screen
        mouse = self.window.mouse
        teclado = self.window.keyboard
        w, h = tela.get_size()
        baralho = self.status_jogador.baralho

        if self.pilha_aberta == "descarte":
            cartas, titulo = baralho.descarte, "PILHA DE DESCARTE"
        else:
            # ordenada por nome pra nao entregar a ordem real de compra
            cartas, titulo = sorted(baralho.compra, key=lambda c: c.nome), "PILHA DE COMPRA"

        tela.blit(self.pilha_fundo, (0, 0))
        self.pilha_borrada.set_alpha(int(self.pilha_alpha))
        tela.blit(self.pilha_borrada, (0, 0))

        esc, cols, gap, topo = self.GRID_ESCALA, self.GRID_COLS, self.GRID_GAP, self.GRID_TOPO
        cw = self.largura_carta / self.ESCALA_CARTA * esc
        ch = self.altura_carta / self.ESCALA_CARTA * esc

        linhas = -(-len(cartas) // cols)
        max_scroll = max(0, linhas * (ch + gap) - gap - (h - topo - 20))
        if mouse.button_down(4) or teclado.key_down("UP"):
            self.pilha_scroll -= 70
        if mouse.button_down(5) or teclado.key_down("DOWN"):
            self.pilha_scroll += 70
        self.pilha_scroll = max(0, min(self.pilha_scroll, max_scroll))

        mx, my = mouse.get_position()
        x0 = (w - (cols * cw + (cols - 1) * gap)) / 2
        for i, carta in enumerate(cartas):
            x = x0 + (i % cols) * (cw + gap)
            y = topo + (i // cols) * (ch + gap) - self.pilha_scroll
            if y + ch < 0 or y > h:
                continue
            sobre = x <= mx <= x + cw and y <= my <= y + ch and my > topo - 10
            carta.set_scale(esc, esc)
            carta.set_rotation(0)
            carta.set_position(x, y - (8 if sobre else 0))
            carta.draw()

        tela.blit(self.pilha_faixa, (0, 0))
        tw = fonte_pixel.largura(titulo, 4)
        fonte_pixel.desenhar(tela, (w - tw) // 2, 28, titulo, fonte_pixel.CREME, esc=4, sombra=(0, 0, 0))
        info = f"{len(cartas)} CARTAS" if len(cartas) != 1 else "1 CARTA"
        iw = fonte_pixel.largura(info, 2)
        fonte_pixel.desenhar(tela, (w - iw) // 2, 78, info, fonte_pixel.DOURADO, esc=2)

        if not cartas:
            vazio = "NENHUMA CARTA"
            vw = fonte_pixel.largura(vazio, 3)
            fonte_pixel.desenhar(tela, (w - vw) // 2, h // 2, vazio, fonte_pixel.CREME, esc=3, sombra=(0, 0, 0))

        self.btn_voltar.update()
        self.btn_voltar.draw()
        if self.btn_voltar.is_clicked() or teclado.key_down("ESC") or mouse.button_down(3):
            self._fechar_pilha()

    def draw(self):
        Tween.update()
        if self.pilha_aberta:
            self._draw_pilha()
            return

        self.fundo.draw()
        dt = self.window.delta_time()
        mouse = self.window.mouse
        baralho = self.status_jogador.baralho

        if self._takehit_pendente:
            self._timer_takehit -= dt
            if self._timer_takehit <= 0:
                self.jogador.tocar("takehit")
                self._takehit_pendente = False

        if tuple(id(c) for c in baralho.mao) != self._assinatura_mao:
            self._organizar_mao()

        if mouse.button_down(mouse.LEFT):
            if self._sobre_pilha(self.pilha_descarte):
                self._pilha_pedida = "descarte"
            elif self._sobre_pilha(self.pilha_compra):
                self._pilha_pedida = "compra"

        pode_agir = (
            self.inimigo1_ativo
            and self.gerenciador.estado == "turno_jogador"
            and not self._takehit_pendente
        )

        velocidade_hover = 12
        hover = None
        if pode_agir:
            hover = next((c for c in reversed(baralho.mao) if self._mouse_sobre_carta(c)), None)
        for carta in list(baralho.mao):
            sobre = carta is hover
            # no hover a carta endireita e sobe ate aparecer inteira
            carta.set_rotation(0 if sobre else carta.angulo_repouso)
            alvo_y = self.window.altura - self.altura_carta if sobre else carta.y_repouso
            carta.y += (alvo_y - carta.y) * min(1, velocidade_hover * dt)

            if sobre and not self._pilha_pedida and mouse.button_down(1):
                self._jogar_carta(carta)
                break

        if (
            self.gerenciador.estado == "turno_jogador"
            and not self._takehit_pendente
            and not self._pilha_pedida
            and mouse.is_over_object(self.botao_passar_turno)
            and mouse.button_down(mouse.LEFT)
        ):
            self.passarturno()

        self.botao_passar_turno.draw()
        self._desenhar_pilha(self.pilha_compra, len(baralho.compra))
        self._desenhar_pilha(self.pilha_descarte, len(baralho.descarte))

        self.jogador.update()
        self.jogador.draw()

        self.inimigo1.update()
        self.inimigo1.draw()

        self._desenhar_barra_vida(self.barra_vida_jogador, self.status_jogador)
        self._desenhar_orbe()

        if self.inimigo1_ativo:
            self._desenhar_barra_vida(self.barra_vida_inimigo1, self.status_inimigo1)

        for carta in baralho.mao:
            if carta is not hover:
                carta.draw()
        if hover in baralho.mao:
            hover.draw()

        # abre por ultimo pra o print da tela ja pegar o frame completo
        if self._pilha_pedida:
            self._abrir_pilha(self._pilha_pedida)
            self._pilha_pedida = None


if __name__ == "__main__":
    janela = Window(1280, 720, "Teste de Composição")
    tela = CenaCombate(janela)

    while True:
        tela.draw()
        janela.update()