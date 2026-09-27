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
        # CORRIGIDO: a formula antiga era "self.vida -= max(0, self.vida-dano_real)",
        # que dá resultado errado (ex: 8 de vida - 3 de dano dano_real virava 3 em vez de 5,
        # e um dano MAIOR que a vida atual simplesmente não fazia nada, o combatente
        # nunca morria). O certo é so subtrair o dano real e travar em 0:
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
# FICHAS DE TESTE (pra rodar os combates de teste)
# ================================================================

# Ficha do inimigo Goblin (GDD 3.4: "Goblin: 8 de vida... criatura pequena
# encontrada em bando de 3. Possui apenas a habilidade de atacar o
# Personagem"). O valor de vida (8) é o único número que o GDD realmente
# fixa pra esse inimigo -- o dano do ataque dele fica como "X dano"
# genérico no documento, então self.dano_ataque aqui é so um valor de
# teste pra podermos simular o combate; ajustar no balanceamento.
class Goblin(Combatente):
    def __init__(self, nome="Goblin", vida=8, dano_ataque=3):
        super().__init__(nome=nome, vida=vida, vida_max=vida)
        self.dano_ataque = dano_ataque

    # unica acao que o Goblin tem, segundo o GDD: atacar
    def ataca(self, alvo):
        alvo.recebe_dano(self.dano_ataque)


# Ficha do Player (Principe). O GDD (3.1) só diz que ele "possui uma
# quantia inicial FIXA de vida", sem dizer o número -- e também não fixa
# o valor máximo de Energia/AP (1.1 da Especificação de Game Objects só
# diz que existe). Por isso tudo aqui é valor de teste genérico mesmo,
# como você pediu.
class Player(Combatente):
    def __init__(self, nome="Principe", vida=50, ap_max=3):
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

    # no inicio do turno, alem do escudo (que ja zerava), o AP tambem
    # enche de novo (Especificacao de Game Objects, 1.1: "Energia (AP):
    # ...Valor maximo restaurado no inicio do turno")
    def start_turno(self):
        super().start_turno()
        self.ap = self.ap_max
