# Lógica pura do mapa: sem pygame, sem imagem. Dá pra testar só no terminal.
# O mapa é um grafo em andares, como o do Slay the Spire: começa embaixo (andar 0),
# os caminhos vão se abrindo e juntando, e no topo tem uma única sala de boss.
import random

ANDARES = 12     # contando o andar do boss (o último)
COLUNAS = 7
CAMINHOS = 6     # quantos caminhos saem do começo (as pontas podem se encontrar no meio)

# Chance de cada tipo nas salas "livres". Evento e loja ainda não têm sala pra entrar,
# então ficam com peso 0. Quando forem feitos, é só subir o peso aqui.
PESOS = {"combate": 78, "fogueira": 22, "evento": 0, "loja": 0}

# a partir de qual andar cada tipo pode aparecer (nada de descanso logo no começo)
ANDAR_MINIMO = {"fogueira": 3, "loja": 2, "evento": 1}

# esses não podem aparecer duas vezes seguidas num caminho, nem lado a lado
SEM_REPETIR = ("fogueira", "loja")

# Andares em que TODAS as salas são fogueira, além do que vem antes do boss.
FOGUEIRAS_FIXAS_EXTRA = ()

# A fogueira é a única cura do jogo, então ela tem que estar ao alcance de qualquer caminho.
# CARGA é quanto de vida cada luta custa em média pra um jogador comum (que lê as intenções
# dos inimigos, defende e ataca o mais fraco, sem otimizar), medido simulando lutas com as
# regras reais. O mapa garante que NENHUM caminho junta mais que CARGA_MAXIMA entre duas
# fogueiras (56 = 70% dos 80 de vida do jogador). Se mexer nos inimigos, nas cartas ou nas
# listas de encontros, refaz a medição, senão o mapa fica injusto sem ninguém perceber.
# CARGA_MAXIMA não pode ser menor que a maior CARGA, senão nenhuma fogueira resolve.
CARGA = {"facil": 10, "medio": 26, "dificil": 45}
CARGA_MAXIMA = 56


# O começo é fácil, o meio é médio e só o último andar de combate (o que vem logo antes do
# descanso do boss) é difícil. Dois andares difíceis seguidos obrigariam fogueira em todo o
# andar do meio, e o mapa ficaria sempre igual.
def dificuldade_do_andar(andar, andares=ANDARES):
    # os andares de combate vão de 0 até andares-3; o antes do boss é descanso
    regulares = andares - 2
    posicao = andar / regulares
    if posicao < 0.3:
        return "facil"
    if posicao < 0.9:
        return "medio"
    return "dificil"


class NoSala:
    def __init__(self, andar, coluna, tipo="combate"):
        self.andar = andar
        self.coluna = coluna
        self.tipo = tipo              # combate, evento, loja, fogueira ou boss
        self.estado = "bloqueado"     # bloqueado, disponivel ou visitado
        self.proximos = []
        self.anteriores = []
        self.dificuldade = None       # só pra combate: facil, medio ou dificil
        self.dx = 0                   # desvio só visual, pro mapa não ficar quadradinho
        self.dy = 0

    def __repr__(self):
        return f"<{self.tipo} andar={self.andar} col={self.coluna} {self.estado}>"


class Mapa:
    def __init__(self, andares=ANDARES, colunas=COLUNAS):
        self.andares = andares
        self.colunas = colunas
        self.por_andar = [[] for _ in range(andares)]
        self.atual = None             # último nó visitado

    def todos(self):
        return [no for andar in self.por_andar for no in andar]

    def inicio(self):
        return self.por_andar[0]

    def boss(self):
        return self.por_andar[-1][0]

    def disponiveis(self):
        return [no for no in self.todos() if no.estado == "disponivel"]

    @property
    def concluido(self):
        return self.boss().estado == "visitado"

    # marca o nó como visitado, bloqueia as outras opções do andar e libera os próximos
    def visitar(self, no):
        if no.estado != "disponivel":
            raise ValueError(f"essa sala não pode ser visitada agora: {no}")
        for outro in self.por_andar[no.andar]:
            if outro is not no and outro.estado == "disponivel":
                outro.estado = "bloqueado"
        no.estado = "visitado"
        for proximo in no.proximos:
            proximo.estado = "disponivel"
        self.atual = no

    # ------------------------------------------------------------------ geração
    @classmethod
    def gerar(cls, semente=None, andares=ANDARES, colunas=COLUNAS, caminhos=CAMINHOS, pesos=None):
        rng = random.Random(semente)
        pesos = pesos or PESOS
        for _ in range(500):
            mapa = cls._montar(rng, andares, colunas, caminhos)
            if mapa is None:
                continue
            _sortear_tipos(rng, mapa, pesos)
            if _garantir_descansos(mapa):
                for no in mapa.inicio():
                    no.estado = "disponivel"
                return mapa
        raise RuntimeError("não consegui gerar um mapa justo")

    @classmethod
    def _montar(cls, rng, andares, colunas, caminhos):
        arestas = _tracar_caminhos(rng, andares, colunas, caminhos)
        if arestas is None:
            return None

        mapa = cls(andares, colunas)
        nos = {}
        for andar, lista in enumerate(arestas):
            for origem, destino in lista:
                for chave in ((andar, origem), (andar + 1, destino)):
                    if chave not in nos:
                        nos[chave] = NoSala(*chave)
                nos[(andar, origem)].proximos.append(nos[(andar + 1, destino)])
                nos[(andar + 1, destino)].anteriores.append(nos[(andar, origem)])

        # sala do boss: uma só, no meio do último andar, e todo mundo do andar antes chega nela
        boss = NoSala(andares - 1, colunas // 2, "boss")
        nos[(andares - 1, boss.coluna)] = boss
        for no in [n for (a, _), n in nos.items() if a == andares - 2]:
            no.proximos.append(boss)
            boss.anteriores.append(no)

        for (andar, coluna), no in sorted(nos.items()):
            mapa.por_andar[andar].append(no)
            if no.tipo != "boss":
                no.dx, no.dy = rng.randint(-10, 10), rng.randint(-8, 8)
        for andar in mapa.por_andar:
            andar.sort(key=lambda n: n.coluna)
        return mapa


def _cruza(arestas, origem, destino):
    for o, d in arestas:
        if (origem < o and destino > d) or (origem > o and destino < d):
            return True
    return False


# Cada caminho anda um andar por vez, pra mesma coluna ou pra uma do lado, e nunca cruza
# o fio de outro caminho. Devolve None se travou (aí o gerar tenta de novo).
def _tracar_caminhos(rng, andares, colunas, caminhos):
    passos = andares - 2          # liga os andares 0..andares-2; o boss é ligado depois
    arestas = [set() for _ in range(passos)]
    inicios = rng.sample(range(colunas), min(caminhos, colunas))
    for coluna in inicios:
        for andar in range(passos):
            opcoes = [d for d in (coluna - 1, coluna, coluna + 1)
                      if 0 <= d < colunas and not _cruza(arestas[andar], coluna, d)]
            if not opcoes:
                return None
            destino = rng.choice(opcoes)
            arestas[andar].add((coluna, destino))
            coluna = destino
    return arestas


def _sortear_tipos(rng, mapa, pesos):
    andares = mapa.andares
    antes_do_boss = andares - 2
    fixos = set(FOGUEIRAS_FIXAS_EXTRA) | {antes_do_boss}

    # 1º os andares fixos, pra o resto do mapa já saber o que tem do lado
    for andar in fixos:
        for no in mapa.por_andar[andar]:
            no.tipo = "fogueira"
    for no in mapa.por_andar[0]:
        no.tipo = "combate"

    for andar in range(1, antes_do_boss):
        if andar in fixos:
            continue
        for no in mapa.por_andar[andar]:
            no.tipo = _tipo_livre(rng, no, andar, pesos)

    for no in mapa.todos():
        if no.tipo == "combate":
            no.dificuldade = dificuldade_do_andar(no.andar, andares)


def _tipo_livre(rng, no, andar, pesos):
    vizinhos = no.anteriores + no.proximos
    irmaos = [filho for pai in no.anteriores for filho in pai.proximos if filho is not no]
    proibidos = {v.tipo for v in vizinhos + irmaos if v.tipo in SEM_REPETIR}

    opcoes, pesos_validos = [], []
    for tipo, peso in pesos.items():
        if peso <= 0 or andar < ANDAR_MINIMO.get(tipo, 0) or tipo in proibidos:
            continue
        opcoes.append(tipo)
        pesos_validos.append(peso)
    if not opcoes:
        return "combate"
    return rng.choices(opcoes, weights=pesos_validos)[0]


# estrito: ninguém do lado (pai, filho ou irmão) é fogueira. relaxado: só pai e filho.
def _pode_virar_fogueira(no, estrito=True):
    if no.tipo != "combate" or no.andar < ANDAR_MINIMO["fogueira"]:
        return False
    vizinhos = no.anteriores + no.proximos
    if estrito:
        vizinhos = vizinhos + [filho for pai in no.anteriores for filho in pai.proximos if filho is not no]
    return all(v.tipo != "fogueira" for v in vizinhos)


# Acha o primeiro nó cujo pior caminho até ele junta carga demais desde a última fogueira.
# Devolve (nó, cadeia de pais que causam o acúmulo) ou None se tá tudo certo.
def _primeiro_estouro(mapa):
    acumulado = {}
    for andar in mapa.por_andar:
        for no in andar:
            if no.tipo in ("fogueira", "boss"):
                acumulado[no] = (0, None)
                continue
            base, pai_pior = 0, None
            for pai in no.anteriores:
                valor = 0 if pai.tipo == "fogueira" else acumulado[pai][0]
                if valor >= base:
                    base, pai_pior = valor, pai
            acumulado[no] = (base + CARGA[no.dificuldade], pai_pior)
            if acumulado[no][0] > CARGA_MAXIMA:
                cadeia, atual = [no], pai_pior
                while atual is not None and atual.tipo == "combate":
                    cadeia.append(atual)
                    atual = acumulado[atual][1]
                return cadeia
    return None


# Põe fogueiras nos pontos que estouram o limite, até todo caminho ficar dentro dele.
# Prefere o nó que estourou e, se ele não puder, sobe pelos pais. Só aceita fogueiras irmãs
# quando não tem outro jeito (ex: dois andares difíceis seguidos pedem fogueira em todo o do meio).
def _garantir_descansos(mapa):
    for _ in range(300):
        cadeia = _primeiro_estouro(mapa)
        if cadeia is None:
            return True
        escolhido = next((n for n in cadeia if _pode_virar_fogueira(n)), None)
        if escolhido is None:
            escolhido = next((n for n in cadeia if _pode_virar_fogueira(n, estrito=False)), None)
        if escolhido is None:
            return False
        escolhido.tipo = "fogueira"
        escolhido.dificuldade = None
    return False


# teste rápido no terminal: python mapa.py
if __name__ == "__main__":
    mapa = Mapa.gerar(semente=1)
    for andar in reversed(range(mapa.andares)):
        linha = ["  .  "] * mapa.colunas
        for no in mapa.por_andar[andar]:
            linha[no.coluna] = f"{no.tipo[:3].upper():^5}"
        print(f"{andar:2d} " + " ".join(linha))
