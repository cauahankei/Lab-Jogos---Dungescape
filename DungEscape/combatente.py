# Lógica pura de combate: sem pygame, sem imagem. Dá pra testar só no terminal.


class Combatente:
    def __init__(self, nome, vida, vida_max):
        self.nome = nome
        self.vida = vida
        self.vida_max = vida_max
        self.escudo = 0

    # o escudo come o dano primeiro, o que sobrar vai na vida
    def recebe_dano(self, qnt):
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
    def __init__(self, nome, vida, dano_ataque, ator_id):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.dano_ataque = dano_ataque
        self.ator_id = ator_id  # qual entrada de ANIMACOES (ator.py) desenha ele

    # por enquanto todo inimigo só ataca, igual no GDD
    def agir(self, alvo):
        alvo.recebe_dano(self.dano_ataque)
        return {"acao": "ataque"}


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
    "goblin": dict(nome="Goblin", vida=60, dano_ataque=10, ator_id="goblin"),
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
