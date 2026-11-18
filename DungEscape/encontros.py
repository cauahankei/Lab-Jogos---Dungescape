import random

# Pra criar outra categoria (elite, boss...) é só preencher a lista dela.
# obs: o max de inimigos em 1 combate é 3, não colocar mais que isso se não dá merda
ENCONTROS = {
    "normal": [
        ["slime"],
        ["goblin", "slime"],
        ["goblin", "goblin", "goblin"],
        ["esqueleton"],
        ["morcegosa", "morcegosa", "morcegosa"],
        ["morcegosa", "morcegosa"],

    ],

    "facil": [["slime"], ["goblin"], ["morcegosa"], ["slime", "slime"]],
    "medio": [["slime", "slime", "slime"], ["goblin", "slime"], ["morcegosa", "slime"], ["esqueleton", "slime"]],
    "dificil": [["goblin", "slime", "slime"], ["morcegosa", "slime", "slime"], ["esqueleton", "slime", "slime"]],
    "elite": [["goblin", "goblin", "goblin"], ["goblin", "goblin", "slime"]],
    "boss": [["wizard"]],
}

def sortear_encontro(categoria="normal"):
    lista = ENCONTROS.get(categoria)
    if not lista:
        raise ValueError(f"não há encontros na categoria '{categoria}'")
    return list(random.choice(lista))   # cópia, pra ninguém alterar o original