import pygame
from PPlay.scenemanager import Scene
from PPlay.gameimage import GameImage
from PPlay.timer import Timer
from PPlay.tween import Tween
from utils import asset_path
from cartas import Baralho, deck_inicial, TAMANHO_CARTA
from combatente import Player, criar_inimigo
from gerenciador_combate import GerenciadorCombate
from ator import AtorAnimado
from hud import (BarraVida, OrbeEnergia, IconePilha, MaoDeCartas,
                 VisualizadorPilha, centralizado, desenhar_seta_alvo, IconeIntencao)
import fonte_pixel

MARGEM = 24


# Junta num lugar só tudo que um inimigo precisa na tela: ficha de combate,
# animação e barra de vida.
class InimigoEmCena:
    def __init__(self, status, centro_x, chao_y):
        self.status = status
        self.ator = AtorAnimado(status.ator_id, centro_x, chao_y, virado_para_esquerda=True)
        self.barra = BarraVida(status, 120, 12, cor=(190, 60, 60), cor_fundo=(30, 15, 15))
        # a barra fica fixa (baseada no idle), senão ela pularia a cada animação
        self.barra.posicionar(centro_x, self.ator.topo_idle() - 24)
        self.intencao = IconeIntencao(status)

    def contem(self, x, y):
        ax, ay, aw, ah = self.ator.area_idle()
        return ax <= x <= ax + aw and ay <= y <= ay + ah


# Uma luta: o jogador contra uma lista de inimigos (ids do catálogo em combatente.py).
# Passa o player de fora se quiser levar vida e baralho de uma luta pra outra.
class CenaCombate(Scene):
    def __init__(self, inimigos=("goblin",), player=None):
        super().__init__()
        if not inimigos:
            raise ValueError("a luta precisa de pelo menos 1 inimigo")
        largura, altura = self.janela.width, self.janela.height
        self.chao_y = altura * 0.85
        self.fundo = GameImage(asset_path("assets", "Background", "background.png"))

        # --- lógica ---
        self.player = player or Player(baralho=Baralho(deck_inicial()))
        status = [criar_inimigo(i) for i in inimigos]
        self.gerenciador = GerenciadorCombate(self.player, status)

        # --- personagens ---
        self.ator_player = AtorAnimado("player", largura * 0.2, self.chao_y)
        self.barra_player = BarraVida(self.player)
        self.barra_player.posicionar(self.ator_player.x_centro, self.ator_player.topo_idle() - 24)

        self.inimigos = [InimigoEmCena(s, x, self.chao_y)
                         for s, x in zip(status, self._posicoes_inimigos(len(status)))]
        self.alvo = self.inimigos[0] if self.inimigos else None

        # --- interface ---
        self.botao_passar_turno = GameImage(asset_path("assets", "hud", "botao_passar_turno_new.png"))
        y_pilhas = altura - 64 - MARGEM
        self.pilha_compra = IconePilha("pilha_compra.png", MARGEM, y_pilhas)
        self.pilha_descarte = IconePilha("pilha_descarte.png", largura - 56 - MARGEM, y_pilhas)
        self.botao_passar_turno.set_position(self.pilha_descarte.x - self.botao_passar_turno.width - 16,
                                             altura - self.botao_passar_turno.height - MARGEM)
        self.orbe = OrbeEnergia(MARGEM + 70, y_pilhas-15)

        self.mao = MaoDeCartas(TAMANHO_CARTA,
                               self.pilha_compra.x + self.pilha_compra.largura + 16,
                               self.botao_passar_turno.x - 16)
        self.visualizador = VisualizadorPilha(TAMANHO_CARTA)

        self._hover = None
        self._pilha_pedida = None
        self._aguardando_reacao = False   # espera o player apanhar antes de liberar o input
        self.mao.organizar(self.player.baralho.mao)



    # até 3 inimigos, o último sempre no mesmo canto da tela
    def _posicoes_inimigos(self, n):
        ultimo = self.janela.width * 0.8
        return [ultimo - (n - 1 - i) * 210 for i in range(n)]

    def _pode_agir(self):
        return (self.gerenciador.estado == "turno_jogador" and not self._aguardando_reacao
                and self.gerenciador.resultado() is None)

    # ------------------------------------------------------------ lógica
    def loop(self):
        Tween.update()
        if self.visualizador.aberta:
            self.visualizador.loop()
            return

        Timer.update()
        self._garantir_alvo()
        self._hover = self.mao.atualizar(self.player.baralho.mao, self._pode_agir(),
                                         self.janela.delta_time())
        self._cliques()

        self.ator_player.update()

        if not self.player.is_alive():
            if not self._aguardando_reacao and not self.ator_player.em_acao():
                if self.ator_player.estado != "death":
                    self.ator_player.tocar("death")

        for inimigo in self.inimigos:
            inimigo.ator.update()
            if not inimigo.status.is_alive() and not inimigo.ator.em_acao():
                if inimigo.ator.estado != "death":
                    inimigo.ator.tocar("death")

        if self.gerenciador.estado == "turno_inimigos" and self._todos_livres():
            evento = self.gerenciador.proxima_acao_inimiga()
            if evento is not None:
                self._animar_acao(evento)
    def _cliques(self):
        mouse = self.mouse
        if not mouse.button_down(mouse.LEFT):
            return

        if self.pilha_descarte.sobre():
            self._pilha_pedida = "descarte"
        elif self.pilha_compra.sobre():
            self._pilha_pedida = "compra"
        elif not self._pode_agir():
            return
        elif self._hover:
            self._jogar_carta(self._hover)
        elif mouse.is_over_object(self.botao_passar_turno):
            self.gerenciador.terminar_turno_jogador()
        else:
            self._escolher_alvo_com_clique()

    # se o alvo morreu, passa pro primeiro que ainda tá vivo
    def _garantir_alvo(self):
        if self.alvo is None or self.alvo.status.is_alive():
            return
        vivo = next((i for i in self.inimigos if i.status.is_alive()), None)
        self.alvo = vivo or self.alvo

    def _escolher_alvo_com_clique(self):
        mx, my = self.mouse.get_position()
        sob_o_mouse = [i for i in self.inimigos if i.status.is_alive() and i.contem(mx, my)]
        if sob_o_mouse:
            # as áreas se sobrepõem, então vale o mais perto do clique
            self.alvo = min(sob_o_mouse, key=lambda i: abs(mx - i.ator.x_centro))

    def _jogar_carta(self, carta):
        resultado = self.gerenciador.jogar_carta(carta, self.alvo.status)
        if not resultado["sucesso"]:
            if resultado["motivo"] == "ap_insuficiente":
                print(f"AP insuficiente para jogar {carta.nome}!")
            return

        self.mao.organizar(self.player.baralho.mao)
        alvo = self.alvo
        if carta.dano > 0:
            self.ator_player.tocar("attack")
            self._reagir(alvo)
            if carta.base.get("vezes", 1) > 1:
                Timer.after(0.3, self._segundo_golpe, alvo)
        self._garantir_alvo()

        print(f"{carta.nome} -> {alvo.status.nome}: {alvo.status.vida}/{alvo.status.vida_max} | "
              f"AP {self.player.ap}/{self.player.ap_max} | escudo {self.player.escudo}")

    # o alvo morre (se a vida zerou) ou apanha
    def _reagir(self, inimigo):
        inimigo.ator.tocar("takehit" if inimigo.status.is_alive() else "death")

    def _segundo_golpe(self, inimigo):
        if inimigo.status.is_alive():
            inimigo.ator.tocar("takehit")

    def _player_apanha(self):
        self.ator_player.tocar("takehit")
        self._aguardando_reacao = False

        #verifica se todos estão "idle" ou se alguem tá agindo
    def _todos_livres(self):
        if self._aguardando_reacao:
            return False
        if self.ator_player.em_acao():
            return False
        for inimigo in self.inimigos:
            if inimigo.ator.em_acao():
                return False
        return True

    def _animar_acao(self, evento):
        if evento["acao"]["tipo"] != "ataque":
            return          # escudo: nada toca, o goblin continua no idle

        for inimigo in self.inimigos:
            if inimigo.status is evento["inimigo"]:
                inimigo.ator.tocar("attack")
        self._aguardando_reacao = True
        Timer.after(0.25, self._player_apanha)
    # ------------------------------------------------------------ desenho
    def draw(self):
        if self.visualizador.aberta:
            self.visualizador.draw()
            return

        baralho = self.player.baralho
        self.fundo.draw()

        self.botao_passar_turno.draw()
        self.pilha_compra.draw(len(baralho.compra))
        self.pilha_descarte.draw(len(baralho.descarte))
        self.orbe.draw(self.player.ap, self.player.ap_max)

        self.ator_player.draw()
        self.barra_player.draw()
        for inimigo in self.inimigos:
            inimigo.ator.draw()
            if inimigo.status.is_alive():
                inimigo.barra.draw()
                if self.gerenciador.estado == "turno_jogador":
                    inimigo.intencao.draw(inimigo.ator.x_centro, inimigo.barra.barra.y - 6, self.player)

        # só mostra a seta quando tem mais de um inimigo pra escolher
        vivos = [i for i in self.inimigos if i.status.is_alive()]
        if len(vivos) > 1 and self.alvo in vivos:
            desenhar_seta_alvo(self.alvo.ator.x_centro, self.alvo.barra.barra.y - 50)

        self.mao.draw(baralho.mao, self._hover)

        resultado = self.gerenciador.resultado()
        if resultado and self._todos_livres():
            centralizado("VITÓRIA" if resultado == "vitoria" else "DERROTA", 200, 8,
                         fonte_pixel.DOURADO if resultado == "vitoria" else fonte_pixel.VERMELHO)

        # abre por último pra o "print" da tela já pegar o frame completo
        if self._pilha_pedida == "descarte":
            self.visualizador.abrir("Pilha de descarte", baralho.descarte)
        elif self._pilha_pedida == "compra":
            # em ordem alfabética pra não entregar a ordem real das compras
            self.visualizador.abrir("Pilha de compra", sorted(baralho.compra, key=lambda c: c.nome))
        self._pilha_pedida = None