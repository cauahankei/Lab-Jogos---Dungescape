import random
from PPlay.sprite import Sprite
from utils import asset_path
import fonte_pixel

# ---------------------------------------------------------------
# Onde o texto cai em cima do PNG da carta (68x109, antes de escalar).
# Se mexer na arte, é só acertar esses números.
# ---------------------------------------------------------------
CUSTO_CENTRO = (10, 10)     # centro do selo do custo (canto de cima, esquerda)
NOME_CENTRO_X = 39          # centro da placa do nome
NOME_TOPO_1 = 11            # y do nome quando cabe em 1 linha
NOME_TOPO_2 = 8             # y da 1ª linha quando o nome tem 2
NOME_LARGURA_MAX = 40
DESC_CENTRO_X = 34          # centro da caixa de descrição
DESC_TOPO = 60
DESC_ALTURA = 41
DESC_LARGURA_MAX = 44
SOMBRA = (30, 22, 32)       # sombrinha atrás do nome
TAMANHO_CARTA = (68, 109)    # tamanho dos PNGs


# O PNG é só a arte (moldura, ícone, placa e caixa vazias). Nome, custo e
# descrição são escritos por código em cima, então buff/debuff = mudar o valor
# e chamar atualizar_texto().
# dano e escudo são atributos normais (o resto do jogo usa); qualquer outro
# número da carta (comprar, retaliação, força...) vai em carta.extras["nome"].
class Carta(Sprite):
    def __init__(self, imagem, nome, custo, dano=0, escudo=0, descricao="", **extras):
        Sprite.__init__(self, imagem)
        self.nome = nome
        self.custo = custo
        self.dano = dano
        self.escudo = escudo
        self.extras = dict(extras)
        self.descricao = descricao

        # valores originais, pra saber se o número tá buffado (verde) ou debuffado (vermelho)
        self.custo_base = custo
        self.base = {"dano": dano, "escudo": escudo, **extras}

        # a engine divide a mesma imagem entre todas as cartas iguais (cache).
        # então a arte limpa fica guardada e o texto é escrito numa cópia
        self.arte = self.image
        self.atualizar_texto()

    # valor atual de um campo da descrição (dano, escudo ou extra)
    def _valor(self, campo):
        if campo == "dano":
            return self.dano
        if campo == "escudo":
            return self.escudo
        return self.extras[campo]

    # dourado normal, verde se subiu, vermelho se caiu
    def _numero(self, campo):
        atual, base = self._valor(campo), self.base[campo]
        if atual > base:
            return f"<v{atual}>"
        if atual < base:
            return f"<r{atual}>"
        return f"<{atual}>"

    # redesenha nome, custo e descrição por cima da arte limpa.
    # chama sempre que mudar dano/escudo/custo/extras (Força, debuff de custo...)
    def atualizar_texto(self):
        img = self.arte.copy()

        # custo
        txt_custo = str(self.custo)
        cor_custo = fonte_pixel.BRANCO
        if self.custo < self.custo_base:
            cor_custo = fonte_pixel.VERDE      # ficou mais barata
        elif self.custo > self.custo_base:
            cor_custo = fonte_pixel.VERMELHO   # ficou mais cara
        w = fonte_pixel.largura(txt_custo, 2)
        fonte_pixel.desenhar(img, CUSTO_CENTRO[0] - w // 2, CUSTO_CENTRO[1] - 5,
                             txt_custo, cor_custo, esc=2)

        # nome (quebra em 2 linhas sozinho se não couber)
        linhas = fonte_pixel.quebrar(self.nome, NOME_LARGURA_MAX)
        topo = NOME_TOPO_1 if len(linhas) == 1 else NOME_TOPO_2
        for i, ln in enumerate(linhas):
            w = fonte_pixel.largura(ln)
            fonte_pixel.desenhar(img, NOME_CENTRO_X - w // 2, topo + i * 7, ln,
                                 fonte_pixel.BRANCO, sombra=SOMBRA)

        # descrição, com os valores de agora
        valores = {campo: self._numero(campo) for campo in self.base}
        texto = self.descricao.format(**valores)
        linhas = fonte_pixel.quebrar(texto, DESC_LARGURA_MAX)
        bloco = 5 + (len(linhas) - 1) * 8
        topo = DESC_TOPO + (DESC_ALTURA - bloco) // 2
        for i, ln in enumerate(linhas):
            w = fonte_pixel.largura(ln)
            fonte_pixel.desenhar(img, DESC_CENTRO_X - w // 2, topo + i * 8, ln)

        self.image = img

    # dano vai pro alvo, escudo vai pra quem jogou
    def usar(self, usuario, alvo=None):
        if self.dano > 0:
            alvo.recebe_dano(self.dano)
        if self.escudo > 0:
            usuario.recebe_escudo(self.escudo)


# As três pilhas do jogador: compra, mão e descarte.
class Baralho:
    def __init__(self, cartas, limite_mao=10):
        self.compra = list(cartas)
        self.mao = []
        self.descarte = []
        self.limite_mao = limite_mao
        random.shuffle(self.compra)

    # compra até qnt cartas; se a compra acabar, o descarte é embaralhado e
    # vira a nova compra. qnt <= 0 não compra nada
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


# ---------------------------------------------------------------
# Catálogo das cartas do GDD. Os valores são de teste (o GDD só diz "X").
# Na descrição, {dano}/{escudo}/extras viram o número na hora, "\n" quebra
# linha e [palavra] fica ciano.
# As marcadas com TODO ainda só fazem dano/escudo, o efeito especial vem depois.
# ---------------------------------------------------------------
CARTAS = {
    "ataque": dict(arquivo="carta_ataque.png", nome="Ataque", custo=1, dano=6,
                   descricao="Causa {dano}\nde dano."),
    "defesa": dict(arquivo="carta_defesa.png", nome="Defesa", custo=1, escudo=5,
                   descricao="Ganha {escudo}\nde escudo."),
    "foco": dict(arquivo="carta_foco.png", nome="Foco", custo=1, compra=2,                   # TODO: comprar
                 descricao="Compra {compra}\ncartas do\nbaralho."),
    "corte_rapido": dict(arquivo="carta_corte_rapido.png", nome="Corte Rápido", custo=0, dano=3,
                         descricao="Causa {dano}\nde dano.\nCusto zero."),
    "corte_duplo": dict(arquivo="carta_corte_duplo.png", nome="Corte Duplo", custo=1, dano=4,   # TODO: bater 2x
                        descricao="Dano {dano}\nduas vezes."),
    "contra_ataque": dict(arquivo="carta_contra_ataque.png", nome="Contra Ataque", custo=1,   # TODO: Retaliação
                          retaliacao=4, descricao="Ao ser atacado, devolve {retaliacao} de dano."),
    "fortalecer": dict(arquivo="carta_fortalecer.png", nome="Fortalecer", custo=1, forca=2,   # TODO: Força
                       descricao="Ganha {forca}\nde [força].\nAtaques\ncausam +{forca}."),
    "golpe_baixo": dict(arquivo="carta_golpe_baixo.png", nome="Golpe Baixo", custo=1, dano=6,  # TODO: Vulnerável
                        descricao="Causa {dano}\nde dano e\naplica\n[vulnerável]."),
    "bater_defender": dict(arquivo="carta_bater_defender.png", nome="Bater e Defender", custo=2,
                           dano=5, escudo=5,
                           descricao="Causa {dano}\nde dano e\nganha {escudo}\nde escudo."),
    "golpe_pesado": dict(arquivo="carta_golpe_pesado.png", nome="Golpe Pesado", custo=2, dano=14,  # TODO: Vulnerável
                         descricao="Causa {dano}\nde dano.\nVocê fica\n[vulnerável]."),
}


def criar_carta(id_carta):
    dados = dict(CARTAS[id_carta])
    arquivo = dados.pop("arquivo")
    return Carta(asset_path("assets", "Cartas", arquivo), **dados)


def deck_inicial():
    return [criar_carta("ataque") for _ in range(5)] + [criar_carta("defesa") for _ in range(4)]
