class Combatente:

#seta os atributos iniciais do combatente
    def __init__(self, nome, vida, vida_max):
        self.nome=nome
        self.vida=vida
        self.vida_max=vida_max
        self.escudo=0

##calcula o dano ao combatente (consideirando reduçoes de escudo)
    def recebe_dano(self, qnt):
        dano_absorvido=min(self.escudo,qnt)
        dano_real=qnt-dano_absorvido
        self.escudo-=dano_absorvido
        self.vida = max(0, self.vida - dano_real)

##soma escudo ao combatente
    def recebe_escudo(self, qnt):
        self.escudo+=qnt

##verifica se o combatente está vivo
    def is_alive(self):
        return self.vida>0

##ainda precisamos testar se vamos fzr desse jeito (zerar escudo a cada turno)
    def start_turno(self):
        self.escudo=0


# ================================================================
# Tipos de combatente ("subclasses")
# ================================================================

class inimigo1(Combatente):
    def __init__(self, nome="inimigo1", vida=8, dano_ataque=99):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.dano_ataque = dano_ataque

    # unica acao que o inimigo1 tem, segundo o GDD: atacar
    def agir(self, alvo):
        alvo.recebe_dano(self.dano_ataque)
        return {"acao": "ataque"}


class Player(Combatente):
    def __init__(self, nome="Aprendiz", vida=50, ap_max=3):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.ap_max = ap_max
        self.ap = ap_max

    # tenta gastar AP pra jogar uma carta; devolve False sem gastar nada
    # se não tiver AP suficiente (mesmo padrão usado no resto do projeto)
    def gasta_ap(self, custo):
        if self.ap < custo:
            return False
        self.ap -= custo
        return True

    # no inicio do turno, alem do escudo (que ja zerava), o AP tambem enche de novo 
    def start_turno(self):
        super().start_turno()
        self.ap = self.ap_max

if __name__ == "__main__":
    jogador = Player()
    inimigo = inimigo1()

    jogador.recebe_escudo(10)
    retorno = inimigo.agir(jogador)
    
    print("retorno:", retorno)
    print("vida:", jogador.vida, "| escudo:", jogador.escudo)
