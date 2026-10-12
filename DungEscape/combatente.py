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

class Inimigo1(Combatente):
    def __init__(self, nome="inimigo1", vida=20, dano_ataque=15):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.dano_ataque = dano_ataque

    # unica acao que o inimigo1 tem, segundo o GDD: atacar
    def agir(self, alvo):
        alvo.recebe_dano(self.dano_ataque)
        return {"acao": "ataque"}


class Player(Combatente):
    def __init__(self, nome="Aprendiz", vida=50, ap_max=3, baralho=None, tamanho_mao=5):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.ap_max = ap_max
        self.ap = ap_max

        #inclui baralho e tamanho de mao na classe do player
        self.baralho = baralho
        self.tamanho_mao = tamanho_mao

    # tenta gastar AP pra jogar uma carta; devolve False sem gastar nada
    # se não tiver AP suficiente (mesmo padrão usado no resto do projeto)
    def gasta_ap(self, custo):
        if self.ap < custo:
            return False
        self.ap -= custo
        return True

    # no inicio do turno: escudo zera, AP enche e completa a mao ate tamanho_mao
    # (se ja tiver mais que isso, nao compra nada)
    def start_turno(self):
        super().start_turno()
        self.ap = self.ap_max
        if self.baralho is not None:
            self.baralho.comprar(self.tamanho_mao - len(self.baralho.mao))



#apenas para testes direto no terminal, não faz nada quando importado, apenas quando esse codigo é rodado diretamente
if __name__ == "__main__":
    jogador = Player()
    inimigo = Inimigo1()

    jogador.recebe_escudo(10)
    retorno = inimigo.agir(jogador)
    
    print("retorno:", retorno)
    print("vida:", jogador.vida, "| escudo:", jogador.escudo)
    print("tá vivo?", jogador.is_alive())
