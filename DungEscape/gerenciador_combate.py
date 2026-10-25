# Regras do combate (de quem é a vez, quem leva o quê). Não desenha nada.


class GerenciadorCombate:
    def __init__(self, jogador, inimigos):
        self.jogador = jogador
        self.inimigos = inimigos
        self.estado = "turno_jogador"   # ou "turno_inimigos" / "fim"
        self.jogador.start_turno()

    def inimigos_vivos(self):
        return [i for i in self.inimigos if i.is_alive()]

    # alvo que vale quando ninguém foi escolhido: o primeiro vivo
    def alvo_padrao(self):
        vivos = self.inimigos_vivos()
        return vivos[0] if vivos else None

    # "vitoria", "derrota" ou None se a luta ainda tá rolando
    def resultado(self):
        if not self.jogador.is_alive():
            return "derrota"
        if not self.inimigos_vivos():
            return "vitoria"
        return None

    def _checar_fim(self):
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

        self._checar_fim()
        return {"sucesso": True, "alvo": alvo}

    def terminar_turno_jogador(self):
        if self.estado == "turno_jogador":
            self.estado = "turno_inimigos"

    # todos os vivos atacam e devolve quem agiu (a cena usa isso pras animações).
    # se o jogador cair no meio, os próximos nem chegam a atacar
    def turno_inimigos(self):
        if self.estado != "turno_inimigos":
            return []

        agiram = []
        for inimigo in self.inimigos_vivos():
            inimigo.agir(self.jogador)
            agiram.append(inimigo)
            if not self.jogador.is_alive():
                break

        self.estado = "turno_jogador"
        self._checar_fim()
        if self.estado != "fim":
            self.jogador.start_turno()
        return agiram


# teste rápido no terminal: python gerenciador_combate.py
if __name__ == "__main__":
    from combatente import Player, criar_inimigo

    jogador = Player()
    inimigos = [criar_inimigo("goblin"), criar_inimigo("goblin")]
    g = GerenciadorCombate(jogador, inimigos)

    g.terminar_turno_jogador()
    print("agiram:", [i.nome for i in g.turno_inimigos()], "| vida do jogador:", jogador.vida)
    print("estado:", g.estado, "| resultado:", g.resultado())
