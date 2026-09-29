from animacao_direcional import AnimacaoDirecional
from utils import asset_path

ANIMACOES = {
    "goblin": {
        "escala": 6.0,
        "animacoes": {
            "idle":    {"arquivo": ("assets", "Goblin", "Idle.png"),    "frames": 4, "duracao": 600, "loop": True},
            "takehit": {"arquivo": ("assets", "Goblin", "TakeHit.png"), "frames": 4, "duracao": 400, "loop": False, "depois": "idle"},
            "death":   {"arquivo": ("assets", "Goblin", "Death.png"),   "frames": 4, "duracao": 500, "loop": False},
            "attack":  {"arquivo": ("assets", "Goblin", "Attack.png"), "frames": 8, "duracao": 500, "loop": False, "depois": "idle"}
        },
    },
    "player": {
        "escala": 6.0,
        "animacoes": {
            "idle":    {"arquivo": ("assets", "Player", "Idle.png"),    "frames": 8, "duracao": 600, "loop": True},
            "attack":  {"arquivo": ("assets", "Player", "Attack1.png"), "frames": 4, "duracao": 400, "loop": False, "depois": "idle"},
            "takehit": {"arquivo": ("assets", "Player", "TakeHit_Silhouette.png"), "frames": 4, "duracao": 400, "loop": False, "depois": "idle"},
        },
    },
}

class AtorAnimado:
    def __init__(self, nome_entidade, x_centro, chao_y, virado_para_esquerda=False):
        config = ANIMACOES[nome_entidade]

        self.nome_entidade = nome_entidade
        self.escala = config["escala"]
        self.config = config["animacoes"]
        self.x_centro = x_centro
        self.chao_y = chao_y

        self.animacoes = {}
        for nome, dados in self.config.items():
            anim = AnimacaoDirecional(asset_path(*dados["arquivo"]), dados["frames"], loop=dados["loop"], virado_para_esquerda=virado_para_esquerda,)
            anim.set_total_duration(dados["duracao"])
            anim.set_scale(self.escala, self.escala)

            if not dados["loop"]:
                anim.rodando = False
            self.animacoes[nome] = anim

        self.estado = "idle"
        self._posicionar()

    def _posicionar(self):
        anim = self.animacoes[self.estado]
        largura = anim.width * self.escala
        altura = anim.height * self.escala
        anim.set_position(self.x_centro - largura / 2, self.chao_y - altura)

    def tocar(self, nome):
        if nome not in self.animacoes:
            raise ValueError(f"'{nome}' não existe nas animações de '{self.nome_entidade}'")
        anim = self.animacoes[nome]
        anim.set_curr_frame(0)
        anim.rodando = True
        self.estado = nome
        self._posicionar()

    def topo_idle(self):
        idle = self.animacoes["idle"]
        return self.chao_y - idle.height * self.escala

    def update(self):
        anim = self.animacoes[self.estado]
        anim.update()

        dados = self.config[self.estado]
        if not dados["loop"] and not anim.rodando:
            proximo = dados.get("depois")
            if proximo is not None:
                self.tocar(proximo)

    def draw(self):
        self.animacoes[self.estado].draw()


#testando testando testando, isso nao roda se a classe for importada, só quando dá play direto aqui
if __name__ == "__main__":
    from PPlay.window import Window
    from PPlay.gameimage import GameImage

    janela = Window(1280, 720, "Teste do AtorAnimado")
    fundo = GameImage(asset_path("assets", "Background", "background.png"))
    chao_y = janela.altura * 0.85

    jogador = AtorAnimado("player", janela.largura * 0.2, chao_y)
    goblin = AtorAnimado("goblin", janela.largura * 0.8, chao_y, virado_para_esquerda=True)

    reacoes = ["takehit", "death"]
    proxima = 0

    while True:
        fundo.draw()

        if janela.mouse.button_down(1):
            print("clique")
            if jogador.estado == "idle":
                jogador.tocar("attack")
            if goblin.estado == "idle" and proxima < len(reacoes):
                goblin.tocar(reacoes[proxima])
                proxima += 1

        jogador.update()
        jogador.draw()
        goblin.update()
        goblin.draw()
        janela.update()