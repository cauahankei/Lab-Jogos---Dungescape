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


# ---------------------------------------------------------------
# Efeitos que uma carta pode ter. Cada um só roda se a carta tem o campo
# com valor > 0, então uma carta nova é só juntar os campos que quiser.
# A ordem importa: dano vem antes dos status (senão o Golpe Baixo já
# bateria com o vulnerável aplicado).
# Nenhum deles sabe da cena: só mexem em quem usou e em quem é o alvo.
# ---------------------------------------------------------------
def _efeito_dano(carta, usuario, alvo):
    alvo.recebe_dano(usuario.dano_causado(carta.base["dano"]))


def _efeito_escudo(carta, usuario, alvo):
    usuario.recebe_escudo(carta.base["escudo"])


def _efeito_compra(carta, usuario, alvo):
    baralho = getattr(usuario, "baralho", None)   # inimigo não tem baralho
    if baralho is not None:
        baralho.comprar(carta.base["compra"])


def _efeito_forca(carta, usuario, alvo):
    usuario.aplicar_status("forca", carta.base["forca"])


def _efeito_vulneravel(carta, usuario, alvo):
    alvo.aplicar_status("vulneravel", carta.base["vulneravel"])


EFEITOS = {
    "dano": _efeito_dano,
    "escudo": _efeito_escudo,
    "compra": _efeito_compra,
    "forca": _efeito_forca,
    "vulneravel": _efeito_vulneravel,
}


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

    # roda todos os efeitos da carta (ver EFEITOS lá em cima)
    def usar(self, usuario, alvo=None):
        for campo, efeito in EFEITOS.items():
            if self.base.get(campo, 0) > 0:
                efeito(self, usuario, alvo)

    # deixa o dano mostrado na carta igual ao que ela vai causar de verdade
    # (com a Força de quem joga). só redesenha se o número mudou
    def sincronizar(self, usuario):
        novo = usuario.dano_causado(self.base["dano"]) if self.base["dano"] > 0 else 0
        if novo != self.dano:
            self.dano = novo
            self.atualizar_texto()


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

    def todas(self):
        return self.compra + self.mao + self.descarte

    # atualiza o dano de todas as cartas (mão e pilhas) pro jogador atual
    def sincronizar(self, usuario):
        for carta in self.todas():
            carta.sincronizar(usuario)


# ---------------------------------------------------------------
# Catálogo de cartas. Os valores são de teste (o GDD só diz "X").
# Na descrição, {dano}/{escudo}/extras viram o número na hora, "\n" quebra
# linha e [palavra] fica ciano.
# Campos com efeito: dano, escudo, compra, forca, vulneravel (ver EFEITOS).
# Faltam entrar: Corte Rápido, Corte Duplo, Contra Ataque, Bater e Defender e
# Golpe Pesado (a arte deles já tá em assets/Cartas).
# ---------------------------------------------------------------
CARTAS = {
    "ataque": dict(arquivo="carta_ataque.png", nome="Ataque", custo=1, dano=6,
                   descricao="Causa {dano}\nde dano."),
    "defesa": dict(arquivo="carta_defesa.png", nome="Defesa", custo=1, escudo=5,
                   descricao="Ganha {escudo}\nde escudo."),
    "foco": dict(arquivo="carta_foco.png", nome="Foco", custo=1, compra=2,
                 descricao="Compra {compra}\ncartas do\nbaralho."),
    "fortalecer": dict(arquivo="carta_fortalecer.png", nome="Fortalecer", custo=1, forca=2,
                       descricao="Ganha {forca}\nde [força].\nAtaques\ncausam +{forca}."),
    "golpe_baixo": dict(arquivo="carta_golpe_baixo.png", nome="Golpe Baixo", custo=1, dano=6,
                        vulneravel=2,
                        descricao="Causa {dano}\nde dano e\naplica {vulneravel}\n[vulnerável]."),
}


def criar_carta(id_carta):
    dados = dict(CARTAS[id_carta])
    arquivo = dados.pop("arquivo")
    return Carta(asset_path("assets", "Cartas", arquivo), **dados)


def deck_inicial():
    receita = {"ataque": 4, "defesa": 3, "foco": 1, "fortalecer": 1, "golpe_baixo": 1}
    return [criar_carta(id_carta) for id_carta, qnt in receita.items() for _ in range(qnt)]
