import random
from PPlay.sprite import Sprite
from utils import asset_path
import fonte_pixel


# onde o texto vai em cima do PNG da carta
# se um dia mudar o desenho do png, e so ajustar esses numero aqui

CUSTO_CENTRO = (10, 10)     
NOME_CENTRO_X = 39          
NOME_TOPO_1 = 11            
NOME_TOPO_2 = 8             
NOME_LARGURA_MAX = 40
DESC_CENTRO_X = 34          
DESC_TOPO = 60              
DESC_ALTURA = 41
DESC_LARGURA_MAX = 44
SOMBRA = (30, 22, 32)       


# classe de carta, contendo as infos de cada carta
# o PNG da carta e so a ARTE (moldura + icone + placa/selo/caixa vazios).
# todo o texto (nome, custo, descricao) e escrito por codigo em cima dele,
# entao quando um buff/debuff muda um valor e so chamar atualizar_texto().

class Carta(Sprite):
    def __init__(self, imagem, nome, custo, dano=0, escudo=0, descricao="", **extras):
        Sprite.__init__(self, imagem)
        self.nome = nome
        self.custo = custo
        self.dano = dano
        self.escudo = escudo
        self.extras = dict(extras)
        self.descricao = descricao   # texto com {dano}, {escudo}, {compra}

        # guarda os valores ORIGINAIS pra saber depois se o numero ta
        # buffado (verde) ou debuffado (vermelho) na descricao
        self.custo_base = custo
        self.base = {"dano": dano, "escudo": escudo, **extras}


        self.arte = self.image
        self.atualizar_texto()

    # valor atual de um campo da descricao (dano, escudo ou extra)
    def _valor(self, campo):
        if campo == "dano":
            return self.dano
        if campo == "escudo":
            return self.escudo
        return self.extras[campo]

    # deixa o numero colorido: dourado normal, verde se subiu, vermelho se caiu
    def _numero(self, campo):
        atual, base = self._valor(campo), self.base[campo]
        if atual > base:
            return f"<v{atual}>"
        if atual < base:
            return f"<r{atual}>"
        return f"<{atual}>"

    # redesenha nome, custo e descricao por cima da arte limpa.
    # chama isso SEMPRE que mudar dano/escudo/custo/extras da carta
    # (ex: depois de aplicar Forca, ou de um debuff que reduz o custo).
    def atualizar_texto(self):
        img = self.arte.copy()

        txt_custo = str(self.custo)
        cor_custo = fonte_pixel.BRANCO
        if self.custo < self.custo_base:
            cor_custo = fonte_pixel.VERDE      # ficou mais barata
        elif self.custo > self.custo_base:
            cor_custo = fonte_pixel.VERMELHO   # ficou mais cara
        w = fonte_pixel.largura(txt_custo, 2)
        fonte_pixel.desenhar(img, CUSTO_CENTRO[0] - w // 2, CUSTO_CENTRO[1] - 5,
                             txt_custo, cor_custo, esc=2)


        linhas = fonte_pixel.quebrar(self.nome, NOME_LARGURA_MAX)
        topo = NOME_TOPO_1 if len(linhas) == 1 else NOME_TOPO_2
        for i, ln in enumerate(linhas):
            w = fonte_pixel.largura(ln)
            fonte_pixel.desenhar(img, NOME_CENTRO_X - w // 2, topo + i * 7, ln,
                                 fonte_pixel.BRANCO, sombra=SOMBRA)


        valores = {campo: self._numero(campo) for campo in self.base}
        texto = self.descricao.format(**valores)
        linhas = fonte_pixel.quebrar(texto, DESC_LARGURA_MAX)
        bloco = 5 + (len(linhas) - 1) * 8
        topo = DESC_TOPO + (DESC_ALTURA - bloco) // 2
        for i, ln in enumerate(linhas):
            w = fonte_pixel.largura(ln)
            fonte_pixel.desenhar(img, DESC_CENTRO_X - w // 2, topo + i * 8, ln)

        self.image = img

    # aplica o efeito da carta de verdade: causa dano no alvo (o inimigo)
    # e/ou da escudo pra quem jogou a carta (o player). e por isso que a
    # carta agora e "funcional" e nao so um dado visual.
    def usar(self, usuario, alvo=None):
        if self.dano > 0:
            alvo.recebe_dano(self.dano)
        if self.escudo > 0:
            usuario.recebe_escudo(self.escudo)



# as tres pilhas do jogador: compra, mao e descarte
class Baralho:
    def __init__(self, cartas, limite_mao=10):
        self.compra = list(cartas)
        self.mao = []
        self.descarte = []
        self.limite_mao = limite_mao
        random.shuffle(self.compra)

    # compra ate qnt cartas. se a pilha de compra acabar, embaralha o descarte
    # e ele vira a nova pilha de compra. qnt <= 0 nao compra nada
    def comprar(self, qnt):
        for _ in range(qnt):
            if len(self.mao) >= self.limite_mao:
                break
            if not self.compra:
                if not self.descarte:
                    break
                self.compra, self.descarte = self.descarte, []
                random.shuffle(self.compra)
            self.mao.append(self.compra.pop())

    def descartar(self, carta):
        if carta in self.mao:
            self.mao.remove(carta)
            self.descarte.append(carta)


def _png(nome):
    return asset_path("assets", "Cartas", nome)


# aqui tão as cartas que especificamos no gdd, ainda falta fazer
# as outras cartas além de ataque e defesa, FAHHHHHH
def criar_ataque():
    return Carta(_png("carta_ataque.png"), "Ataque", custo=1, dano=6,
                 descricao="Causa {dano}\nde dano.")

def criar_defesa():
    return Carta(_png("carta_defesa.png"), "Defesa", custo=1, escudo=5,
                 descricao="Ganha {escudo}\nde escudo.")

def criar_foco():  # TODO: comprar cartas
    return Carta(_png("carta_foco.png"), "Foco", custo=1, compra=2,
                 descricao="Compra {compra}\ncartas do\nbaralho.")

def criar_corte_rapido():
    return Carta(_png("carta_corte_rapido.png"), "Corte Rápido", custo=0, dano=3,
                 descricao="Causa {dano}\nde dano.\nCusto zero.")

def criar_corte_duplo():  # TODO: bater 2 vezes (hoje bate 1)
    return Carta(_png("carta_corte_duplo.png"), "Corte Duplo", custo=1, dano=4,
                 descricao="Dano {dano}\nduas vezes.")

def criar_contra_ataque():  # TODO: status Retaliacao
    return Carta(_png("carta_contra_ataque.png"), "Contra Ataque", custo=1, retaliacao=4,
                 descricao="Ao ser atacado, devolve {retaliacao} de dano.")

def criar_fortalecer():  # TODO: status Forca
    return Carta(_png("carta_fortalecer.png"), "Fortalecer", custo=1, forca=2,
                 descricao="Ganha {forca}\nde [força].\nAtaques\ncausam +{forca}.")

def criar_golpe_baixo():  # TODO: aplicar Vulneravel no inimigo
    return Carta(_png("carta_golpe_baixo.png"), "Golpe Baixo", custo=1, dano=6,
                 descricao="Causa {dano}\nde dano e\naplica\n[vulnerável].")

def criar_bater_defender():
    return Carta(_png("carta_bater_defender.png"), "Bater e Defender", custo=2, dano=5, escudo=5,
                 descricao="Causa {dano}\nde dano e\nganha {escudo}\nde escudo.")

def criar_golpe_pesado():  # TODO: aplicar Vulneravel no player
    return Carta(_png("carta_golpe_pesado.png"), "Golpe Pesado", custo=2, dano=14,
                 descricao="Causa {dano}\nde dano.\nVocê fica\n[vulnerável].")


# nomes antigos, so pra cena_combate.py continuar funcionando sem mexer
# ainda tem que mudar o cena_combate pra trocar pelos nomes novos 
# e incluir as outras cartas man

def criar_corte_basico():
    return criar_ataque()

def criar_escudo():
    return criar_defesa()
