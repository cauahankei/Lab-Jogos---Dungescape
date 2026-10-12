from combatente import Player, Inimigo1
from cartas import criar_corte_basico

class GerenciadorCombate:
    def __init__(self, jogador, inimigos):
        self.jogador = jogador
        self.inimigos = inimigos
        self.estado = "turno_jogador"
        self.fila = []

        self.jogador.start_turno()

    def inimigos_vivos(self):
        vivos=[]
        for inimigo in self.inimigos:
            if inimigo.is_alive():
                vivos.append(inimigo)
        return vivos

    def alvo(self):
        vivos = self.inimigos_vivos()
        if vivos:
            return vivos[0]
        return None

    def jogar_carta(self, carta):
        if self.estado != "turno_jogador":
            return {"sucesso": False, "motivo": "fora_do_turno"}

        alvo = self.alvo()
        if alvo is None:
            return {"sucesso": False, "motivo": "sem_alvo"}

        if not self.jogador.gasta_ap(carta.custo):
            return {"sucesso": False, "motivo": "ap_insuficiente"}

        carta.usar(self.jogador, alvo)
        if self.jogador.baralho is not None:
            self.jogador.baralho.descartar(carta)

        return {"sucesso": True, "alvo": alvo}

    def terminar_turno_jogador(self):
        if self.estado != "turno_jogador":
            return

        self.estado = "turno_inimigos"
        self.fila = self.inimigos_vivos()

    def terminar_turno_inimigos(self):
        self.jogador.start_turno()
        self.estado = "turno_jogador"
        self.fila = []

    def turno_inimigos(self):
        if self.estado != "turno_inimigos":
            return
        for inimigo in self.fila:
            inimigo.agir(self.jogador)

        self.terminar_turno_inimigos()








#teste teste teste

if __name__ == "__main__":

    from PPlay.window import Window
    janela = Window(1280, 720, "Teste do Gerenciador")

    jogador=Player()

    print("AP antes do gerenciador existir:", jogador.ap)

    inimigo = Inimigo1()
    inimigo2 = Inimigo1()

    gerenciador = GerenciadorCombate(jogador, [inimigo, inimigo2])

    result = gerenciador.jogar_carta(criar_corte_basico())
    
    alvo = gerenciador.alvo()
    print("AP depois do gerenciador ser criado:", jogador.ap)
    print("estado:", gerenciador.estado)
    print("fila_inimigos:", gerenciador.fila)
    print(result["sucesso"], result.get("alvo"))
    if result["sucesso"]:
        print("atingiu:", result["alvo"].nome, "| vida agora:", result["alvo"].vida)

    gerenciador.terminar_turno_jogador()

    print("estado:", gerenciador.estado)
    print("fila_inimigos:", gerenciador.fila)