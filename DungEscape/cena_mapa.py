import math
import pygame
from PPlay.scenemanager import Scene
from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.camera import Camera
from PPlay.tween import Tween
from utils import asset_path
from cartas import TAMANHO_CARTA
from hud import IconePilha, VisualizadorPilha, desenhar_seta_alvo
import fonte_pixel
import fluxo

ESPACO_X = 70            # distância entre colunas
ESPACO_Y = 104           # distância entre andares
MARGEM_TOPO = 190        # sobra em cima do boss
MARGEM_BASE = 150        # sobra embaixo do 1º andar
ALTURA_BARRA = 76        # barra de vida/andar/baralho lá em cima

NOMES = {"combate": "COMBATE", "fogueira": "FOGUEIRA", "boss": "BOSS", "evento": "EVENTO", "loja": "LOJA"}
ORDEM_LEGENDA = ("combate", "evento", "loja", "fogueira", "boss")

# cores dos fios (pontinhos entre as salas)
TINTA = (64, 40, 22)
APAGADO = (120, 92, 62)
PERCORRIDO = (150, 34, 30)
ABERTO = (236, 120, 30)


def _mapa(arquivo):
    return asset_path("assets", "mapa", arquivo)


# Fundo do mapa: o mesmo calabouço do combate, borrado e escurecido (cacheado, é só uma vez)
def fundo_borrado(escuro=120):
    w, h = Window.get_instance().width, Window.get_instance().height
    img = pygame.image.load(asset_path("assets", "Background", "background.png")).convert()
    img = pygame.transform.smoothscale(img, (w, h))
    pequena = pygame.transform.smoothscale(img, (w // 8, h // 8))
    img = pygame.transform.smoothscale(pequena, (w, h))
    sombra = pygame.Surface((w, h))
    sombra.fill((10, 6, 12))
    sombra.set_alpha(escuro)
    img.blit(sombra, (0, 0))
    return img


# Escurece as bordas da tela, igual luz de tocha: centro claro, cantos escuros
def _vinheta(w, h):
    base = pygame.Surface((32, 18), pygame.SRCALPHA)
    for y in range(18):
        for x in range(32):
            dx, dy = (x - 15.5) / 15.5, (y - 8.5) / 8.5
            d = min(1.0, math.hypot(dx, dy) / 1.1)
            base.set_at((x, y), (6, 4, 8, int(max(0, d - 0.45) / 0.55 * 150)))
    return pygame.transform.smoothscale(base, (w, h))


class _Ponto:
    # só serve de alvo pra câmera seguir (ela precisa de x, y, width e height)
    def __init__(self, x, y):
        self.x, self.y, self.width, self.height = x, y, 0, 0


class CenaMapa(Scene):
    def __init__(self, jornada):
        super().__init__()
        self.jornada = jornada
        self.mapa = jornada.mapa
        self.player = jornada.player
        largura, altura = self.janela.width, self.janela.height
        self.centro_x = largura / 2
        self.altura_mundo = MARGEM_TOPO + (self.mapa.andares - 1) * ESPACO_Y + MARGEM_BASE

        # posição de cada sala no mundo (o mapa é bem mais alto que a tela)
        self.pos = {}
        meio = (self.mapa.colunas - 1) / 2
        for no in self.mapa.todos():
            x = self.centro_x + (no.coluna - meio) * ESPACO_X + no.dx
            y = self.altura_mundo - MARGEM_BASE - no.andar * ESPACO_Y + no.dy
            self.pos[no] = (x, y)

        # A câmera do PPlay só faz a conta de rolagem e limites. Ela se registra como câmera
        # global, o que desviaria TODO desenho de GameImage (inclusive no combate), então
        # solto o registro e uso transform_y na mão.
        self.camera = Camera(largura, altura)
        Camera._instance = None
        self.camera.set_world_bounds(largura, self.altura_mundo)
        atual = self.mapa.atual
        # a sala atual fica na parte de baixo da tela, pra os próximos andares (e o boss) aparecerem
        y_alvo = (self.pos[atual][1] - 430) if atual else self.altura_mundo - MARGEM_BASE - 150
        self.alvo = _Ponto(self.centro_x, y_alvo + altura / 2)
        self.camera.y = self.camera.limite_base if atual is None else y_alvo + 260   # entra "subindo"
        self.seguindo = True
        self._arrastando = False
        self._y_mouse = 0

        # imagens
        self.fundo = fundo_borrado()
        self.vinheta = _vinheta(largura, altura)
        self.topo = GameImage(_mapa("pergaminho_topo.png"))
        self.meio = GameImage(_mapa("pergaminho_meio.png"))
        self.base = GameImage(_mapa("pergaminho_base.png"))
        self.nos = {}
        for tipo in NOMES:
            for estado in ("disponivel", "bloqueado", "visitado"):
                self.nos[(tipo, estado)] = GameImage(_mapa(f"no_{tipo}_{estado}.png"))
        self.coracao = GameImage(_mapa("coracao.png"))
        self.tipos_no_mapa = [t for t in ORDEM_LEGENDA if any(n.tipo == t for n in self.mapa.todos())]

        # barra do topo: baralho (clicável) e fundo escuro
        self.icone_baralho = IconePilha("pilha_compra.png", largura - 56 - 24, 6)
        self.visualizador = VisualizadorPilha(TAMANHO_CARTA)
        self.barra = pygame.Surface((largura, ALTURA_BARRA), pygame.SRCALPHA)
        self.barra.fill((12, 8, 14, 225))
        pygame.draw.rect(self.barra, (218, 160, 92), (0, ALTURA_BARRA - 3, largura, 3))
        self.escuro = pygame.Surface((largura, altura))
        self.escuro.fill((0, 0, 0))

        self.hover = None
        self._abrir_baralho = False
        self._saindo = None
        self.fade = 255                      # entra clareando
        Tween.to(self, "fade", 0, 0.55, "ease_out")

    # ------------------------------------------------------------ lógica
    def loop(self):
        Tween.update()
        if self.visualizador.aberta:
            self.visualizador.loop()
            return

        if self._saindo is not None:
            if self.fade >= 254:
                fluxo.entrar_na_sala(self._saindo)
            return

        self._rolar()
        if self.seguindo:
            self.camera.follow(self.alvo, 0.07)
        self.camera._aplicar_limites()

        mouse = self.mouse
        mx, my = mouse.get_position()
        self.hover = self._sala_sob_o_mouse(mx, my)
        if mouse.button_down(mouse.LEFT):
            if self.icone_baralho.sobre():
                self._abrir_baralho = True
            elif self.hover is not None:
                self._entrar(self.hover)
            else:
                self._arrastando, self._y_mouse = True, my
                self.seguindo = False
        if self._arrastando:
            if mouse.button_pressed(mouse.LEFT):
                self.camera.y -= my - self._y_mouse
                self._y_mouse = my
            else:
                self._arrastando = False

    # roda do mouse (pygame 2) ou botões 4/5, e as setas do teclado
    def _rolar(self):
        passo = 0
        roda = [e.y for e in self.janela.eventos if e.type == pygame.MOUSEWHEEL]
        if roda:
            passo = -sum(roda) * 80
        elif self.mouse.button_down(4):
            passo = -80
        elif self.mouse.button_down(5):
            passo = 80
        if self.teclado.key_down("UP"):
            passo = -80
        elif self.teclado.key_down("DOWN"):
            passo = 80
        if passo:
            self.camera.y += passo
            self.seguindo = False

    def _sala_sob_o_mouse(self, mx, my):
        if my < ALTURA_BARRA:
            return None
        for no in self.mapa.disponiveis():
            x, y = self.pos[no]
            raio = 44 if no.tipo == "boss" else 30
            if math.hypot(mx - x, my - self.camera.transform_y(y)) <= raio:
                return no
        return None

    def _entrar(self, no):
        self.mapa.visitar(no)
        self._saindo = no
        Tween.to(self, "fade", 255, 0.45, "ease_in")

    # ------------------------------------------------------------ desenho
    def draw(self):
        if self.visualizador.aberta:
            self.visualizador.draw()
            return

        tela = Window.get_screen()
        tela.blit(self.fundo, (0, 0))
        self._desenhar_pergaminho()
        self._desenhar_fios(tela)
        self._desenhar_nos(tela)
        tela.blit(self.vinheta, (0, 0))
        self._desenhar_legenda(tela)
        self._desenhar_barra(tela)
        if self.hover is not None:
            self._desenhar_dica(tela, self.hover)

        if self.fade > 0:
            self.escuro.set_alpha(int(self.fade))
            tela.blit(self.escuro, (0, 0))
        if self._abrir_baralho:
            self._abrir_baralho = False
            self.visualizador.abrir("Seu baralho", sorted(self.player.baralho.todas(), key=lambda c: c.nome))

    def _desenhar_pergaminho(self):
        cam = self.camera
        x_topo = self.centro_x - self.topo.width / 2
        x_meio = self.centro_x - self.meio.width / 2
        y = 20
        self.topo.set_position(x_topo, cam.transform_y(y))
        self.topo.draw()
        y += self.topo.height - 4
        fim = self.altura_mundo - 20 - self.base.height + 4
        while y < fim:
            if -self.meio.height < cam.transform_y(y) < self.janela.height:
                self.meio.set_position(x_meio, cam.transform_y(y))
                self.meio.draw()
            y += self.meio.height
        self.base.set_position(x_topo, cam.transform_y(fim))
        self.base.draw()

    # fios de pontinhos entre uma sala e as próximas
    def _desenhar_fios(self, tela):
        agora = pygame.time.get_ticks() / 1000
        for no in self.mapa.todos():
            x0, y0 = self.pos[no]
            y0 = self.camera.transform_y(y0)
            for prox in no.proximos:
                x1, y1 = self.pos[prox]
                y1 = self.camera.transform_y(y1)
                if max(y0, y1) < 0 or min(y0, y1) > self.janela.height:
                    continue
                if no.estado == "visitado" and prox.estado == "visitado":
                    cor, lado = PERCORRIDO, 4
                elif no.estado == "visitado" and prox.estado == "disponivel":
                    cor, lado = ABERTO, 5
                elif no.estado == "visitado":
                    cor, lado = APAGADO, 3
                elif no.estado == "disponivel":
                    cor, lado = TINTA, 4
                else:
                    cor, lado = APAGADO, 4
                dist = math.hypot(x1 - x0, y1 - y0)
                n = int(dist // 13)
                for k in range(1, n):
                    t = k / n
                    px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                    if math.hypot(px - x0, py - y0) < 30 or math.hypot(px - x1, py - y1) < (46 if prox.tipo == "boss" else 30):
                        continue
                    pulso = 1 if (cor == ABERTO and int(agora * 4 + k) % 2 == 0) else 0
                    pygame.draw.rect(tela, cor, (int(px) - lado // 2, int(py) - lado // 2, lado + pulso, lado + pulso))

    def _desenhar_nos(self, tela):
        agora = pygame.time.get_ticks() / 1000
        for no in self.mapa.todos():
            x, y = self.pos[no]
            y = self.camera.transform_y(y)
            if y < -60 or y > self.janela.height + 60:
                continue
            img = self.nos[(no.tipo, no.estado)]
            img.set_position(x - img.width / 2, y - img.height / 2)
            img.draw()
            if no.estado == "disponivel":
                base = 46 if no.tipo == "boss" else 31
                raio = base + (5 if no is self.hover else 0) + 2 * math.sin(agora * 5)
                cor = (255, 236, 170) if no is self.hover else (255, 200, 110)
                pygame.draw.circle(tela, cor, (int(x), int(y)), int(raio), 3 if no is self.hover else 2)
            if no is self.mapa.atual:
                desenhar_seta_alvo(x, y - (66 if no.tipo == "boss" else 54))

    def _desenhar_dica(self, tela, no):
        x, y = self.pos[no]
        y = self.camera.transform_y(y)
        texto = NOMES[no.tipo]
        if no.dificuldade:
            texto += "  " + {"facil": "FÁCIL", "medio": "MÉDIO", "dificil": "DIFÍCIL"}[no.dificuldade]
        w = fonte_pixel.largura(texto, 2)
        caixa = (int(x + 38), int(y - 14), w + 16, 28)
        pygame.draw.rect(tela, (14, 10, 16), caixa)
        pygame.draw.rect(tela, (218, 160, 92), caixa, 2)
        fonte_pixel.desenhar(tela, caixa[0] + 8, caixa[1] + 9, texto, fonte_pixel.CREME, esc=2)

    def _desenhar_legenda(self, tela):
        x0, y0, largura = 56, 130, 220
        altura = 56 + len(self.tipos_no_mapa) * 58
        caixa = pygame.Surface((largura, altura), pygame.SRCALPHA)
        caixa.fill((12, 8, 14, 215))
        tela.blit(caixa, (x0, y0))
        pygame.draw.rect(tela, (218, 160, 92), (x0, y0, largura, altura), 2)
        fonte_pixel.desenhar(tela, x0 + 16, y0 + 16, "LEGENDA", fonte_pixel.DOURADO, esc=2)
        for i, tipo in enumerate(self.tipos_no_mapa):
            icone = self.nos[(tipo, "disponivel")]
            escala = 0.6 if tipo == "boss" else 1.0
            iy = y0 + 56 + i * 58
            if tipo == "boss":
                icone.set_scale(0.6, 0.6)
            icone.set_position(x0 + 14, iy)
            icone.draw()
            if tipo == "boss":
                icone.set_scale(1, 1)
            fonte_pixel.desenhar(tela, x0 + 74, iy + 16, NOMES[tipo], fonte_pixel.CREME, esc=2)

    def _desenhar_barra(self, tela):
        tela.blit(self.barra, (0, 0))
        self.coracao.set_position(24, 24)
        self.coracao.draw()
        fonte_pixel.desenhar(tela, 66, 26, f"{self.player.vida}/{self.player.vida_max}", fonte_pixel.BRANCO,
                             esc=3, sombra=(0, 0, 0))
        atual = self.mapa.atual
        texto = "ESCOLHA ONDE COMEÇAR" if atual is None else f"ANDAR {atual.andar + 1} DE {self.mapa.andares}"
        w = fonte_pixel.largura(texto, 3)
        fonte_pixel.desenhar(tela, int((self.janela.width - w) / 2), 26, texto, fonte_pixel.DOURADO, esc=3,
                             sombra=(0, 0, 0))
        self.icone_baralho.draw(len(self.player.baralho.todas()))
