# DungEscape — Roguelike de Cartas

Trabalho desenvolvido para a disciplina de **Laboratório de Desenvolvimento de Jogos**, utilizando o framework **PowerPPlay 2.0 (PPlay)**.

## Sobre o projeto

Jogo roguelike de cartas fortemente inspirado em *Slay the Spire*, onde o jogador enfrenta combates por turnos utilizando um deck de cartas, avançando por um mapa de encontros com progressão permadeath.

O projeto foi desenvolvido utilizando **exclusivamente o framework PPlay** como ferramenta de desenvolvimento, sem bibliotecas externas além das já utilizadas internamente pelo próprio framework (Pygame-CE).

## Autores

- João Lucas Mesquita

- Cauã Nascimento

## Informações Institucionais

- **Disciplina:** Laboratório de Desenvolvimento de Jogos
- **Instituição:** UFF - Universidade Federal Fluminense
- **Professor(a):** Esteban Clua

## Tecnologias utilizadas

- **Python 3.8+** (recomendado 3.10+)
- **[PowerPPlay 2.0 (PPlay)](https://github.com/)** — framework de desenvolvimento de jogos 2D construído sobre Pygame-CE, desenvolvido no Instituto de Computação da UFF
- **Pygame-CE** — dependência interna do PPlay

## Funcionalidades

> Marque conforme for implementando ao longo do desenvolvimento.

- [x] Tela de composição de combate (fundo, personagem, inimigo, mão de cartas)
- [ ] Sistema de combate por turnos (vida, bloqueio, dano)
- [ ] Sistema de cartas (ataque, defesa, habilidades)
- [ ] Interação de jogar cartas (clique/arraste)
- [ ] Intenção de ataque dos inimigos
- [ ] Mapa de progressão roguelike (nós de eventos/combate/loja)
- [ ] Sistema de recompensas entre combates
- [ ] Feedback visual (shake, flash, partículas)
- [ ] Múltiplos inimigos/biomas
- [ ] Sistema de save/progressão entre execuções

## Estrutura do projeto

```
meu_jogo/
├── PPlay/              # Framework PowerPPlay 2.0
├── core/               # Lógica de jogo pura (combate, cartas, regras) — sem dependência de PPlay
├── ui/                 # Camada visual — cenas, sprites, integração com PPlay
├── data/               # Definição de conteúdo do jogo (cartas, inimigos)
├── assets/             # Imagens, sons e demais recursos visuais
└── main.py             # Ponto de entrada do jogo
```

## Referências

- Documentação oficial (Elaborada por Kauã Neves) do framework **PowerPPlay 2.0**, Instituto de Computação — UFF.
- *Slay the Spire* (MegaCrit, 2019) — referência de design de jogo.

## Licença

Projeto acadêmico desenvolvido para fins educacionais.
