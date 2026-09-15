class Combatente:
    def __init__(self, nome, vida_max):
        self.nome = nome
        self.vida_max = vida_max
        self.vida = vida_max
        self.bloqueio = 0

    def receber_dano(self, quantidade):
        # o bloqueio absorve primeiro
        dano_absorvido = min(self.bloqueio, quantidade)
        self.bloqueio -= dano_absorvido
        dano_real = quantidade - dano_absorvido
        self.vida = max(0, self.vida - dano_real)
        return dano_real   # devolve pra cena poder mostrar o número na tela

    def ganhar_bloqueio(self, quantidade):
        self.bloqueio += quantidade

    def esta_vivo(self):
        return self.vida > 0

    def iniciar_turno(self):
        self.bloqueio = 0  

    def __repr__(self):
        return f"{self.nome}: {self.vida}/{self.vida_max} HP, {self.bloqueio} bloqueio"
    
print("=== Teste 1: dano sem bloqueio ===")
heroi = Combatente("Herói", 50)
print("Inicial:      ", heroi)

dano = heroi.receber_dano(12)
print(f"Levou 12 → entrou {dano} de dano real")
print("Depois:       ", heroi)