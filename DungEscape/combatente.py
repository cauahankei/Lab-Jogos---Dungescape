import random

MULT_VULNERAVEL = 1.5                # GDD: vulnerável aumenta o dano recebido em 50%
STATUS_COM_DURACAO = ("vulneravel",)  # esses perdem 1 por rodada; os outros ficam até o fim da luta


class Combatente:
    def __init__(self, nome, vida, vida_max):
        self.nome = nome
        self.vida = vida
        self.vida_max = vida_max
        self.escudo = 0
        self.status = {}   # nome -> valor. forca = bônus de dano; vulneravel = turnos que faltam

    # ---------- status ----------
    # aplicar de novo soma (2 de força + 2 de força = 4)
    def aplicar_status(self, nome, valor):
        self.status[nome] = self.status.get(nome, 0) + valor

    def tem_status(self, nome):
        return self.status.get(nome, 0) > 0

    def limpar_status(self):
        self.status = {}
        self.escudo = 0

    # chamado uma vez por rodada, depois que os inimigos agiram
    def fim_de_rodada(self):
        for nome in STATUS_COM_DURACAO:
            if self.tem_status(nome):
                self.status[nome] -= 1
                if self.status[nome] <= 0:
                    del self.status[nome]

    # ---------- dano ----------
    # dano que ESSE combatente causa (a força soma no dano base)
    def dano_causado(self, base):
        return max(0, base + self.status.get("forca", 0))

    # vulnerável aumenta o dano recebido (arredonda pra baixo), depois o escudo
    # come o que puder e o resto vai na vida
    def recebe_dano(self, qnt):
        if self.tem_status("vulneravel"):
            qnt = int(qnt * MULT_VULNERAVEL)
        absorvido = min(self.escudo, qnt)
        self.escudo -= absorvido
        self.vida = max(0, self.vida - (qnt - absorvido))

    def recebe_escudo(self, qnt):
        self.escudo += qnt

    def is_alive(self):
        return self.vida > 0

    # ainda não sabemos se o escudo vai zerar todo turno mesmo, por enquanto zera
    def start_turno(self):
        self.escudo = 0


class Inimigo(Combatente):
    def __init__(self, nome, vida, acoes, ator_id):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.acoes = acoes
        self.ator_id = ator_id
        self.proxima_acao = None
        self.sortear_acao()      # já nasce sabendo o que vai fazer no 1º turno

    def sortear_acao(self):
        pesos = []
        for acao in self.acoes:
            pesos.append(acao["peso"])
        escolhida = random.choices(self.acoes, weights=pesos)[0]
        self.proxima_acao = {"tipo": escolhida["tipo"],
                            "valor": self._valor_da_acao(escolhida)}

    def _valor_da_acao(self, acao):
        if acao["tipo"] == "ataque":
            return acao["dano"]
        return acao["escudo"]


    def agir(self, alvo):
        acao = self.proxima_acao
        if acao["tipo"] == "ataque":
            alvo.recebe_dano(self.dano_causado(acao["valor"]))
        elif acao["tipo"] == "escudo":
            self.recebe_escudo(acao["valor"])
        self.sortear_acao()      # decide já a ação do próximo turno
        return acao

class Player(Combatente):
    def __init__(self, nome="Aprendiz", vida=80, ap_max=3, baralho=None, tamanho_mao=5):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.ap_max = ap_max
        self.ap = ap_max
        self.baralho = baralho
        self.tamanho_mao = tamanho_mao

    # False (sem gastar nada) se não tiver AP pra pagar a carta
    def gasta_ap(self, custo):
        if self.ap < custo:
            return False
        self.ap -= custo
        return True

    # começo do turno: escudo zera, AP enche e a mão completa até tamanho_mao
    # (se já tiver mais que isso, não compra nada)
    def start_turno(self):
        super().start_turno()
        self.ap = self.ap_max
        if self.baralho is not None:
            self.baralho.comprar(self.tamanho_mao - len(self.baralho.mao))


# ---------------------------------------------------------------
# Catálogo de inimigos. Pra criar um novo: põe uma linha aqui e as
# animações dele em ator.py (com o mesmo nome do ator_id).
# ---------------------------------------------------------------
INIMIGOS = {
    "goblin": dict(nome="Goblin", vida=60, ator_id="goblin",
                   acoes=[
                       {"tipo": "ataque", "dano": 10, "peso": 70},
                       {"tipo": "escudo", "escudo": 8, "peso": 30},
                   ]),

    "slime": dict(nome="Slime", vida=60, ator_id="slime",
                   acoes=[
                       {"tipo": "ataque", "dano": 8, "peso": 20},
                       {"tipo": "escudo", "escudo": 15, "peso": 80},
                   ]),
                   
}


def criar_inimigo(id_inimigo):
    return Inimigo(**INIMIGOS[id_inimigo])


# teste rápido no terminal: python combatente.py
if __name__ == "__main__":
    jogador = Player()
    inimigo = criar_inimigo("goblin")

    jogador.recebe_escudo(10)
    inimigo.agir(jogador)
    print("vida:", jogador.vida, "| escudo:", jogador.escudo, "| vivo?", jogador.is_alive())

    inimigo.aplicar_status("vulneravel", 2)
    antes = inimigo.vida
    inimigo.recebe_dano(10)
    print("goblin vulnerável levou 10 ->", antes - inimigo.vida, "de dano")
