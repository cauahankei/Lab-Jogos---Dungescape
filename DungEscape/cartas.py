from PPlay.sprite import Sprite
from utils import asset_path

# classe de carta, contendo as infos de cada carta.
# alem do dano, agora ela tambem pode dar escudo (pra cartas de defesa
# tipo "Escudo") -- uma carta pode ter os dois ao mesmo tempo tb, pra
# quando formos fazer cartas como "Bater e Defender" (GDD 3.3) depois.
class Carta(Sprite):
    def __init__(self, imagem, nome, custo, dano=0, escudo=0):
        Sprite.__init__(self, asset_path(imagem))
        self.nome = nome
        self.custo = custo
        self.dano = dano
        self.escudo = escudo

    # aplica o efeito da carta de verdade: causa dano no alvo (o inimigo)
    # e/ou da escudo pra quem jogou a carta (o player). e por isso que a
    # carta agora e "funcional" e nao so um dado visual.
    def usar(self, usuario, alvo=None):
        if self.dano > 0:
            alvo.recebe_dano(self.dano)
        if self.escudo > 0:
            usuario.recebe_escudo(self.escudo)

# ================================================================
# CARTAS DE TESTE DO PLAYER (valores genericos, sem balanceamento)
# ================================================================

def criar_corte_basico():
    return Carta(asset_path("assets", "Cartas", "carta1.png"), "Corte Básico", custo=2, dano=5)

def criar_escudo():
    return Carta(asset_path("assets", "Cartas", "carta2.png"), "Escudo", custo=1, escudo=5)
