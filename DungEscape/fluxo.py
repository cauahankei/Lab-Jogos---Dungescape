from PPlay.scenemanager import SceneManager
from encontros import sortear_encontro


# Quem decide qual cena vem depois de qual.
# As cenas só chamam estas funções, então nenhuma precisa conhecer as outras.
def iniciar_combate(player=None, encontro=None):
    from cena_combate import CenaCombate
    SceneManager.change_scene(CenaCombate(encontro or sortear_encontro("normal"), player))


def ir_para_recompensa(player):
    from cena_recompensa import CenaRecompensa
    SceneManager.change_scene(CenaRecompensa(player))

# ---------------------------------------------------------------------------
# Jornada: uma partida inteira, do começo do mapa até o boss.
# ---------------------------------------------------------------------------

# A jornada em andamento. None = ninguém tá numa jornada (ex: testando só a cena de combate).
jornada_atual = None


class Jornada:
    def __init__(self, semente=None):
        from combatente import Player
        from cartas import Baralho, deck_inicial
        from mapa import Mapa
        self.player = Player(baralho=Baralho(deck_inicial()))
        self.mapa = Mapa.gerar(semente)


def iniciar_jornada(semente=None):
    global jornada_atual
    jornada_atual = Jornada(semente)
    ir_para_mapa()


def ir_para_mapa():
    from cena_mapa import CenaMapa
    SceneManager.change_scene(CenaMapa(jornada_atual))


def ir_para_menu():
    global jornada_atual
    from menu import CenaMenu
    jornada_atual = None
    SceneManager.change_scene(CenaMenu())


# O mapa chama isto quando o jogador escolhe uma sala (a sala certa depende do tipo do nó)
def entrar_na_sala(no):
    from salas import criar_sala
    SceneManager.change_scene(criar_sala(jornada_atual, no))


# Depois de escolher (ou pular) a recompensa: volta pro mapa. Sem jornada, mantém o jeito
# antigo de antes do mapa existir, que era já abrir outra luta.
def depois_da_recompensa(player):
    if jornada_atual is None:
        iniciar_combate(player)
    else:
        ir_para_mapa()


# Botão "Continuar" do combate da jornada: ganhou vai pra recompensa, perdeu é fim de jogo
def fim_do_combate(resultado, no):
    if resultado == "vitoria":
        if no.tipo == "boss":
            from salas import CenaVitoria
            SceneManager.change_scene(CenaVitoria())
            return
        ir_para_recompensa(jornada_atual.player)
    else:
        from salas import CenaFimDeJogo
        SceneManager.change_scene(CenaFimDeJogo())
