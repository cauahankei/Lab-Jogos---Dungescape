# sons.py
from PPlay.sound import Music, Sound, SoundManager
from utils import asset_path

VOLUME_COMPRA = 25
VOLUME_JOGAR_CARTA = 15
VOLUME_ATAQUE_INIMIGO = 5
VOLUME_MUSICA_COMBATE = 5
VOLUME_MUSICA_MENU = 5

_som_compra = None
_som_jogar_carta = None
_som_ataque_inimigo = None
_musica_combate = None
_musica_menu = None

def audio_compra():
    global _som_compra
    if _som_compra is None:
        _som_compra = Sound(asset_path(
            "assets", "sons", "cartas", "card_draw_1.wav"
        ))
        _som_compra.set_volume(VOLUME_COMPRA)
    _som_compra.play()

def audio_usar_carta():
    global _som_jogar_carta
    if _som_jogar_carta is None:
        _som_jogar_carta = Sound(asset_path(
            "assets", "sons", "cartas", "card_draw_3.wav"
        ))
        _som_jogar_carta.set_volume(VOLUME_JOGAR_CARTA)
    _som_jogar_carta.play()

def audio_ataque_inimigo():
    global _som_ataque_inimigo
    if _som_ataque_inimigo is None:
        _som_ataque_inimigo = Sound(asset_path(
            "assets", "sons", "combate", "punch_3.wav"
        ))
        _som_ataque_inimigo.set_volume(VOLUME_ATAQUE_INIMIGO)
    _som_ataque_inimigo.play()

def iniciar_musica_combate():
    global _musica_combate
    if _musica_combate is None:
        _musica_combate = Music(asset_path(
            "assets", "sons", "combate", "Ruins.wav"
        ))
    SoundManager.set_music_volume(VOLUME_MUSICA_COMBATE)
    _musica_combate.play(loops=-1)

def parar_musica_combate():
    if _musica_combate is not None:
        _musica_combate.stop()

def iniciar_musica_menu():
    global _musica_menu
    if _musica_menu is None:
        _musica_menu = Music(asset_path(
            "assets", "sons", "menu", "Innocent.wav"
        ))
    SoundManager.set_music_volume(VOLUME_MUSICA_MENU)
    _musica_menu.play(loops=-1)

def parar_musica_menu():
    if _musica_menu is not None:
        _musica_menu.stop()