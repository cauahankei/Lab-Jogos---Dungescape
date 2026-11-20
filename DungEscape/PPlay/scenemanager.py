import pygame

"""
===============================================================================
POWER PPLAY 2.0 - Framework de Alta Performance para Desenvolvimento de Jogos
===============================================================================
Desenvolvedor Líder e Arquiteto da Versão 2.0: 
    Kauã Neves Jesus de Paula

Ano de Lançamento: 2026
Instituição: Universidade Federal Fluminense (IC-UFF) - Niterói, RJ
-------------------------------------------------------------------------------
Este software é uma evolução profunda e modernização da biblioteca PPlay,
originalmente concebida pela Equipe PPlay:
    Prof. Esteban Clua, Prof. Anselmo Montenegro, Gabriel Saldanha,
    Adônis Gasiglia, Yuri Nogueira e Sergio Herman.
===============================================================================
"""

class Scene:
    """
    Classe base para todas as cenas do jogo.
    O aluno deve herdar desta classe para criar seus menus e fases.
    """
    def __init__(self):
        # Referência rápida para a janela e inputs
        from .window import Window
        self.janela = Window.get_instance()
        self.teclado = self.janela.keyboard
        self.mouse = self.janela.mouse

    def loop(self):
        """Onde o aluno coloca a lógica de movimento e física."""
        pass

    def draw(self):
        """Onde o aluno coloca os comandos de desenho."""
        pass

class SceneManager:
    """
    Controlador central que decide qual cena está ativa no momento.
    """
    _current_scene = None
    _confirmando_menu = False
    _botao_sim = None
    _botao_nao = None

    @classmethod
    def change_scene(cls, next_scene):
        """
        Troca a cena atual. 
        next_scene deve ser uma instância de uma classe que herda de Scene.
        """
        cls._current_scene = next_scene
        cls._confirmando_menu = False
        cls._botao_sim = None
        cls._botao_nao = None

    @classmethod
    def run(cls):
        """
        Executa o ciclo de vida da cena atual.
        Deve ser chamado dentro do loop principal do jogo.
        """
        if cls._current_scene:
            cena = cls._current_scene
            teclado = cena.teclado

            if cls._confirmando_menu:
                cls._botao_sim.update()
                cls._botao_nao.update()
                if cls._botao_sim.is_clicked() or teclado.key_down("ENTER"):
                    cls._confirmando_menu = False
                    cls._botao_sim = None
                    cls._botao_nao = None
                    from fluxo import ir_para_menu
                    ir_para_menu()
                elif cls._botao_nao.is_clicked() or teclado.key_down("ESC"):
                    cls._confirmando_menu = False
                    cls._botao_sim = None
                    cls._botao_nao = None

                cls._current_scene.draw()
                if cls._confirmando_menu:
                    cls._desenhar_confirmacao_menu()
                return

            if (
                not getattr(cena, "ignorar_esc_menu", False)
                and teclado.key_down("ESC")
            ):
                cls._confirmando_menu = True
                cls._criar_botoes_confirmacao_menu()
                cena.draw()
                cls._desenhar_confirmacao_menu()
                return

            # 1. Executa a lógica da cena
            cena.loop()
            
            # 2. Executa os desenhos da cena
            cena.draw()
        else:
            from .window import Window
            Window.get_screen().fill((255, 0, 0)) # Alerta visual: Nenhuma cena ativa

    @classmethod
    def _desenhar_confirmacao_menu(cls):
        from .window import Window

        tela = Window.get_screen()
        largura, altura = tela.get_size()
        sobreposicao = pygame.Surface((largura, altura), pygame.SRCALPHA)
        sobreposicao.fill((0, 0, 0, 170))
        tela.blit(sobreposicao, (0, 0))

        caixa = pygame.Rect(0, 0, 620, 180)
        caixa.center = (largura // 2, altura // 2)
        pygame.draw.rect(tela, (30, 27, 35), caixa, border_radius=8)
        pygame.draw.rect(tela, (218, 172, 76), caixa, 3, border_radius=8)

        fonte_titulo = pygame.font.SysFont("Arial", 30, bold=True)
        titulo = fonte_titulo.render(
            "Deseja voltar para o menu?", True, (255, 239, 201)
        )
        tela.blit(titulo, titulo.get_rect(center=(largura // 2, altura // 2 - 22)))
        cls._botao_sim.draw()
        cls._botao_nao.draw()

    @classmethod
    def _criar_botoes_confirmacao_menu(cls):
        from .uikit import Button
        from .window import Window

        janela = Window.get_instance()
        x = (janela.largura - 324) / 2
        y = janela.altura / 2 + 24
        cls._botao_sim = Button(
            150, 48, "SIM", (72, 82, 52), (104, 120, 70)
        )
        cls._botao_sim.set_position(x, y)
        cls._botao_nao = Button(
            150, 48, "NÃO", (75, 58, 52), (115, 78, 64)
        )
        cls._botao_nao.set_position(x + 174, y)