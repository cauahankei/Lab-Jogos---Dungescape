# Peças de interface do combate. Nenhuma sabe da cena: dá pra reaproveitar
# em outras telas (loja, mapa, recompensa...).
import math
import pygame
from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.uikit import ProgressBar, Button
from PPlay.tween import Tween
from utils import asset_path
import fonte_pixel


def _hud(arquivo):
    return asset_path("assets", "hud", arquivo)


def _texto_com_contorno(texto, esc=2):
    margem = 1
    largura, altura = fonte_pixel.largura(texto, esc), 5 * esc
    superficie = pygame.Surface(
        (largura + margem * 2, altura + margem * 2),
        pygame.SRCALPHA,
    )
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                fonte_pixel.desenhar(
                    superficie, margem + dx, margem + dy, texto, (0, 0, 0), esc=esc
                )
    fonte_pixel.desenhar(
        superficie, margem, margem, texto, fonte_pixel.BRANCO, esc=esc
    )
    return superficie


# Ícones dos status que aparecem embaixo da barra (o número é o valor do status).
# Status novo: põe o PNG em assets/hud e uma linha aqui.
ICONES_STATUS = {
    "forca": "status_forca.png",
    "vulneravel": "status_vulneravel.png",
    "fraqueza": "status_fraqueza.png",
    "retaliacao": "status_retaliacao.png",
}

ICONES_INTENCAO = {
    "ataque": "simbolo_ataque.png",
    "escudo": "simbolo_escudo.png",
    "debuff": "simbolo_debuff.png",
    "buff": "simbolo_buff.png",
}

# Barra de vida de qualquer combatente. Com escudo, uma faixa cinza cobre a
# barra da esquerda pra direita, proporcional à vida máxima.
class BarraVida:
    def __init__(self, combatente, largura=150, altura=14, cor=(90, 190, 90), cor_fundo=(35, 20, 20)):
        self.combatente = combatente
        self.barra = ProgressBar(largura, altura, cor_barra=cor, cor_fundo=cor_fundo)
        self.barra.valor_max = combatente.vida_max
        self.icone_escudo = GameImage(_hud("escudo_icone.png"))
        self.icones_status = {nome: GameImage(_hud(arq)) for nome, arq in ICONES_STATUS.items()}
        self._valor_vida = None
        self._texto_vida = None

    def posicionar(self, centro_x, y):
        self.barra.set_position(centro_x - self.barra.width / 2, y)

    def draw(self):
        barra, status = self.barra, self.combatente
        barra.set_value(status.vida)
        barra.draw()
        self._desenhar_escudo(barra, status)
        self._desenhar_vida(barra, status)
        self._desenhar_status(barra, status)

    def _desenhar_vida(self, barra, status):
        valor = (max(0, int(status.vida)), int(status.vida_max))
        if self._valor_vida != valor:
            self._valor_vida = valor
            self._texto_vida = _texto_com_contorno(f"{valor[0]}/{valor[1]}")

        x = barra.x + (barra.width - self._texto_vida.get_width()) / 2
        y = barra.y + (barra.height - self._texto_vida.get_height()) / 2
        Window.get_screen().blit(self._texto_vida, (round(x), round(y)))

    def _desenhar_escudo(self, barra, status):
        if status.escudo <= 0:
            return

        tela = Window.get_screen()
        largura = barra.width * min(1, status.escudo / status.vida_max)
        pygame.draw.rect(tela, (150, 160, 178), (barra.x, barra.y, largura, barra.height))
        pygame.draw.rect(tela, (205, 214, 228), (barra.x, barra.y, largura, 2))
        pygame.draw.rect(tela, (215, 222, 235), (barra.x, barra.y, barra.width, barra.height), 1)

        # escudo com o valor, do lado esquerdo da barra
        icone = self.icone_escudo
        icone.set_position(barra.x - icone.width - 4, barra.y + barra.height / 2 - icone.height / 2)
        icone.draw()
        txt = str(status.escudo)
        w = fonte_pixel.largura(txt, 2)
        fonte_pixel.desenhar(tela, int(icone.x + (icone.width - w) // 2),
                             int(icone.y + icone.height // 2 - 5), txt, (20, 22, 34), esc=2)


    # status ativos em fileira, embaixo da barra
    def _desenhar_status(self, barra, status):
        tela = Window.get_screen()
        x, y = barra.x, barra.y + barra.height + 6
        for nome, icone in self.icones_status.items():
            valor = status.status.get(nome, 0)
            if valor <= 0:
                continue
            icone.set_position(x, y)
            icone.draw()
            txt = str(valor)
            w = fonte_pixel.largura(txt, 2)
            fonte_pixel.desenhar(tela, int(x + icone.width - w - 1), int(y + icone.height - 11),
                                 txt, fonte_pixel.BRANCO, esc=2, sombra=(0, 0, 0))
            x += icone.width + 6


# Orbe de energia com "AP/AP máx" no meio, igual ao do Slay the Spire.
class OrbeEnergia:
    def __init__(self, x, y):
        self.imagem = GameImage(_hud("energia_fundo.png"))
        self.imagem.set_scale(2, 2)
        self.imagem.set_position(x, y)
        self.centro = (x + 50, y + 50)   # 50 = metade do orbe já ampliado
        self._valor = None
        self._texto = None

    # o texto só é refeito quando o valor muda
    def _montar_texto(self, txt, esc=3, pad=6):
        w, h = fonte_pixel.largura(txt, esc), 5 * esc
        texto = pygame.Surface((w + 2 * pad, h + 2 * pad), pygame.SRCALPHA)
        for dx in (-esc, 0, esc):
            for dy in (-esc, 0, esc):
                if dx or dy:
                    fonte_pixel.desenhar(texto, pad + dx, pad + dy, txt, (0, 0, 0), esc=esc)
        fonte_pixel.desenhar(texto, pad, pad, txt, fonte_pixel.BRANCO, esc=esc)
        return texto

    def draw(self, ap, ap_max):
        if self._valor != (ap, ap_max):
            self._valor = (ap, ap_max)
            self._texto = self._montar_texto(f"{ap}/{ap_max}")
        self.imagem.draw()
        cx, cy = self.centro
        Window.get_screen().blit(self._texto, (cx - self._texto.get_width() // 2,
                                               cy - self._texto.get_height() // 2))


# Ícone de pilha (compra ou descarte) com contador. Sobe um pouco no hover.
class IconePilha:
    def __init__(self, arquivo, x, y):
        self.imagem = GameImage(_hud(arquivo))
        self.x, self.y = x, y
        self.largura, self.altura = self.imagem.width, self.imagem.height
        self.imagem.set_position(x, y)

    def sobre(self):
        mx, my = Window.get_instance().mouse.get_position()
        return self.x <= mx <= self.x + self.largura and self.y <= my <= self.y + self.altura

    def draw(self, quantidade):
        self.imagem.y = self.y - (4 if self.sobre() else 0)
        self.imagem.draw()
        txt = str(quantidade)
        w = fonte_pixel.largura(txt, 2)
        fonte_pixel.desenhar(Window.get_screen(), int(self.x + 42 - w // 2),
                             int(self.imagem.y + 45), txt, fonte_pixel.BRANCO, esc=2)


# Mão de cartas em leque. Cuida do layout, do hover (a carta endireita e sobe)
# e do desenho. Quem decide o que fazer no clique é a cena.
class MaoDeCartas:
    ESCALA = 1.5
    ESPACO_EXTRA = 20
    VELOCIDADE_HOVER = 12

    # x_min e x_max: o espaço livre entre os outros itens da tela
    def __init__(self, tam_carta, x_min, x_max):
        self.janela = Window.get_instance()
        self.largura = tam_carta[0] * self.ESCALA
        self.altura = tam_carta[1] * self.ESCALA
        centro = self.janela.width / 2
        self.area = 2 * min(centro - x_min, x_max - centro)
        self._assinatura = None

    def organizar(self, cartas):
        self._assinatura = tuple(id(c) for c in cartas)
        if not cartas:
            return

        espaco = self.largura + self.ESPACO_EXTRA
        if len(cartas) > 1:
            # mão grande: as cartas se sobrepõem em vez de invadir os botões
            espaco = min(espaco, (self.area - self.largura) / (len(cartas) - 1))
        total = (len(cartas) - 1) * espaco + self.largura
        esquerda = self.janela.width / 2 - total / 2
        topo = self.janela.height - 100

        for i, carta in enumerate(cartas):
            x = esquerda + i * espaco
            angulo = ((x + self.largura / 2) - (esquerda + total / 2)) * -0.05

            theta = math.radians(abs(angulo))
            alt_rotacionada = self.largura * math.sin(theta) + self.altura * math.cos(theta)
            y = topo + (alt_rotacionada - self.altura) / 2

            carta.set_scale(self.ESCALA, self.ESCALA)
            carta.set_position(x, y)
            carta.set_rotation(angulo)
            carta.angulo_repouso = angulo
            carta.y_repouso = topo

    def _sobre(self, carta):
        mx, my = self.janela.mouse.get_position()
        return carta.x <= mx <= carta.x + self.largura and carta.y <= my <= carta.y + self.altura

    # devolve a carta sob o mouse (ou None). ativo=False desliga o hover
    def atualizar(self, cartas, ativo, dt):
        if tuple(id(c) for c in cartas) != self._assinatura:
            self.organizar(cartas)

        hover = None
        if ativo:
            hover = next((c for c in reversed(cartas) if self._sobre(c)), None)

        for carta in cartas:
            sobre = carta is hover
            carta.set_rotation(0 if sobre else carta.angulo_repouso)
            alvo_y = self.janela.height - self.altura if sobre else carta.y_repouso
            carta.y += (alvo_y - carta.y) * min(1, self.VELOCIDADE_HOVER * dt)
        return hover

    # a carta em hover é desenhada por último pra ficar por cima das outras
    def draw(self, cartas, hover=None):
        for carta in cartas:
            if carta is not hover:
                carta.draw()
        if hover in cartas:
            hover.draw()


# Tela de pilha (compra ou descarte): fundo borrado e as cartas em grade.
class VisualizadorPilha:
    COLUNAS = 6
    ESCALA = 2        # inteira pra manter o pixel art nítido
    ESPACO = 24
    TOPO = 120

    def __init__(self, tam_carta):
        self.janela = Window.get_instance()
        self.largura = tam_carta[0] * self.ESCALA
        self.altura = tam_carta[1] * self.ESCALA
        self.aberta = False
        self.scroll = 0
        self.alpha = 0

        w, h = self.janela.width, self.janela.height
        self.voltar = Button(150, 44, "Voltar", cor_base=(88, 58, 44), cor_hover=(140, 92, 60))
        self.voltar.set_position(w - 150 - 24, h - 44 - 24)

    # chama no fim do frame, com a tela já desenhada: ela vira o fundo borrado
    def abrir(self, titulo, cartas):
        tela = Window.get_screen()
        w, h = tela.get_size()
        self.fundo = tela.copy()
        pequena = pygame.transform.smoothscale(tela, (w // 6, h // 6))
        self.borrado = pygame.transform.smoothscale(pequena, (w, h))
        escuro = pygame.Surface((w, h))
        escuro.fill((8, 6, 14))
        escuro.set_alpha(150)
        self.borrado.blit(escuro, (0, 0))
        self.faixa = pygame.Surface((w, self.TOPO - 10))
        self.faixa.fill((10, 8, 16))
        self.faixa.set_alpha(235)

        self.titulo, self.cartas = titulo, list(cartas)
        self.aberta = True
        self.scroll = 0
        self.alpha = 0
        Tween.to(self, "alpha", 255, 0.2, "ease_out")

    def fechar(self):
        self.aberta = False
        self.fundo = self.borrado = self.faixa = None

    def _scroll_max(self):
        linhas = -(-len(self.cartas) // self.COLUNAS)
        return max(0, linhas * (self.altura + self.ESPACO) - self.ESPACO
                   - (self.janela.height - self.TOPO - 20))

    def loop(self):
        mouse, teclado = self.janela.mouse, self.janela.keyboard

        # roda do mouse (pygame 2) ou, se não vier, os botões 4/5; setas também
        roda = [e.y for e in self.janela.eventos if e.type == pygame.MOUSEWHEEL]
        if roda:
            self.scroll -= sum(roda) * 70
        elif mouse.button_down(4) or teclado.key_down("UP"):
            self.scroll -= 70
        elif mouse.button_down(5) or teclado.key_down("DOWN"):
            self.scroll += 70
        self.scroll = max(0, min(self.scroll, self._scroll_max()))

        self.voltar.update()
        if self.voltar.is_clicked() or teclado.key_down("ESC") or mouse.button_down(3):
            self.fechar()

    def draw(self):
        tela = Window.get_screen()
        w, h = tela.get_size()
        mx, my = self.janela.mouse.get_position()

        tela.blit(self.fundo, (0, 0))
        self.borrado.set_alpha(int(self.alpha))
        tela.blit(self.borrado, (0, 0))

        x0 = (w - (self.COLUNAS * self.largura + (self.COLUNAS - 1) * self.ESPACO)) / 2
        for i, carta in enumerate(self.cartas):
            x = x0 + (i % self.COLUNAS) * (self.largura + self.ESPACO)
            y = self.TOPO + (i // self.COLUNAS) * (self.altura + self.ESPACO) - self.scroll
            if y + self.altura < 0 or y > h:
                continue
            sobre = x <= mx <= x + self.largura and y <= my <= y + self.altura and my > self.TOPO - 10
            carta.set_scale(self.ESCALA, self.ESCALA)
            carta.set_rotation(0)
            carta.set_position(x, y - (8 if sobre else 0))
            carta.draw()

        tela.blit(self.faixa, (0, 0))
        centralizado(self.titulo.upper(), 28, 4, fonte_pixel.CREME)
        n = len(self.cartas)
        centralizado("1 CARTA" if n == 1 else f"{n} CARTAS", 78, 2, fonte_pixel.DOURADO)
        if not self.cartas:
            centralizado("NENHUMA CARTA", h // 2, 3, fonte_pixel.CREME)

        self.voltar.draw()

# Mostra o que o inimigo vai fazer no próximo turno: ícone + número
class IconeIntencao:
    def __init__(self, inimigo):
        self.inimigo = inimigo
        self.icones = {}
        for tipo, arquivo in ICONES_INTENCAO.items():
            self.icones[tipo] = GameImage(_hud(arquivo))

    # y_baixo é onde a base do ícone fica
    def draw(self, centro_x, y_baixo, alvo):
        acao = self.inimigo.proxima_acao
        icone = self.icones[acao["tipo"]]

        valor = acao["valor"]
        if acao["tipo"] == "ataque":
            valor = alvo.dano_recebido(self.inimigo.dano_causado(valor))   # inclui a Força dele e mod. por vulneravel tbm

        txt = str(valor)
        w = fonte_pixel.largura(txt, 2)
        x = centro_x - (icone.width + 4 + w) / 2
        y = y_baixo - icone.height

        icone.set_position(x, y)
        icone.draw()
        fonte_pixel.desenhar(Window.get_screen(), int(x + icone.width + 4),
                             int(y + icone.height / 2 - 5), txt,
                             fonte_pixel.BRANCO, esc=2, sombra=(0, 0, 0))


# Texto pixelado centralizado na tela (títulos, avisos...)
def centralizado(texto, y, esc, cor):
    tela = Window.get_screen()
    w = fonte_pixel.largura(texto, esc)
    fonte_pixel.desenhar(tela, (tela.get_width() - w) // 2, int(y), texto, cor, esc=esc, sombra=(0, 0, 0))


# Setinha que quica em cima do inimigo escolhido como alvo
def desenhar_seta_alvo(x, y):
    quica = math.sin(pygame.time.get_ticks() / 150) * 3
    y = y + quica
    pontos = [(x - 15, y), (x + 15, y), (x, y + 22)]
    tela = Window.get_screen()
    pygame.draw.polygon(tela, (241, 194, 126), pontos)
    pygame.draw.polygon(tela, (38, 38, 38), pontos, 2)
