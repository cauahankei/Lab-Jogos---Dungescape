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
        self.vida-=max(0, self.vida-dano_real)

##soma escudo ao combatente
    def recebe_escudo(self, qnt):
        self.escudo+=qnt

##verifica se o combatente está vivo
    def is_alive(self):
        return self.vida>0

##ainda precisamos testar se vamos fzr desse jeito (zerar escudo a cada turno)
    def start_turno(self):
        self.escudo=0