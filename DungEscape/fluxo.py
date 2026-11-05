from PPlay.scenemanager import SceneManager
from encontros import sortear_encontro


# Quem decide qual cena vem depois de qual.
# As cenas só chamam estas funções, então nenhuma precisa conhecer as outras.
def iniciar_combate(player=None):
    from cena_combate import CenaCombate
    SceneManager.change_scene(CenaCombate(sortear_encontro("normal"), player))


def ir_para_recompensa(player):
    from cena_recompensa import CenaRecompensa
    SceneManager.change_scene(CenaRecompensa(player))