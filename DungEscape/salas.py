from PPlay.scenemanager import Scene
from PPlay.window import Window
from PPlay.animation import Animation
from PPlay.uikit import Button
from PPlay.tween import Tween
from cena_combate import CenaCombate
from cena_mapa import fundo_borrado
from encontros import sortear_encontro
from hud import BarraVida, centralizado
from utils import asset_path
import fonte_pixel
import fluxo


def _botao(texto, x, y, largura=240, altura=52):
    botao = Button(largura, altura, texto, cor_base=(88, 58, 44), cor_hover=(140, 92, 60))
    botao.set_position(x - largura / 2, y)
    return botao


# Combate de uma sala do mapa: mantém vida e baralho entre lutas e vai direto à tela de
# morte quando o jogador perde.
class CombateDaJornada(CenaCombate):
    _usar_tela_resultado_padrao = False

    def __init__(self, jornada, no, categoria=None):
        # todas as cartas voltam pra pilha de compra antes da luta
        jornada.player.baralho.reiniciar()
        # A categoria pode ser fixada para o boss; salas comuns usam a dificuldade do nó.
        super().__init__(sortear_encontro(categoria or no.dificuldade), jornada.player)
        self.no = no
        self.botao_continuar = _botao("Continuar", self.janela.width / 2, 320)

    def _terminou(self):
        if self.gerenciador.resultado() is None or self.visualizador.aberta or not self._todos_livres():
            return False
        # a morte já tem que ter começado (senão o botão pisca no 1º frame depois do golpe final)
        mortos = [i.ator for i in self.inimigos if not i.status.is_alive()]
        if not self.player.is_alive():
            mortos.append(self.ator_player)
        return all(ator.estado == "death" for ator in mortos)

    def loop(self):
        super().loop()
        if not self._terminou():
            return
        if self.gerenciador.resultado() == "derrota":
            fluxo.fim_do_combate("derrota", self.no)
        elif self.no.tipo == "boss":
            fluxo.fim_do_combate("vitoria", self.no)
        else:
            self.botao_continuar.update()
            if self.botao_continuar.is_clicked():
                fluxo.fim_do_combate(self.gerenciador.resultado(), self.no)

    def draw(self):
        super().draw()
        if self.no.tipo != "boss" and self._terminou() and self.gerenciador.resultado() == "vitoria":
            self.botao_continuar.draw()


# Só serve pra mostrar a vida subindo na barra: a vida de verdade já foi restaurada
class _VidaExibida:
    def __init__(self, player, vida):
        self.vida, self.vida_max, self.escudo, self.status = vida, player.vida_max, 0, {}


# Fogueira: cura 30% da vida máxima do jogador.
class CenaFogueira(Scene):
    def __init__(self, jornada, no):
        super().__init__()
        player = jornada.player
        self.exibida = _VidaExibida(player, player.vida)
        cura = player.vida_max * 30 // 100
        player.vida = min(player.vida_max, player.vida + cura)
        self.curou = player.vida - self.exibida.vida
        Tween.to(self.exibida, "vida", player.vida, 1.4, "ease_out")

        self.player = player
        self.fundo = fundo_borrado(150)
        self.fogo = Animation(asset_path("assets", "mapa", "fogueira_anim.png"), 4)
        self.fogo.set_total_duration(600)
        centro = self.janela.width / 2
        self.fogo.set_position(centro - self.fogo.width / 2, 130)
        self.barra = BarraVida(self.exibida, 320, 22)
        self.barra.posicionar(centro, 470)
        self.botao = _botao("Continuar", centro, 560)

    def loop(self):
        Tween.update()
        self.fogo.update()
        self.botao.update()
        if self.botao.is_clicked():
            fluxo.ir_para_mapa()

    def draw(self):
        tela = Window.get_screen()
        tela.blit(self.fundo, (0, 0))
        self.fogo.draw()
        centralizado("FOGUEIRA", 40, 5, fonte_pixel.DOURADO)
        centralizado("VOCÊ DESCANSOU", 420, 3, fonte_pixel.CREME)
        self.barra.draw()
        texto = f"VIDA {int(self.exibida.vida)}/{self.player.vida_max}"
        w = fonte_pixel.largura(texto, 3)
        fonte_pixel.desenhar(tela, int((self.janela.width - w) / 2), 500, texto, fonte_pixel.BRANCO,
                             esc=3, sombra=(0, 0, 0))
        if self.curou:
            centralizado(f"+{self.curou} DE VIDA", 535, 2, fonte_pixel.VERDE)
        self.botao.draw()


# Telas simples com um título e um botão, pra sala do boss e pro fim de jogo
class _TelaAviso(Scene):
    TITULO = ""
    SUBTITULO = ""
    COR = fonte_pixel.DOURADO
    BOTAO = "Nova jornada"

    def __init__(self, *args):
        super().__init__()
        self.fundo = fundo_borrado(190)
        self.botao = _botao(self.BOTAO, self.janela.width / 2, 430)

    def acao(self):
        fluxo.iniciar_jornada()

    def loop(self):
        self.botao.update()
        if self.botao.is_clicked():
            self.acao()

    def draw(self):
        Window.get_screen().blit(self.fundo, (0, 0))
        centralizado(self.TITULO, 200, 7, self.COR)
        centralizado(self.SUBTITULO, 320, 2, fonte_pixel.CREME)
        self.botao.draw()


# Sala do boss usa a pool própria de encontros.
class CenaBoss(CombateDaJornada):
    def __init__(self, jornada, no):
        super().__init__(jornada, no, categoria="boss")


class CenaFimDeJogo(_TelaAviso):
    TITULO = "VOCÊ MORREU"
    SUBTITULO = "A MASMORRA VENCEU DESSA VEZ"
    COR = fonte_pixel.VERMELHO


class CenaVitoria(_TelaAviso):
    TITULO = "VITÓRIA!"
    SUBTITULO = "VOCÊ VENCEU! Por enquanto..."
    BOTAO = "Voltar ao menu"

    def acao(self):
        fluxo.ir_para_menu()


# Que sala abre pra cada tipo de nó do mapa. Evento e loja entram aqui quando forem feitos
# (e com peso maior que 0 em PESOS, no mapa.py, pra aparecerem no mapa).
SALAS = {
    "combate": CombateDaJornada,
    "fogueira": CenaFogueira,
    "boss": CenaBoss,
}


def criar_sala(jornada, no):
    if no.tipo == "evento":
        return jornada.eventos.criar_cena(jornada, no)
    if no.tipo not in SALAS:
        raise NotImplementedError(f"ainda não existe sala do tipo '{no.tipo}'")
    return SALAS[no.tipo](jornada, no)
