# Regras do combate (de quem é a vez, quem leva o quê). Não desenha nada.


class GerenciadorCombate:
    def __init__(self, jogador, inimigos):
        self.jogador = jogador
        self.inimigos = inimigos
        self.fila = []
        self.estado = "turno_jogador"   # ou "turno_inimigos" / "fim"
        self.jogador.limpar_status()    # status de uma luta anterior nao passam pra essa
        self.jogador.start_turno()
        self.sincronizar_cartas()

    # as cartas mostram o dano real (com Forca), entao atualiza depois de qualquer mudanca
    def sincronizar_cartas(self):
        if self.jogador.baralho is not None:
            self.jogador.baralho.sincronizar(self.jogador)

    def inimigos_vivos(self):
        vivos = []
        for inimigo in self.inimigos:
            if inimigo.is_alive():
                vivos.append(inimigo)
        return vivos

    # alvo que vale quando ninguem foi escolhido: o primeiro vivo
    def alvo_padrao(self):
        vivos = self.inimigos_vivos()
        if len(vivos) > 0:
            return vivos[0]
        return None

    # "vitoria", "derrota" ou None se a luta ainda ta rolando
    def resultado(self):
        if not self.jogador.is_alive():
            return "derrota"
        if not self.inimigos_vivos():
            return "vitoria"
        return None

    def checar_fim(self):
        if self.resultado():
            self.estado = "fim"

    def jogar_carta(self, carta, alvo=None):
        if self.estado != "turno_jogador":
            return {"sucesso": False, "motivo": "fora_do_turno"}

        if alvo is None or not alvo.is_alive():
            alvo = self.alvo_padrao()
        if alvo is None:
            return {"sucesso": False, "motivo": "sem_alvo"}

        if not self.jogador.gasta_ap(carta.custo):
            return {"sucesso": False, "motivo": "ap_insuficiente"}

        carta.usar(self.jogador, alvo)
        if self.jogador.baralho is not None:
            self.jogador.baralho.descartar(carta)

        self.sincronizar_cartas()
        self.checar_fim()
        return {"sucesso": True, "alvo": alvo}

    def terminar_turno_jogador(self):
        if self.estado == "turno_jogador":
            self.estado = "turno_inimigos"
            self.fila = self.inimigos_vivos()


    def proxima_acao_inimiga(self):
        if self.estado != "turno_inimigos":
            return None

        while len(self.fila) > 0:
            inimigo = self.fila.pop(0)      # tira o primeiro da fila
            if inimigo.is_alive():
                inimigo.agir(self.jogador)
                if not self.jogador.is_alive():
                    self.fila = []          # jogador morreu: os outros nao atacam
                return inimigo

        # a fila acabou: fim da rodada, os status com duracao (vulneravel) perdem 1 turno
        self.jogador.fim_de_rodada()
        for inimigo in self.inimigos:
            inimigo.fim_de_rodada()

        # e o turno dos inimigos termina
        self.estado = "turno_jogador"
        self.checar_fim()
        if self.estado != "fim":
            self.jogador.start_turno()
            self.sincronizar_cartas()
        return None

# teste rapido no terminal: python gerenciador_combate.py
if __name__ == "__main__":
    from combatente import Player, criar_inimigo

    jogador = Player()
    inimigos = [criar_inimigo("goblin"), criar_inimigo("goblin")]
    g = GerenciadorCombate(jogador, inimigos)

    g.terminar_turno_jogador()
    print("agiram:", [i.nome for i in g.turno_inimigos()], "| vida do jogador:", jogador.vida)
    print("estado:", g.estado, "| resultado:", g.resultado())
