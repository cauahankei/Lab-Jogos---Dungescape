# Dungescape — Roguelike Deckbuilder

Trabalho desenvolvido para a disciplina de **Laboratório de Desenvolvimento de Jogos**, utilizando o framework **PowerPPlay 2.0 (PPlay)**.

## Sobre o projeto

**Dungescape** é um roguelike de construção de baralhos (*deckbuilder*) por turnos com geração procedural de rotas e morte permanente (*permadeath*), inspirado em *Slay the Spire*.

Na história, o jogador assume o papel de um **Aprendiz** de cavaleiro capturado nas profundezas de uma masmorra secreta por um **Mago Sombrio**, que pretende submetê-lo a experimentos proibidos para forjar um Cavaleiro das Trevas. Escapando de sua cela antes que o ritual se conclua, o Aprendiz precisa escalar **18 andares** de perigos, gerenciar sua energia e baralho em combates táticos, sobreviver a eventos narrativos e derrotar o Mago Sombrio no topo da fortaleza.

O projeto foi desenvolvido utilizando **exclusivamente o framework PowerPPlay 2.0 (PPlay)** e **Pygame-CE**, sem bibliotecas externas adicionais.

## Autores

- João Lucas Mesquita
- Cauã da Silva Nascimento

## Informações Institucionais

- **Disciplina:** Laboratório de Desenvolvimento de Jogos
- **Instituição:** UFF — Universidade Federal Fluminense
- **Professor:** Esteban Clua

## Tecnologias utilizadas

- **Python 3.8+** (recomendado 3.10+)
- **PowerPPlay 2.0 (PPlay)** — framework de desenvolvimento de jogos 2D construído sobre Pygame-CE, desenvolvido no Instituto de Computação da UFF
- **Pygame-CE** — dependência interna do PPlay

## Funcionalidades Implementadas

- [x] **Mapa Procedural em Pergaminho:** 18 andares interligados por rotas geradas proceduralmente com garantia de equilíbrio de desgaste entre salas de **Combate**, **Eventos** e **Fogueiras**.
- [x] **Sistema de Combate por Turnos:** Gerenciamento de Energia (AP), Escudo temporário, seleção de alvos, estados de combate (*Força*, *Vulnerável*, *Fraqueza* e *Retaliação*) e intenções visíveis dos inimigos.
- [x] **Construção de Baralho (16 Cartas):** Deck inicial enxuto com cartas de ataque, defesa, habilidades táticas, compra de cartas e poderes únicos de batalha adquiridos em eventos.
- [x] **Bestiário Completo e Chefe Final:** 4 inimigos comuns/avançados (*Slime*, *Goblin*, *Morcegosa* e *Esqueleto*) e o chefe final (*Mago Sombrio*) com roteiro de ações próprio.
- [x] **Eventos Narrativos e Fogueiras:** Encontros únicos (*Pacto de Morcego*, *Caminho Espiritual* e *O Fungo Energético*) e fogueiras para restauração de vida.
- [x] **Sistema de Recompensas:** Escolha opcional de 1 entre 2 cartas ao vencer combates, permitindo manter o baralho enxuto.
- [x] **Atmosfera Visual e Sonora:** Cenário 3D com filtro de pixelização (4x), iluminação dinâmica pulsante simulando tochas, fonte bitmap customizada e efeitos sonoros integrados.

## Estrutura do projeto

```text
dungescape/
├── PPlay/                  # Framework PowerPPlay 2.0
├── assets/                 # Sprites, cartas, cenários, fontes, sons e músicas
├── ator.py                 # Controle de spritesheets, animações e estados visuais
├── cartas.py               # Catálogo das 16 cartas, efeitos e mecânica de baralho
├── combatente.py           # Regras de dano, escudo, status, Player, Inimigos e Mago Sombrio
├── efeitos_visuais.py      # Filtro de pixelização (4x) do cenário e sistema de iluminação dinâmica
├── encontros.py            # Pools de encontros por dificuldade (fácil, médio, difícil e boss)
├── eventos.py              # Cenas interativas dos eventos narrativos da masmorra
├── fluxo.py                # Gerenciamento de jornada e transições entre cenas
├── fonte_pixel.py          # Renderização de fonte pixelada customizada com cores dinâmicas
├── gerenciador_combate.py  # Máquina de estados do turno e resolução das ações
├── hud.py                  # Interface de combate, barras de vida, intenções e pilhas de cartas
├── mapa.py                 # Geração procedural do pergaminho de 18 andares
├── menu.py                 # Tela inicial e navegação principal
├── salas.py                # Controlador das salas de fogueira, vitória e fim de jogo
└── main.py                 # Ponto de entrada da aplicação
```

## Como executar

1. Certifique-se de ter o **Python 3.10+** e o **Pygame-CE** instalados no ambiente:
   ```bash
   pip install pygame-ce
   ```
2. Na raiz do projeto, execute o arquivo principal:
   ```bash
   python main.py
   ```

## Créditos e Agradecimentos (Assets Gratuitos)

Todos os recursos gráficos e sonoros utilizados neste projeto são de **uso livre**, disponibilizados por criadores independentes no **itch.io**:

- **Personagens e Inimigos (Aprendiz, Monstros e Mago Sombrio):** [LuizMelo](https://luizmelo.itch.io) (`@LuizGdeMelo`)
  - [Monsters Creatures Fantasy](https://luizmelo.itch.io/monsters-creatures-fantasy)
  - [Monsters Creatures Fantasy 2](https://luizmelo.itch.io/monsters-creatures-fantasy-2)
  - [Medieval Warrior Pack 2](https://luizmelo.itch.io/medieval-warrior-pack-2)
  - [Evil Wizard 2](https://luizmelo.itch.io/evil-wizard-2)
- **Cenário 3D da Masmorra:** [Forsunka](https://forsunka.itch.io) — [Dungeon Tiles](https://forsunka.itch.io/dungeon-tiles)
- **Templates de Cartas e Ícones de HUD:** [guawoo](https://guawoo.itch.io) — [Card Game Layout Template](https://guawoo.itch.io/card-game-layout-template)
- **Efeitos Sonoros (SFX):** [Chequered Ink (ci)](https://ci.itch.io) — [400+ Sounds Pack](https://ci.itch.io/400-sounds-pack)
- **Trilha Sonora:** [Juzek](https://juzek.itch.io) (`@sweetpowersauce`) — [Game Boy Music Loop Pack](https://juzek.itch.io/game-boy-music-loop-pack)

## Referências

- Documentação oficial (elaborada por Kauã Neves) do framework **PowerPPlay 2.0**, Instituto de Computação — UFF.
- *Slay the Spire* (MegaCrit, 2019) — referência principal de design de jogo.

## Licença

Projeto acadêmico desenvolvido para fins educacionais.