# ================================================================
# fonte_pixel.py
# escreve texto pixelado em cima de uma superficie do pygame
# (usado pra escrever nome, custo e descricao NAS CARTAS).
#
# nao precisa mexer aqui, so no cartas.py. mas se quiser trocar a cor
# das coisas, as cores ficam logo aqui embaixo.
#
# marcacao dentro do texto:
#   <6>   -> numero dourado (valor normal)
#   <v6>  -> numero verde   (valor MAIOR que o base, tipo buff de Forca)
#   <r6>  -> numero vermelho (valor MENOR que o base, tipo debuff)
#   [PALAVRA] -> palavra-chave ciano (Vulneravel, Forca...). sem espaco dentro!
# ================================================================

CREME = (242, 230, 201)
DOURADO = (241, 194, 126)
VERDE = (120, 220, 120)
VERMELHO = (235, 100, 95)
CIANO = (154, 209, 245)
BRANCO = (242, 242, 242)

# cada letra e uma grade 3x5 ("#" = pixel aceso, "|" = proxima linha)
_F = {
    'A': ".#.|#.#|###|#.#|#.#", 'B': "##.|#.#|##.|#.#|##.", 'C': ".##|#..|#..|#..|.##",
    'D': "##.|#.#|#.#|#.#|##.", 'E': "###|#..|##.|#..|###", 'F': "###|#..|##.|#..|#..",
    'G': ".##|#..|#.#|#.#|.##", 'H': "#.#|#.#|###|#.#|#.#", 'I': "###|.#.|.#.|.#.|###",
    'J': "..#|..#|..#|#.#|.#.", 'K': "#.#|#.#|##.|#.#|#.#", 'L': "#..|#..|#..|#..|###",
    'M': "#.#|###|###|#.#|#.#", 'N': "##.|#.#|#.#|#.#|#.#", 'O': ".#.|#.#|#.#|#.#|.#.",
    'P': "##.|#.#|##.|#..|#..", 'Q': ".#.|#.#|#.#|##.|.##", 'R': "##.|#.#|##.|#.#|#.#",
    'S': ".##|#..|.#.|..#|##.", 'T': "###|.#.|.#.|.#.|.#.", 'U': "#.#|#.#|#.#|#.#|###",
    'V': "#.#|#.#|#.#|#.#|.#.", 'W': "#.#|#.#|###|###|#.#", 'X': "#.#|#.#|.#.|#.#|#.#",
    'Y': "#.#|#.#|.#.|.#.|.#.", 'Z': "###|..#|.#.|#..|###",
    '0': "###|#.#|#.#|#.#|###", '1': ".#.|##.|.#.|.#.|###", '2': "##.|..#|.#.|#..|###",
    '3': "##.|..#|.#.|..#|##.", '4': "#.#|#.#|###|..#|..#", '5': "###|#..|##.|..#|##.",
    '6': ".##|#..|###|#.#|###", '7': "###|..#|.#.|.#.|.#.", '8': "###|#.#|###|#.#|###",
    '9': "###|#.#|###|..#|##.",
    '.': "...|...|...|...|.#.", ':': "...|.#.|...|.#.|...", '+': "...|.#.|###|.#.|...",
    '-': "...|...|###|...|...", ',': "...|...|...|.#.|#..", '!': ".#.|.#.|.#.|...|.#.",
    '/': "..#|..#|.#.|#..|#..", '%': "#.#|..#|.#.|#..|#.#",
}
# letra com acento = letra base + um pontinho (em cima) ou cedilha (embaixo)
_ACENTOS = {'Á': 'A', 'Ã': 'A', 'Â': 'A', 'À': 'A', 'É': 'E', 'Ê': 'E', 'Í': 'I',
            'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ú': 'U', 'Ç': 'C'}


def _glifo(ch):
    if ch in _F:
        return _F[ch].split('|'), None
    if ch in _ACENTOS:
        return _F[_ACENTOS[ch]].split('|'), ('baixo' if ch == 'Ç' else 'cima')
    return None, None


# ---------------- le a marcacao e vira uma lista de (letra, cor) ----------------
def _ler(texto, cor_base):
    seq = []
    i = 0
    while i < len(texto):
        ch = texto[i]
        if ch == '<':
            fim = texto.find('>', i)
            if fim != -1:
                miolo = texto[i + 1:fim]
                cor = DOURADO
                if miolo[:1] == 'v':
                    cor, miolo = VERDE, miolo[1:]
                elif miolo[:1] == 'r':
                    cor, miolo = VERMELHO, miolo[1:]
                seq.extend((c, cor) for c in miolo)
                i = fim + 1
                continue
        if ch == '[':
            fim = texto.find(']', i)
            if fim != -1:
                seq.extend((c, CIANO) for c in texto[i + 1:fim])
                i = fim + 1
                continue
        seq.append((ch, cor_base))
        i += 1
    return seq


def largura(texto, esc=1):
    # largura em pixels (ignora a marcacao)
    seq = _ler(texto, CREME)
    w = sum((3 if c == ' ' else 4) * esc for c, _ in seq)
    return max(0, w - esc)


def quebrar(texto, largura_max):
    # quebra o texto em linhas que cabem em largura_max pixels.
    # "\n" no texto forca uma quebra.
    linhas = []
    for paragrafo in texto.split('\n'):
        atual = ""
        for palavra in paragrafo.split(' '):
            teste = palavra if not atual else atual + ' ' + palavra
            if atual and largura(teste) > largura_max:
                linhas.append(atual)
                atual = palavra
            else:
                atual = teste
        linhas.append(atual)
    return linhas


def desenhar(superficie, x, y, texto, cor=CREME, esc=1, sombra=None):
    # escreve o texto com o canto de cima-esquerda em (x, y)
    seq = _ler(texto, cor)

    def passada(ox, oy, forcar_cor=None):
        cx = ox
        for ch, cc in seq:
            if ch == ' ':
                cx += 3 * esc
                continue
            g, acento = _glifo(ch.upper())
            if g is None:
                cx += 4 * esc
                continue
            c_final = forcar_cor or cc
            for r, linha in enumerate(g):
                for k, v in enumerate(linha):
                    if v == '#':
                        _quad(superficie, cx + k * esc, oy + r * esc, esc, c_final)
            if acento == 'cima':
                _quad(superficie, cx + esc, oy - esc, esc, c_final)
            elif acento == 'baixo':
                _quad(superficie, cx + esc, oy + 5 * esc, esc, c_final)
            cx += 4 * esc

    if sombra is not None:
        passada(x, y + esc, sombra)
    passada(x, y)


def _quad(sup, x, y, esc, cor):
    x, y = int(x), int(y)
    w, h = sup.get_width(), sup.get_height()
    for j in range(esc):
        for i in range(esc):
            xx, yy = x + i, y + j
            if 0 <= xx < w and 0 <= yy < h:
                sup.set_at((xx, yy), (cor[0], cor[1], cor[2], 255))
