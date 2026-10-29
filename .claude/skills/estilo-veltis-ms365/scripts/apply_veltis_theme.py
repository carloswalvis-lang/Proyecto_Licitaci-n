#!/usr/bin/env python3
"""Aplica el estilo corporativo Veltis a archivos MS365 (Word, PowerPoint, Excel).

- Carga la paleta y Overpass en el TEMA del archivo.
- Pinta cada elemento con REFERENCIAS al tema (Enfasis 1, Enfasis 2 ... y sus tonalidades
  "Mas claro 80%/60%/40%" y "Mas oscuro 25%/50%"), nunca con hex fijos: si el tema cambia,
  el documento cambia con el.
- Ajusta tamanos de texto por elemento (titulos, cuerpo, citas, tablas, vinetas).

Uso: python apply_veltis_theme.py archivo(.docx/.pptx/.xlsx/.html) [...] [-o salida] [--inplace]
     [--colors-only | --fonts-only] [--theme-only] [--no-sizes] [--keep-direct]
"""
import argparse, colorsys, re, shutil, sys, zipfile
from pathlib import Path
from lxml import etree

FONT = "Overpass"

# ---------------------------------------------------------------- paleta del tema
# Unico lugar con hex: los valores que se cargan en el tema del archivo.
TEMA = {
    "dk1": "000000",      # Texto/fondo - Oscuro 1
    "lt1": "FFFFFF",      # Texto/fondo - Claro 1
    "dk2": "3F3F3F",      # Texto/fondo - Oscuro 2
    "lt2": "D8D8D8",      # Texto/fondo - Claro 2
    "accent1": "FC5E24",  # Enfasis 1
    "accent2": "F0AE94",  # Enfasis 2
    "accent3": "D7D7D7",  # Enfasis 3
    "accent4": "D7D7D7",  # Enfasis 4
    "accent5": "A02B93",  # Enfasis 5
    "accent6": "4EA72E",  # Enfasis 6
    "hlink": "467886",    # Hipervinculo
    "folHlink": "96607D", # Hipervinculo visitado
}

# ---------------------------------------------------------------- variables de color (referencias)
BASES = {"OSCURO_1": "dk1", "CLARO_1": "lt1", "OSCURO_2": "dk2", "CLARO_2": "lt2",
         "ENFASIS_1": "accent1", "ENFASIS_2": "accent2", "ENFASIS_3": "accent3",
         "ENFASIS_4": "accent4", "ENFASIS_5": "accent5", "ENFASIS_6": "accent6",
         "HIPERVINCULO": "hlink", "HIPERVINCULO_VISITADO": "folHlink"}
TONOS = {"": None, "_CLARO_80": ("claro", 80), "_CLARO_60": ("claro", 60), "_CLARO_40": ("claro", 40),
         "_OSCURO_25": ("oscuro", 25), "_OSCURO_50": ("oscuro", 50)}


class Ref:
    """Referencia a un color del tema + tonalidad, como en el selector de Office."""
    def __init__(self, slot, tono=None):
        self.slot, self.tono = slot, tono

    @property
    def fallback_hex(self):  # cache que Word exige en w:val; Office lo recalcula desde el tema
        h = TEMA[self.slot]
        if not self.tono:
            return h
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        hh, l, s = colorsys.rgb_to_hls(r, g, b)
        p = self.tono[1] / 100
        l = l * (1 - p) + p if self.tono[0] == "claro" else l * (1 - p)
        return "".join(f"{round(c * 255):02X}" for c in colorsys.hls_to_rgb(hh, l, s))


# PALETA["ENFASIS_1"], PALETA["ENFASIS_2_CLARO_80"], PALETA["ENFASIS_1_OSCURO_25"], ...
PALETA = {n + suf: Ref(slot, tono) for n, slot in BASES.items() for suf, tono in TONOS.items()}
globals().update(PALETA)  # tambien disponibles como variables: ENFASIS_1, ENFASIS_2_CLARO_60, ...

# ---------------------------------------------------------------- roles por elemento (color + tamano)
# Edita aqui para cambiar la identidad. Colores = nombres de PALETA; tamanos en pt.
WORD_ROLES = {
    #                color                    pt    negrita cursiva  borde (color, lado)
    "title":         ("ENFASIS_1",            26,   True,   False,   ("ENFASIS_1", "bottom")),
    "subtitle":      ("ENFASIS_2_OSCURO_50",  14,   False,  True,    None),
    "heading 1":     ("ENFASIS_1",            18,   True,   False,   None),
    "heading 2":     ("ENFASIS_2_OSCURO_50",  14,   True,   False,   ("ENFASIS_2", "bottom")),
    "heading 3":     ("ENFASIS_1_OSCURO_25",  12,   True,   False,   None),
    "normal":        (None,                   11,   False,  False,   None),
    "quote":         ("OSCURO_2",             11,   False,  True,    ("ENFASIS_2", "left")),
    "intense quote": ("ENFASIS_1_OSCURO_25",  12,   True,   True,    ("ENFASIS_1", "left")),
    "caption":       ("ENFASIS_2_OSCURO_50",   9,   False,  True,    None),
}
WORD_TABLA = {
    "encabezado_fondo": "ENFASIS_1", "encabezado_texto": "CLARO_1", "encabezado_pt": 10,
    "banda_fondo": "ENFASIS_2_CLARO_80", "cuerpo_pt": 10,
}
PPT_ROLES = {
    "titulo": ("ENFASIS_1", 36, True),
    "cuerpo_pt": {1: 20, 2: 18, 3: 16, 4: 14, 5: 14, 6: 14, 7: 14, 8: 14, 9: 14},
    "vineta_nivel1": "ENFASIS_1",
    "vineta_otros": "ENFASIS_2_OSCURO_25",
}
EXCEL = {
    "cuerpo_pt": 10,
    "estilo_tabla": "TableStyleMedium2",   # tablas formales: encabezado Enfasis 1 + bandas (por tema)
    # Rangos normales (sin tabla formal): se detectan fila de titulo y fila de encabezado
    "titulo": {"color": "ENFASIS_1", "pt": 14, "negrita": True, "fondo": None},
    "encabezado": {"color": "CLARO_1", "pt": 10, "negrita": True, "fondo": "ENFASIS_1"},
    "banda_fondo": "ENFASIS_2_CLARO_80",   # filas alternas del rango; None para no pintar bandas
}

# Colores duros de las paletas por defecto de Office -> variable Veltis equivalente
DEFAULT_MAP = {
    "4472C4": "ENFASIS_1", "ED7D31": "ENFASIS_2", "A5A5A5": "ENFASIS_3", "FFC000": "ENFASIS_4",
    "5B9BD5": "ENFASIS_5", "70AD47": "ENFASIS_6", "44546A": "OSCURO_2", "E7E6E6": "CLARO_2",
    "0563C1": "HIPERVINCULO", "954F72": "HIPERVINCULO_VISITADO", "2F5496": "ENFASIS_1_OSCURO_25",
    "1F3763": "ENFASIS_1_OSCURO_50", "8EAADB": "ENFASIS_1_CLARO_40", "B4C6E7": "ENFASIS_1_CLARO_60",
    "D9E2F3": "ENFASIS_1_CLARO_80", "F4B083": "ENFASIS_2_CLARO_40", "F7CAAC": "ENFASIS_2_CLARO_60",
    "FBE4D5": "ENFASIS_2_CLARO_80", "C45911": "ENFASIS_2_OSCURO_25",
    "156082": "ENFASIS_1", "E97132": "ENFASIS_2", "196B24": "ENFASIS_3", "0F9ED5": "ENFASIS_4",
    "0E2841": "OSCURO_2", "E8E8E8": "CLARO_2", "0F4761": "ENFASIS_1_OSCURO_25",
    "4F81BD": "ENFASIS_1", "C0504D": "ENFASIS_2", "9BBB59": "ENFASIS_3", "8064A2": "ENFASIS_4",
    "4BACC6": "ENFASIS_5", "F79646": "ENFASIS_6", "1F497D": "OSCURO_2", "EEECE1": "CLARO_2",
    "0000FF": "HIPERVINCULO", "800080": "HIPERVINCULO_VISITADO", "365F91": "ENFASIS_1_OSCURO_25",
    "243F60": "ENFASIS_1_OSCURO_50",
}

# ---------------------------------------------------------------- nombres por formato
WORD_SLOT = {"dk1": "text1", "lt1": "background1", "dk2": "text2", "lt2": "background2",
             "hlink": "hyperlink", "folHlink": "followedHyperlink"}
WORD_SLOT_INV = {"text1": "dk1", "background1": "lt1", "text2": "dk2", "background2": "lt2",
                 "dark1": "dk1", "light1": "lt1", "dark2": "dk2", "light2": "lt2",
                 "hyperlink": "hlink", "followedHyperlink": "folHlink"}
PPT_SLOT = {"dk1": "tx1", "lt1": "bg1", "dk2": "tx2", "lt2": "bg2"}
XL_INDEX = {"lt1": 0, "dk1": 1, "lt2": 2, "dk2": 3, "accent1": 4, "accent2": 5, "accent3": 6,
            "accent4": 7, "accent5": 8, "accent6": 9, "hlink": 10, "folHlink": 11}

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"a": A, "w": W, "s": S, "p": P}
wq = lambda t: f"{{{W}}}{t}"
aq = lambda t: f"{{{A}}}{t}"

RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike",
             "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden",
             "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect",
             "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout",
             "specVanish", "oMath"]
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
             "sectPr", "pPrChange"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
              "textDirection", "tcFitText", "vAlign", "hideMark", "headers", "cellIns", "cellDel",
              "cellMerge", "tcPrChange"]
STYLE_ORDER = ["name", "aliases", "basedOn", "next", "link", "autoRedefine", "hidden", "uiPriority",
               "semiHidden", "unhideWhenUsed", "qFormat", "locked", "personal", "personalCompose",
               "personalReply", "rsid", "pPr", "rPr", "tblPr", "trPr", "tcPr", "tblStylePr"]
LVL_ORDER = ["lnSpc", "spcBef", "spcAft", "buClrTx", "buClr", "buSzTx", "buSzPct", "buSzPts", "buFontTx",
             "buFont", "buNone", "buAutoNum", "buChar", "buBlip", "tabLst", "defRPr", "extLst"]
FILLS = ("noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill")
STYLE_ALIASES = {"titulo": "title", "título": "title", "ttulo": "title", "subttulo": "subtitle",
                 "subtítulo": "subtitle", "cita": "quote", "citadestacada": "intense quote",
                 "intensequote": "intense quote", "descripcin": "caption", "descripción": "caption"}


# ---------------------------------------------------------------- utilidades XML
def insert_ordered(parent, tag_q, order, ns_uri):
    for child in parent:
        if child.tag == tag_q:
            return child
    el = etree.Element(tag_q)
    idx = order.index(tag_q.split("}")[-1])
    for i, child in enumerate(parent):
        if not isinstance(child.tag, str):
            continue
        q = etree.QName(child)
        if q.namespace == ns_uri and q.localname in order and order.index(q.localname) > idx:
            parent.insert(i, el)
            return el
    parent.append(el)
    return el


def rpr_get(rpr, tag):
    return insert_ordered(rpr, wq(tag), RPR_ORDER, W)


def clear_attrs(el):
    for k in list(el.attrib):
        del el.attrib[k]


# ---------------------------------------------------------------- escritura de referencias por formato
def _word_tone_attrs(ref, prefix):
    """prefix '' -> themeTint/themeShade ; 'Fill' -> themeFillTint/themeFillShade"""
    if not ref.tono:
        return {}
    v = f"{round(255 * (1 - ref.tono[1] / 100)):02X}"
    kind = "Tint" if ref.tono[0] == "claro" else "Shade"
    return {f"theme{prefix}{kind}": v}


def word_set_color(el, ref, attr_val="val", attr_theme="themeColor"):
    """w:color o borde: valor de cache + referencia al tema con tonalidad."""
    for k in (attr_theme, "themeTint", "themeShade"):
        el.attrib.pop(wq(k), None)
    el.set(wq(attr_val), ref.fallback_hex)
    el.set(wq(attr_theme), WORD_SLOT.get(ref.slot, ref.slot))
    for k, v in _word_tone_attrs(ref, "").items():
        el.set(wq(k), v)


def word_set_fill(shd, ref):
    clear_attrs(shd)
    shd.set(wq("val"), "clear"); shd.set(wq("color"), "auto")
    shd.set(wq("fill"), ref.fallback_hex)
    shd.set(wq("themeFill"), WORD_SLOT.get(ref.slot, ref.slot))
    for k, v in _word_tone_attrs(ref, "Fill").items():
        shd.set(wq(k), v)


def dml_scheme(ref):
    """<a:schemeClr val="accent1"><a:lumMod/><a:lumOff/></a:schemeClr> (asi lo escribe Office)."""
    sc = etree.Element(aq("schemeClr"))
    sc.set("val", PPT_SLOT.get(ref.slot, ref.slot))
    if ref.tono:
        p = ref.tono[1] * 1000
        etree.SubElement(sc, aq("lumMod")).set("val", str(100000 - p))
        if ref.tono[0] == "claro":
            etree.SubElement(sc, aq("lumOff")).set("val", str(p))
    return sc


def dml_solid_fill(parent, ref):
    for f in FILLS:
        for old in parent.findall(f"a:{f}", NS):
            parent.remove(old)
    sf = etree.Element(aq("solidFill"))
    sf.append(dml_scheme(ref))
    ln = parent.find("a:ln", NS)
    parent.insert(list(parent).index(ln) + 1 if ln is not None else 0, sf)


def xl_set_color(el, ref):
    clear_attrs(el)
    el.set("theme", str(XL_INDEX[ref.slot]))
    if ref.tono:
        t = ref.tono[1] / 100
        el.set("tint", repr(t if ref.tono[0] == "claro" else -t))


# ---------------------------------------------------------------- tema
def theme_xml(root, do_colors, do_fonts):
    if do_colors:
        cs = root.find(".//a:clrScheme", NS)
        if cs is not None:
            cs.set("name", "Veltis")
            for key, hexv in TEMA.items():
                el = cs.find(f"a:{key}", NS)
                if el is None:
                    el = etree.SubElement(cs, aq(key))
                for c in list(el):
                    el.remove(c)
                etree.SubElement(el, aq("srgbClr")).set("val", hexv)
    if do_fonts:
        fs = root.find(".//a:fontScheme", NS)
        if fs is not None:
            fs.set("name", "Veltis Overpass")
            for part in ("a:majorFont", "a:minorFont"):
                latin = fs.find(f"{part}/a:latin", NS)
                if latin is not None:
                    latin.set("typeface", FONT)
                    for k in ("panose", "pitchFamily", "charset"):
                        latin.attrib.pop(k, None)


# ---------------------------------------------------------------- fuentes
def drawing_fonts(root):
    for el in root.iter(aq("latin")):
        tf = el.get("typeface", "")
        if not tf.startswith("+") and tf != FONT:
            el.set("typeface", FONT)
            for k in ("panose", "pitchFamily", "charset"):
                el.attrib.pop(k, None)


def word_fonts(root):
    for el in root.iter(wq("rFonts")):
        for k in ("ascii", "hAnsi", "cs"):
            el.set(wq(k), FONT)
        for k in ("asciiTheme", "hAnsiTheme", "cstheme"):
            el.attrib.pop(wq(k), None)


# ---------------------------------------------------------------- colores existentes -> referencias
def word_refresh_cache(root):
    """Actualiza el hex de cache de colores que ya apuntan al tema (con su tonalidad)."""
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for theme_attr, val_attr, tint, shade in (("themeColor", "val" if el.tag == wq("color") else "color",
                                                   "themeTint", "themeShade"),
                                                  ("themeFill", "fill", "themeFillTint", "themeFillShade")):
            tc = el.get(wq(theme_attr))
            if not tc:
                continue
            slot = WORD_SLOT_INV.get(tc, tc)
            if slot not in TEMA:
                continue
            tono = None
            if el.get(wq(tint)):
                tono = ("claro", round((1 - int(el.get(wq(tint)), 16) / 255) * 100))
            elif el.get(wq(shade)):
                tono = ("oscuro", round((1 - int(el.get(wq(shade)), 16) / 255) * 100))
            el.set(wq(val_attr), Ref(slot, tono).fallback_hex)


def _lookup(v):
    if not isinstance(v, str):
        return None
    core = (v[2:] if len(v) == 8 and v[:2].upper() == "FF" else v).upper()
    return PALETA[DEFAULT_MAP[core]] if core in DEFAULT_MAP else None


def word_remap(root):
    """Hex por defecto de Office escritos a mano -> referencia al tema Veltis."""
    for el in root.iter():
        if not isinstance(el.tag, str) or etree.QName(el).namespace != W:
            continue
        if el.get(wq("themeColor")) is None:
            attr = "val" if el.tag == wq("color") else "color"
            ref = _lookup(el.get(wq(attr)))
            if ref:
                word_set_color(el, ref, attr_val=attr)
        if el.tag == wq("shd") and el.get(wq("themeFill")) is None:
            ref = _lookup(el.get(wq("fill")))
            if ref:
                el.set(wq("fill"), ref.fallback_hex)
                el.set(wq("themeFill"), WORD_SLOT.get(ref.slot, ref.slot))
                for k, v in _word_tone_attrs(ref, "Fill").items():
                    el.set(wq(k), v)


def dml_remap(root):
    """<a:srgbClr val="4472C4"> -> <a:schemeClr val="accent1"> (conserva transformaciones hijas)."""
    for el in list(root.iter(aq("srgbClr"))):
        ref = _lookup(el.get("val"))
        if not ref:
            continue
        sc = dml_scheme(ref)
        for child in list(el):
            sc.append(child)
        el.getparent().replace(el, sc)


def xl_remap(root):
    for el in root.iter(f"{{{S}}}color", f"{{{S}}}fgColor", f"{{{S}}}bgColor"):
        ref = _lookup(el.get("rgb"))
        if ref:
            xl_set_color(el, ref)


# ---------------------------------------------------------------- Word: estilos por rol
def style_role(st):
    sid = (st.get(wq("styleId")) or "").lower()
    name_el = st.find("w:name", NS)
    name = (name_el.get(wq("val")) if name_el is not None else "").lower()
    for cand in (name, STYLE_ALIASES.get(sid, ""), sid):
        if cand in WORD_ROLES:
            return cand
    m = re.fullmatch(r"(heading|ttulo|título|titulo)\s?([1-3])", sid)
    return f"heading {m.group(2)}" if m else None


def word_role_ids(styles_root):
    return {st.get(wq("styleId")) for st in styles_root.findall("w:style", NS)
            if style_role(st) and style_role(st) != "normal"}


def set_size(rpr, pt):
    for tag in ("sz", "szCs"):
        rpr_get(rpr, tag).set(wq("val"), str(round(pt * 2)))


def word_styles(root, do_fonts, do_colors, accents, sizes):
    if do_fonts:
        dd = root.find("w:docDefaults/w:rPrDefault/w:rPr", NS)
        if dd is not None:
            rpr_get(dd, "rFonts")
        word_fonts(root)
    if not accents and not sizes:
        return
    for st in root.findall("w:style", NS):
        role = style_role(st)
        if not role:
            continue
        color, pt, bold, italic, border = WORD_ROLES[role]
        rpr = insert_ordered(st, wq("rPr"), STYLE_ORDER, W)
        if sizes and pt:
            set_size(rpr, pt)
        if not accents:
            continue
        if do_fonts:
            rf = rpr_get(rpr, "rFonts")
            for k in ("ascii", "hAnsi", "cs"):
                rf.set(wq(k), FONT)
        if bold:
            rpr_get(rpr, "b")
        if italic:
            rpr_get(rpr, "i")
        if do_colors and color:
            col = rpr_get(rpr, "color"); clear_attrs(col)
            word_set_color(col, PALETA[color])
        if do_colors and border:
            bcolor, side = border
            ppr = insert_ordered(st, wq("pPr"), STYLE_ORDER, W)
            bdr = insert_ordered(ppr, wq("pBdr"), PPR_ORDER, W)
            for c in list(bdr):
                bdr.remove(c)
            e = etree.SubElement(bdr, wq(side))
            e.set(wq("val"), "single"); e.set(wq("sz"), "12" if side == "bottom" else "24")
            e.set(wq("space"), "4")
            word_set_color(e, PALETA[bcolor], attr_val="color")


def word_strip_direct(root, role_ids):
    """En parrafos con estilo de rol, quita tamano/color directos para que mande el estilo."""
    for p in root.iter(wq("p")):
        ps = p.find("w:pPr/w:pStyle", NS)
        if ps is None or ps.get(wq("val")) not in role_ids:
            continue
        for rpr in p.iter(wq("rPr")):
            for tag in ("sz", "szCs", "color"):
                for el in rpr.findall(f"w:{tag}", NS):
                    rpr.remove(el)


def word_tables(root, do_colors, sizes):
    t = WORD_TABLA
    for tbl in root.iter(wq("tbl")):
        for ri, tr in enumerate(tbl.findall("w:tr", NS)):
            for tc in tr.findall("w:tc", NS):
                tcpr = tc.find("w:tcPr", NS)
                if tcpr is None:
                    tcpr = etree.Element(wq("tcPr")); tc.insert(0, tcpr)
                if do_colors:
                    if ri == 0:
                        word_set_fill(insert_ordered(tcpr, wq("shd"), TCPR_ORDER, W), PALETA[t["encabezado_fondo"]])
                    elif ri % 2 == 0:
                        word_set_fill(insert_ordered(tcpr, wq("shd"), TCPR_ORDER, W), PALETA[t["banda_fondo"]])
                    else:
                        for sh in tcpr.findall("w:shd", NS):
                            tcpr.remove(sh)
                for r in tc.iter(wq("r")):
                    rpr = r.find("w:rPr", NS)
                    if rpr is None:
                        rpr = etree.Element(wq("rPr")); r.insert(0, rpr)
                    if ri == 0 and do_colors:
                        rpr_get(rpr, "b")
                        col = rpr_get(rpr, "color"); clear_attrs(col)
                        word_set_color(col, PALETA[t["encabezado_texto"]])
                    if sizes:
                        set_size(rpr, t["encabezado_pt"] if ri == 0 else t["cuerpo_pt"])


# ---------------------------------------------------------------- PowerPoint
def ppt_master(root, do_colors, sizes):
    txs = root.find("p:txStyles", NS)
    if txs is None:
        return
    title = txs.find("p:titleStyle/a:lvl1pPr", NS)
    if title is not None:
        color, pt, bold = PPT_ROLES["titulo"]
        d = insert_ordered(title, aq("defRPr"), LVL_ORDER, A)
        if sizes:
            d.set("sz", str(pt * 100))
        if bold:
            d.set("b", "1")
        if do_colors:
            dml_solid_fill(d, PALETA[color])
    body = txs.find("p:bodyStyle", NS)
    if body is None:
        return
    for i in range(1, 10):
        lvl = body.find(f"a:lvl{i}pPr", NS)
        if lvl is None:
            continue
        if sizes:
            insert_ordered(lvl, aq("defRPr"), LVL_ORDER, A).set("sz", str(PPT_ROLES["cuerpo_pt"][i] * 100))
        if do_colors:
            for old in lvl.findall("a:buClrTx", NS):
                lvl.remove(old)
            bc = insert_ordered(lvl, aq("buClr"), LVL_ORDER, A)
            for c in list(bc):
                bc.remove(c)
            bc.append(dml_scheme(PALETA[PPT_ROLES["vineta_nivel1" if i == 1 else "vineta_otros"]]))


def ppt_strip_title_direct(root):
    """En diapositivas/disenos: quita tamano y color directos de titulos para que mande el patron."""
    for sp in root.iter(f"{{{P}}}sp"):
        ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
        if ph is None or ph.get("type") not in ("title", "ctrTitle"):
            continue
        for rpr in sp.iter(aq("rPr"), aq("defRPr"), aq("endParaRPr")):
            rpr.attrib.pop("sz", None)
            for f in FILLS:
                for old in rpr.findall(f"a:{f}", NS):
                    rpr.remove(old)


# ---------------------------------------------------------------- Excel
def xlsx_styles(root, do_fonts, sizes):
    fonts = root.find("s:fonts", NS)
    for f in root.iter(f"{{{S}}}font"):
        if do_fonts:
            name = f.find("s:name", NS)
            if name is not None:
                name.set("val", FONT)
            fam = f.find("s:family", NS)
            if fam is not None:
                fam.set("val", "2")
    if sizes and fonts is not None and len(fonts):
        sz = fonts[0].find("s:sz", NS)  # fuente 0 = estilo Normal del libro
        if sz is not None:
            sz.set("val", str(EXCEL["cuerpo_pt"]))


def xlsx_table(root):
    info = root.find("s:tableStyleInfo", NS)
    if info is None:
        info = etree.Element(f"{{{S}}}tableStyleInfo")
        ext = root.find("s:extLst", NS)
        if ext is not None:
            ext.addprevious(info)   # el esquema exige tableStyleInfo antes de extLst
        else:
            root.append(info)
    info.set("name", EXCEL["estilo_tabla"])
    info.set("showRowStripes", "1")
    for k in ("showFirstColumn", "showLastColumn", "showColumnStripes"):
        info.set(k, info.get(k, "0"))


FONT_ORDER = ["b", "i", "strike", "condense", "extend", "outline", "shadow", "u", "vertAlign", "sz",
              "color", "name", "family", "charset", "scheme"]
sq = lambda t: f"{{{S}}}{t}"


def _cell_has_value(c):
    return c.find("s:v", NS) is not None or c.find("s:is", NS) is not None


class XlStyler:
    """Crea estilos de celda (xf) nuevos a partir de los existentes, con referencias al tema."""
    def __init__(self, styles_root, sizes):
        self.root, self.sizes, self.cache = styles_root, sizes, {}
        self.fonts = styles_root.find("s:fonts", NS)
        self.fills = styles_root.find("s:fills", NS)
        self.xfs = styles_root.find("s:cellXfs", NS)

    def _append(self, parent, el):
        parent.append(el)
        parent.set("count", str(len(parent)))
        return len(parent) - 1

    def xf_for(self, old_s, role, fill_ref):
        key = (old_s, role, fill_ref)
        if key in self.cache:
            return self.cache[key]
        spec = EXCEL[role] if role else None
        old_xf = self.xfs[old_s] if old_s < len(self.xfs) else self.xfs[0]
        xf = etree.fromstring(etree.tostring(old_xf))
        if spec:
            font_id = int(old_xf.get("fontId", "0"))
            font = etree.fromstring(etree.tostring(self.fonts[font_id]))
            if spec["negrita"]:
                insert_ordered(font, sq("b"), FONT_ORDER, S)
            if self.sizes:
                insert_ordered(font, sq("sz"), FONT_ORDER, S).set("val", str(spec["pt"]))
            xl_set_color(insert_ordered(font, sq("color"), FONT_ORDER, S), PALETA[spec["color"]])
            xf.set("fontId", str(self._append(self.fonts, font)))
            xf.set("applyFont", "1")
        if fill_ref:
            fill = etree.Element(sq("fill"))
            pf = etree.SubElement(fill, sq("patternFill")); pf.set("patternType", "solid")
            xl_set_color(etree.SubElement(pf, sq("fgColor")), PALETA[fill_ref])
            etree.SubElement(pf, sq("bgColor")).set("indexed", "64")
            xf.set("fillId", str(self._append(self.fills, fill)))
            xf.set("applyFill", "1")
        self.cache[key] = self._append(self.xfs, xf)
        return self.cache[key]


def xlsx_ranges(zin, sizes):
    """Hojas sin tabla formal: detecta fila de titulo y de encabezado y las pinta con el tema."""
    names = zin.namelist()
    if "xl/styles.xml" not in names:
        return {}
    styles = etree.fromstring(zin.read("xl/styles.xml"))
    if styles.find("s:cellXfs", NS) is None or styles.find("s:fonts", NS) is None:
        return {}
    if styles.find("s:fills", NS) is None:
        return {}
    st = XlStyler(styles, sizes)
    out = {}
    for fn in names:
        if not re.fullmatch(r"xl/worksheets/sheet\d+\.xml", fn):
            continue
        ws = etree.fromstring(zin.read(fn))
        tp = ws.find("s:tableParts", NS)
        if tp is not None and len(tp):
            continue  # ya tiene tablas formales: las estiliza xlsx_table
        rows = ws.findall("s:sheetData/s:row", NS)
        filled = [(r, [c for c in r.findall("s:c", NS) if _cell_has_value(c)]) for r in rows[:30]]
        header_i = next((i for i, (r, cs) in enumerate(filled) if len(cs) >= 2), None)
        if header_i is None:
            continue
        title_i = next((i for i, (r, cs) in enumerate(filled[:header_i]) if len(cs) == 1), None)
        if title_i is not None:
            for c in filled[title_i][1]:
                c.set("s", str(st.xf_for(int(c.get("s", "0")), "titulo", EXCEL["titulo"]["fondo"])))
        header_row = filled[header_i][0]
        for c in header_row.findall("s:c", NS):
            if _cell_has_value(c):
                c.set("s", str(st.xf_for(int(c.get("s", "0")), "encabezado", EXCEL["encabezado"]["fondo"])))
        # filas de datos contiguas bajo el encabezado -> bandas
        band = EXCEL.get("banda_fondo")
        if band:
            cols = {re.sub(r"\d", "", c.get("r", "")) for c in filled[header_i][1]}
            data_rows = rows[rows.index(header_row) + 1:]
            for k, r in enumerate(data_rows):
                cells = [c for c in r.findall("s:c", NS) if re.sub(r"\d", "", c.get("r", "")) in cols]
                if not any(_cell_has_value(c) for c in cells):
                    break
                if k % 2 == 1:
                    for c in cells:
                        c.set("s", str(st.xf_for(int(c.get("s", "0")), None, band)))
        out[fn] = etree.tostring(ws, xml_declaration=True, encoding="UTF-8", standalone=True)
    if out:
        out["xl/styles.xml"] = etree.tostring(styles, xml_declaration=True, encoding="UTF-8", standalone=True)
    return out


# ---------------------------------------------------------------- HTML
# En la web la "referencia al tema" son variables CSS: las tonalidades se derivan de la variable base
# con sintaxis de color relativo hsl(from var(...)), asi que cambiar --enfasis-1 cambia todas sus tonalidades (igual que el tema de Office).
HTML_ROLES = {
    #  selector                 color claro                 color oscuro (dark mode)     tamano    peso  cursiva
    "h1":                     ("ENFASIS_1",               "ENFASIS_1",                 "2.25rem", 700, False),
    "h2":                     ("ENFASIS_2_OSCURO_50",     "ENFASIS_2",                 "1.5rem",  700, False),
    "h3":                     ("ENFASIS_1_OSCURO_25",     "ENFASIS_1_CLARO_40",        "1.25rem", 700, False),
    "h4":                     ("OSCURO_2",                "CLARO_2",                   "1rem",    700, False),
    "body":                   ("OSCURO_1",                "CLARO_1",                   "1rem",    400, False),
    "blockquote":             ("OSCURO_2",                "CLARO_2",                   "1rem",    400, True),
    "figcaption, caption":    ("ENFASIS_2_OSCURO_50",     "ENFASIS_2",                 "0.8125rem", 400, True),
}
FONTS_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              '<link href="https://fonts.googleapis.com/css2?family=Overpass:ital,wght@0,300;0,400;0,700;0,800;0,900;1,400;1,700&display=swap" rel="stylesheet">')


def css_var(name):
    return "--" + name.lower().replace("_", "-")


def css_value(name):
    """Valor CSS de una variable de PALETA, derivado de la variable base (no hex fijo)."""
    ref = PALETA[name]
    base = next(b for b, slot in BASES.items() if slot == ref.slot)
    if not ref.tono:
        return None
    kind, p = ref.tono
    # Igual que Office (lumMod/lumOff en HSL): conserva tono y saturacion, solo mueve la luminosidad
    f = (100 - p) / 100
    l = f"calc(l * {f:g} + {p})" if kind == "claro" else f"calc(l * {f:g})"
    return f"hsl(from var({css_var(base)}) h s {l})"


def build_css():
    L = [":root {", f"  --fuente: '{FONT}', system-ui, sans-serif;"]
    for base, slot in BASES.items():
        L.append(f"  {css_var(base)}: #{TEMA[slot]};")
    for name in PALETA:
        v = css_value(name)
        if v:
            L.append(f"  {css_var(name)}: {v};")
    for i in range(1, 7):
        L.append(f"  --serie-{i}: var(--enfasis-{i});")   # graficos
    light = {"fondo": "var(--claro-1)", "superficie": "var(--claro-2-claro-80)", "borde": "var(--claro-2)",
             "th-fondo": "var(--enfasis-1)", "th-texto": "var(--claro-1)", "banda": "var(--enfasis-2-claro-80)",
             "enlace": "var(--hipervinculo)", "enlace-visitado": "var(--hipervinculo-visitado)"}
    dark = {"fondo": "color-mix(in srgb, var(--oscuro-2) 45%, var(--oscuro-1))",
            "superficie": "var(--oscuro-2)", "borde": "var(--oscuro-2-claro-40)",
            "th-fondo": "var(--enfasis-1)", "th-texto": "var(--claro-1)",
            "banda": "color-mix(in srgb, var(--enfasis-2) 14%, var(--oscuro-1))",
            "enlace": "var(--hipervinculo-claro-40)", "enlace-visitado": "var(--hipervinculo-visitado-claro-40)"}
    for k, v in light.items():
        L.append(f"  --{k}: {v};")
    for sel, (c, _, *_r) in HTML_ROLES.items():
        L.append(f"  --c-{sel.split(',')[0]}: var({css_var(c)});")
    L.append("}")
    dark_lines = [f"    --{k}: {v};" for k, v in dark.items()] + \
                 [f"    --c-{sel.split(',')[0]}: var({css_var(d)});" for sel, (_, d, *_r) in HTML_ROLES.items()]
    L.append('@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {\n' +
             "\n".join("  " + x for x in dark_lines) + "\n  }\n}")
    L.append(':root[data-theme="dark"] {\n' + "\n".join(dark_lines) + "\n}")
    # reglas base
    L.append("body { font-family: var(--fuente); background: var(--fondo); color: var(--c-body); "
             f"font-size: {HTML_ROLES['body'][2]}; line-height: 1.55; }}")
    for sel, (_, _, size, weight, italic) in HTML_ROLES.items():
        if sel == "body":
            continue
        key = sel.split(",")[0]
        L.append(f"{sel} {{ font-family: var(--fuente); color: var(--c-{key}); font-size: {size}; "
                 f"font-weight: {weight};{' font-style: italic;' if italic else ''} }}")
    L += ["h1 { line-height: 1.15; margin: 0 0 .5em; }",
          "h2 { border-bottom: 2px solid var(--enfasis-2); padding-bottom: .2em; }",
          "blockquote { border-left: 4px solid var(--enfasis-2); margin: 1em 0; padding: .25em 1em; }",
          "a { color: var(--enlace); } a:visited { color: var(--enlace-visitado); }",
          "li::marker { color: var(--enfasis-1); }",
          "table { border-collapse: collapse; font-size: .875rem; }",
          "th { background: var(--th-fondo); color: var(--th-texto); font-weight: 700; text-align: left; }",
          "th, td { padding: .45em .75em; border-bottom: 1px solid var(--borde); }",
          "tbody tr:nth-child(even) { background: var(--banda); }",
          "hr { border: 0; border-top: 2px solid var(--enfasis-1); }",
          "button, .btn { font-family: var(--fuente); background: var(--enfasis-1); color: var(--claro-1); "
          "border: 0; border-radius: 6px; padding: .5em 1em; font-weight: 700; }"]
    return "\n".join(L)


def html_hex_to_vars(text):
    """Colores por defecto de Office/hex conocidos escritos en CSS -> var(--...) de la paleta."""
    def rep(m):
        core = m.group(1).upper()
        return f"var({css_var(DEFAULT_MAP[core])})" if core in DEFAULT_MAP else m.group(0)
    return re.sub(r"#([0-9A-Fa-f]{6})\b", rep, text)


def process_html(src, dst, do_colors=True):
    text = Path(src).read_text(encoding="utf-8")
    block = f'<style id="veltis-tema">\n{build_css()}\n</style>'
    text = re.sub(r'<style id="veltis-tema">.*?</style>', "", text, flags=re.S)
    if "fonts.googleapis.com/css2?family=Overpass" not in text:
        block = FONTS_LINK + "\n" + block
    if do_colors:
        text = html_hex_to_vars(text)
    m = re.search(r"</head\s*>", text, re.I)
    text = text[:m.start()] + block + "\n" + text[m.start():] if m else block + "\n" + text
    Path(dst).write_text(text, encoding="utf-8")
    return {"theme": 1, "parts": 1}


# ---------------------------------------------------------------- proceso
def process(src, dst, do_colors=True, do_fonts=True, accents=True, sizes=True, strip=True):
    stats = {"theme": 0, "parts": 0}
    tmp = Path(str(dst) + ".tmp")
    with zipfile.ZipFile(src) as zin:
        overrides = xlsx_ranges(zin, sizes) if (accents and do_colors) else {}
        role_ids = set()
        if "word/styles.xml" in zin.namelist():
            role_ids = word_role_ids(etree.fromstring(zin.read("word/styles.xml")))
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                fn = info.filename
                data = overrides.get(fn) or zin.read(fn)
                if fn.endswith(".xml") and not fn.startswith("customXml/"):
                    try:
                        root = etree.fromstring(data)
                    except etree.XMLSyntaxError:
                        root = None
                    if root is not None:
                        changed = True
                        if re.search(r"/theme/theme\d*\.xml$", fn):
                            theme_xml(root, do_colors, do_fonts); stats["theme"] += 1
                        elif fn == "word/styles.xml":
                            word_styles(root, do_fonts, do_colors, accents, sizes)
                            if do_colors: word_remap(root); word_refresh_cache(root)
                        elif fn.startswith("word/") and re.search(r"(document|header\d*|footer\d*|footnotes|endnotes|numbering|comments)\.xml$", fn):
                            if do_fonts: word_fonts(root); drawing_fonts(root)
                            if do_colors: word_remap(root); dml_remap(root)
                            if strip and (accents or sizes): word_strip_direct(root, role_ids)
                            if fn == "word/document.xml" and accents:
                                word_tables(root, do_colors, sizes)
                            if do_colors: word_refresh_cache(root)
                        elif fn == "xl/styles.xml":
                            xlsx_styles(root, do_fonts, sizes)
                            if do_colors: xl_remap(root)
                        elif re.fullmatch(r"xl/tables/table\d+\.xml", fn):
                            if do_colors and accents: xlsx_table(root)
                        elif fn.startswith(("ppt/", "xl/charts/", "word/charts/", "xl/drawings/")) or "/diagrams/" in fn:
                            if do_fonts: drawing_fonts(root)
                            if do_colors: dml_remap(root)
                            if accents and re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", fn):
                                ppt_master(root, do_colors, sizes)
                            if strip and accents and re.fullmatch(r"ppt/(slides/slide|slideLayouts/slideLayout)\d+\.xml", fn):
                                ppt_strip_title_direct(root)
                        else:
                            changed = False
                        if changed:
                            data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                            stats["parts"] += 1
                zout.writestr(info, data)
    shutil.move(str(tmp), dst)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--css", action="store_true", help="imprime el bloque CSS Veltis (para páginas HTML nuevas)")
    ap.add_argument("-o", "--output")
    ap.add_argument("--inplace", action="store_true")
    ap.add_argument("--colors-only", action="store_true", help="no cambiar fuentes")
    ap.add_argument("--fonts-only", action="store_true", help="solo Overpass")
    ap.add_argument("--theme-only", action="store_true", help="solo tema: no pintar ni redimensionar elementos")
    ap.add_argument("--no-sizes", action="store_true", help="no cambiar tamanos de texto")
    ap.add_argument("--keep-direct", action="store_true", help="respetar tamano/color puesto a mano en titulos")
    a = ap.parse_args()
    if a.css:
        print(FONTS_LINK + "\n<style id=\"veltis-tema\">\n" + build_css() + "\n</style>")
        return
    for f in a.files:
        src = Path(f)
        if a.output and len(a.files) == 1:
            dst = Path(a.output)
        elif a.inplace:
            dst = src
        else:
            dst = src.with_name(f"{src.stem}_veltis{src.suffix}")
        if src.suffix.lower() in (".html", ".htm"):
            st = process_html(src, dst, do_colors=not a.fonts_only)
            print(f"OK {src.name} -> {dst} (HTML: variables CSS Veltis + Overpass)")
            continue
        st = process(src, dst, do_colors=not a.fonts_only, do_fonts=not a.colors_only,
                     accents=not a.theme_only, sizes=not (a.no_sizes or a.theme_only),
                     strip=not a.keep_direct)
        if st["theme"] == 0:
            print(f"AVISO {src.name}: sin tema embebido; solo se cambiaron fuentes/colores explicitos", file=sys.stderr)
        print(f"OK {src.name} -> {dst} ({st['parts']} partes, {st['theme']} temas)")


if __name__ == "__main__":
    main()
