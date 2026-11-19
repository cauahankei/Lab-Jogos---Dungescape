import random

# Pra criar outra categoria (elite, boss...) é só preencher a lista dela.
# obs: o max de inimigos em 1 combate é 3, não colocar mais que isso se não dá merda
ENCONTROS = {
    "facil": [
        ["slime"],
        ["goblin"],
        ["morcegosa"],
        ["goblin", "slime"],
    ],
    "medio": [
        ["esqueleton"],
        ["goblin", "goblin"],
        ["morcegosa", "goblin"],
        ["goblin", "slime", "slime"],
    ],
    "dificil": [
        ["esqueleton", "goblin"],
        ["esqueleton", "morcegosa"],
        ["esqueleton", "slime", "slime"],
        ["goblin", "goblin", "morcegosa"],
    ],
    "normal": [
        ["esqueleton"],
        ["goblin", "goblin"],
        ["morcegosa", "goblin"],
    ],
    "elite": [
        ["esqueleton", "goblin"],
        ["esqueleton", "morcegosa"],
    ],
    "boss": [
        ["wizard"],
    ],
}

# Temporário: defina como None para voltar a sortear pelas pools abaixo.
INIMIGO_FORCADO_PARA_TESTE = None

def sortear_encontro(categoria="normal"):
    if INIMIGO_FORCADO_PARA_TESTE is not None:
        return [INIMIGO_FORCADO_PARA_TESTE]

    lista = ENCONTROS.get(categoria)
    if not lista:
        raise ValueError(f"não há encontros na categoria '{categoria}'")
    return list(random.choice(lista))   # cópia, pra ninguém alterar o original