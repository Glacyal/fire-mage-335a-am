"""
Helper & Factory per SubRegions WeakAuras (Testi, Glow, Bordi)
=============================================================
Fornisce funzioni di utilità per costruire sub-regioni conformi alle specifiche
di WeakAuras 4.0.0 per WotLK 3.3.5a.
"""

def make_subtext(
    text: str,
    justify: str = "CENTER",
    anchor_point: str = "INNER_BOTTOM",
    font_size: int = 12,
    y_offset: int = 0,
    x_offset: int = 0,
    extra_props: dict = None
) -> dict:
    """
    Genera la struttura dizionario per una subRegion di tipo subtext con font Expressway OUTLINE.
    
    :param text: Testo o macro (%p, %s, %c) visualizzato.
    :param justify: Allineamento orizzontale ('CENTER', 'LEFT', 'RIGHT').
    :param anchor_point: Punto di ancoraggio relativo alla regione padre.
    :param font_size: Dimensione del font in punti.
    :param y_offset: Spostamento verticale in pixel.
    :param x_offset: Spostamento orizzontale in pixel.
    :param extra_props: Proprietà addizionali opzionali da fondere nel dizionario.
    :return: Dizionario formattato per la subRegion di WeakAuras.
    """
    res = {
        "type": "subtext",
        "text_text": text,
        "text_justify": justify,
        "anchor_point": anchor_point,
        "anchorPoint": anchor_point,
        "text_anchorPoint": anchor_point,
        "text_fontSize": font_size,
        "text_font": "Expressway",
        "text_fontType": "OUTLINE",
        "text_selfPoint": "AUTO",
        "text_shadowXOffset": 0,
        "text_shadowYOffset": 0,
        "text_shadowColor": [0, 0, 0, 1],
        "text_color": [1, 1, 1, 1],
        "text_text_format_p_format": "timed",
        "text_text_format_p_time_precision": 1,
        "text_text_format_p_time_dynamic_threshold": 60,
        "text_visible": True,
        "anchorXOffset": x_offset,
        "anchorYOffset": y_offset,
        "text_anchorXOffset": x_offset,
        "text_anchorYOffset": y_offset,
        "text_xOffset": x_offset,
        "text_yOffset": y_offset,
    }
    if extra_props:
        res.update(extra_props)
    return res
