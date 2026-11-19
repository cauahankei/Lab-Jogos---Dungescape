import random

from PPlay.scenemanager import Scene
from PPlay.uikit import Button
from PPlay.window import Window

from cena_mapa import fundo_borrado
from hud import centralizado
import fonte_pixel
import fluxo


def _botao(texto, x, y, largura=240, altura=52):
    botao = Button(largura, altura, texto, cor_base=(88, 58, 44), cor_hover=(140, 92, 60))
    botao.set_position(x - largura / 2, y)
    return botao


class CenaPactoMorcego(Scene):
    def __init__(self, jornada, no):
        super().__init__()
        self.jornada = jornada
        self.player = jornada.player
        self.fundo = fundo_borrado(150)
        centro = self.janela.width / 2
        self.perdida = max(1, self.player.vida_max * 20 // 100)
        self.resultado = None
        self.botao_sacrificar = _botao(
            f"Perder {self.perdida} de vida",
            centro - 150, 430, largura=290
        )
        self.botao_recusar = _botao("Não aceitar", centro + 150, 430, largura=290)
        self.botao_continuar = _botao("Continuar", centro, 560)

    def loop(self):
        if self.resultado is None:
            self.botao_sacrificar.update()
            self.botao_recusar.update()
            if self.botao_sacrificar.is_clicked():
                perda_real = min(self.player.vida_max - 1, self.perdida)
                self.player.vida_max -= perda_real
                self.player.vida = min(self.player.vida, self.player.vida_max)
                trocadas = self.player.baralho.substituir_cartas("ataque", "mordida")
                self.player.baralho.sincronizar(self.player)
                self.resultado = (
                    f"{trocadas} ATAQUE{'S' if trocadas != 1 else ''} "
                    f"TROCADO{'S' if trocadas != 1 else ''} POR MORDIDA"
                )
            elif self.botao_recusar.is_clicked():
                self.resultado = "NADA ACONTECEU"
        else:
            self.botao_continuar.update()
            if self.botao_continuar.is_clicked():
                fluxo.ir_para_mapa()

    def draw(self):
        Window.get_screen().blit(self.fundo, (0, 0))
        centralizado("PACTO DE MORCEGO", 40, 5, fonte_pixel.DOURADO)
        centralizado("FORÇA EM TROCA DE SANGUE", 115, 3, fonte_pixel.CREME)
        centralizado("TODOS OS ATAQUES VIRAM MORDIDAS", 175, 3, fonte_pixel.DOURADO)
        centralizado("5 DE DANO + 2 DE VIDA", 215, 3, fonte_pixel.CREME)
        centralizado(f"VIDA MÁXIMA: {self.player.vida_max}", 340, 3, fonte_pixel.CREME)

        if self.resultado is None:
            centralizado(f"ACEITAR POR {self.perdida} DE VIDA MÁXIMA?", 290, 3, fonte_pixel.VERMELHO)
            self.botao_sacrificar.draw()
            self.botao_recusar.draw()
        else:
            cor = fonte_pixel.VERDE if self.resultado != "NADA ACONTECEU" else fonte_pixel.CREME
            centralizado(self.resultado, 485, 3, cor)
            self.botao_continuar.draw()


class CenaCaminhoEspiritual(Scene):
    def __init__(self, jornada, no):
        super().__init__()
        self.jornada = jornada
        self.player = jornada.player
        self.fundo = fundo_borrado(150)
        centro = self.janela.width / 2
        largura = 260
        colunas_x = (self.janela.width / 6, centro, self.janela.width * 5 / 6)
        self.botoes = {
            "forma_demoniaca": _botao(
                "Forças sombrias", colunas_x[0], 430, largura=260
            ),
            "apoteose": _botao(
                "Forças divinas", colunas_x[1], 430, largura=260
            ),
            "forma_deva": _botao(
                "Caminho da alma", colunas_x[2], 430, largura=260
            ),
        }
        self.botao_continuar = _botao("Continuar", centro, 560)
        self.escolha = None

    def loop(self):
        if self.escolha is None:
            for id_carta, botao in self.botoes.items():
                botao.update()
                if botao.is_clicked():
                    from cartas import criar_carta
                    self.player.baralho.adicionar(criar_carta(id_carta))
                    nomes = {
                        "forma_demoniaca": "FORMA DEMONÍACA",
                        "apoteose": "APOTEOSE",
                        "forma_deva": "FORMA DEVA",
                    }
                    self.escolha = nomes[id_carta]
                    break
        else:
            self.botao_continuar.update()
            if self.botao_continuar.is_clicked():
                fluxo.ir_para_mapa()

    def draw(self):
        Window.get_screen().blit(self.fundo, (0, 0))
        centralizado("CAMINHO ESPIRITUAL", 40, 5, fonte_pixel.DOURADO)
        centralizado("ESCOLHA UMA TRANSFORMAÇÃO PARA SER ADICIONADA AO BARALHO", 115, 3, fonte_pixel.CREME)

        tela = Window.get_screen()
        colunas = (
            (self.janela.width / 6, "SOMBRAS", fonte_pixel.VERMELHO,
             ("Forma Demoníaca", "+1 de força por turno")),
            (self.janela.width / 2, "DIVINO", fonte_pixel.DOURADO,
             ("Apoteose", "+3 de proteção por turno")),
            (self.janela.width * 5 / 6, "ALMA", fonte_pixel.VERDE,
             ("Forma Deva", "+1 de energia por turno")),
        )
        for x, titulo, cor, linhas in colunas:
            w = fonte_pixel.largura(titulo, 3)
            fonte_pixel.desenhar(tela, int(x - w / 2), 255, titulo, cor, esc=3)
            for i, linha in enumerate(linhas):
                w = fonte_pixel.largura(linha, 2)
                fonte_pixel.desenhar(tela, int(x - w / 2), 300 + i * 28, linha, fonte_pixel.CREME, esc=2)

        if self.escolha is None:
            for botao in self.botoes.values():
                botao.draw()
        else:
            centralizado(f"VOCÊ ESCOLHEU: {self.escolha}", 485, 3, fonte_pixel.VERDE)
            self.botao_continuar.draw()


class CenaFungoEnergetico(Scene):
    def __init__(self, jornada, no):
        super().__init__()
        self.jornada = jornada
        self.player = jornada.player
        self.fundo = fundo_borrado(150)
        centro = self.janela.width / 2
        self.escolha = None
        self.botao_aceitar = _botao("Deixar entrar", centro - 150, 430, largura=290)
        self.botao_matar = _botao("Matar o fungo", centro + 150, 430, largura=290)
        self.botao_continuar = _botao("Continuar", centro, 560)

    def loop(self):
        if self.escolha is None:
            self.botao_aceitar.update()
            self.botao_matar.update()
            if self.botao_aceitar.is_clicked():
                self.player.ap_max += 1
                self.player.ap = self.player.ap_max
                self.player.tamanho_mao = 4
                self.escolha = "aceitar"
            elif self.botao_matar.is_clicked():
                from fluxo import ir_para_recompensa_evento
                ir_para_recompensa_evento(self.player)
        else:
            self.botao_continuar.update()
            if self.botao_continuar.is_clicked():
                fluxo.ir_para_mapa()

    def draw(self):
        Window.get_screen().blit(self.fundo, (0, 0))
        centralizado("O FUNGO ENERGÉTICO", 40, 5, fonte_pixel.DOURADO)
        centralizado("UMA CRIATURA OFERECE ENERGIA", 115, 3, fonte_pixel.CREME)

        if self.escolha is None:
            centralizado("DEIXAR ENTRAR", 210, 3, fonte_pixel.VERDE)
            centralizado("+1 DE ENERGIA MÁXIMA", 245, 3, fonte_pixel.CREME)
            centralizado("COMEÇA O TURNO COM -1 CARTA NA MÃO", 280, 2, fonte_pixel.CREME)
            centralizado("OU MATAR: RECEBER UMA CARTA", 365, 3, fonte_pixel.VERMELHO)
            self.botao_aceitar.draw()
            self.botao_matar.draw()
        else:
            centralizado("O FUNGO SE UNIU A VOCÊ", 360, 3, fonte_pixel.VERDE)
            centralizado(f"ENERGIA MÁXIMA: {self.player.ap_max}", 420, 3, fonte_pixel.CREME)
            centralizado("TAMANHO DA MÃO: 4", 448, 2, fonte_pixel.CREME)
            self.botao_continuar.draw()


class CenaSemEventos(Scene):
    def __init__(self, jornada, no):
        super().__init__()
        self.fundo = fundo_borrado(150)
        centro = self.janela.width / 2
        self.botao_continuar = _botao("Continuar", centro, 560)

    def loop(self):
        self.botao_continuar.update()
        if self.botao_continuar.is_clicked():
            fluxo.ir_para_mapa()

    def draw(self):
        Window.get_screen().blit(self.fundo, (0, 0))
        centralizado("NENHUM EVENTO RESTANTE", 250, 4, fonte_pixel.DOURADO)
        centralizado("Esta sala não oferece nada.", 320, 2, fonte_pixel.CREME)
        self.botao_continuar.draw()


EVENTOS = {
    "pacto_morcego": CenaPactoMorcego,
    "caminho_espiritual": CenaCaminhoEspiritual,
    "fungo_energetico": CenaFungoEnergetico,
}

# Use None para desativar ou um ID de EVENTOS para testar esse evento no início.
EVENTO_TESTE_INICIAL = None


class GerenciadorEventos:
    def __init__(self, semente=None, evento_inicial=None):
        if evento_inicial is not None and evento_inicial not in EVENTOS:
            raise ValueError(f"evento inicial desconhecido: {evento_inicial}")
        self.rng = random.Random(semente)
        self.ocorridos = set()
        self.evento_inicial = evento_inicial

    def sortear(self):
        disponiveis = [id_evento for id_evento in EVENTOS if id_evento not in self.ocorridos]
        if not disponiveis:
            return None
        if self.evento_inicial is not None and not self.ocorridos:
            id_evento = self.evento_inicial
        else:
            id_evento = self.rng.choice(disponiveis)
        self.ocorridos.add(id_evento)
        return id_evento

    def criar_cena(self, jornada, no):
        id_evento = self.sortear()
        if id_evento is None:
            return CenaSemEventos(jornada, no)
        return EVENTOS[id_evento](jornada, no)
