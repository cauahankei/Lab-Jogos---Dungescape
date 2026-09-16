from pathlib import Path
from PPlay.sprite import Sprite

BASE_DIR = Path(__file__).resolve().parent
def asset_path(*parts):
    return str(BASE_DIR.joinpath(*parts))


# classe de carta, contendo as infos de cada carta, ainda n serve pra mta coisa
# mas vai ser mto relevante em breve
class Carta(Sprite):
    def __init__(self, imagem, nome, custo, dano):
        Sprite.__init__(self, asset_path(imagem))
        self.nome = nome
        self.custo = custo
        self.dano = dano
