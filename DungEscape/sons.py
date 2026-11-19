# sons.py
from PPlay.sound import Music, Sound, SoundManager
from utils import asset_path

VOLUME_COMPRA = 70
VOLUME_JOGAR_CARTA = 40
VOLUME_ATAQUE_INIMIGO = 20
VOLUME_MUSICA_COMBATE = 30
VOLUME_MUSICA_MENU = 30

_som_compra = None
_som_jogar_carta = None
_som_ataque_inimigo = None
_musica_combate = None
_musica_menu = None
_musica_atual = None
_volume_geral = 100
_volume_musica_base = VOLUME_MUSICA_MENU


def obter_volume_geral():
    return _volume_geral


def _volume_ajustado(volume_base):
    return volume_base * _volume_geral / 100


def _aplicar_volume_efeitos():
    for som, volume_base in (
        (_som_compra, VOLUME_COMPRA),
        (_som_jogar_carta, VOLUME_JOGAR_CARTA),
        (_som_ataque_inimigo, VOLUME_ATAQUE_INIMIGO),
    ):
        if som is not None:
            som.set_volume(_volume_ajustado(volume_base))


def definir_volume_geral(volume):
    global _volume_geral
    _volume_geral = max(0, min(100, int(volume)))
    _aplicar_volume_efeitos()
    if _musica_menu is not None or _musica_combate is not None:
        SoundManager.set_music_volume(_volume_ajustado(_volume_musica_base))

def audio_compra():
    global _som_compra
    if _som_compra is None:
        _som_compra = Sound(asset_path(
            "assets", "sons", "cartas", "card_draw_1.wav"
        ))
        _aplicar_volume_efeitos()
    _som_compra.play()

def audio_usar_carta():
    global _som_jogar_carta
    if _som_jogar_carta is None:
        _som_jogar_carta = Sound(asset_path(
            "assets", "sons", "cartas", "card_draw_3.wav"
        ))
        _aplicar_volume_efeitos()
    _som_jogar_carta.play()

def audio_ataque_inimigo():
    global _som_ataque_inimigo
    if _som_ataque_inimigo is None:
        _som_ataque_inimigo = Sound(asset_path(
            "assets", "sons", "combate", "punch_3.wav"
        ))
        _aplicar_volume_efeitos()
    _som_ataque_inimigo.play()

def iniciar_musica_combate():
    global _musica_combate, _musica_atual, _volume_musica_base
    if _musica_combate is None:
        _musica_combate = Music(asset_path(
            "assets", "sons", "combate", "Ruins.wav"
        ))
    _volume_musica_base = VOLUME_MUSICA_COMBATE
    SoundManager.set_music_volume(_volume_ajustado(_volume_musica_base))
    if _musica_atual != "combate" or not _musica_combate.is_playing():
        _musica_combate.play(loops=-1)
        _musica_atual = "combate"

def parar_musica_combate():
    global _musica_atual
    if _musica_combate is not None:
        _musica_combate.stop()
        if _musica_atual == "combate":
            _musica_atual = None

def iniciar_musica_menu():
    global _musica_menu, _musica_atual, _volume_musica_base
    if _musica_menu is None:
        _musica_menu = Music(asset_path(
            "assets", "sons", "menu", "Innocent.wav"
        ))
    _volume_musica_base = VOLUME_MUSICA_MENU
    SoundManager.set_music_volume(_volume_ajustado(_volume_musica_base))
    if _musica_atual != "menu" or not _musica_menu.is_playing():
        _musica_menu.play(loops=-1)
        _musica_atual = "menu"

def parar_musica_menu():
    global _musica_atual
    if _musica_menu is not None:
        _musica_menu.stop()
        if _musica_atual == "menu":
            _musica_atual = None