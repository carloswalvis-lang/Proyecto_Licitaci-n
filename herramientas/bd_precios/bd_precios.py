#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bd_precios.py - Base general de precios y cotizaciones de Veltis (carpeta BD PRECIOS).

Solo libreria estandar de Python 3. Lo usa el skill buscar-cotizaciones y sirve
para analizar la base a mano.

Carpeta de datos (donde estan los CSV), en este orden:
  1. Variable de entorno BD_PRECIOS_DIR.
  2. Clave "bd_precios" de config/local.json del repositorio licitaciones-base
     (este script vive en <repo>/herramientas/bd_precios/).
  3. La carpeta donde esta el script, solo si NO esta dentro del repositorio
     (copia junto a los CSV, como en la carpeta compartida BD PRECIOS).
Dentro del repositorio, sin 1 ni 2, el script se detiene: los CSV nunca deben
quedar en el repo.

Archivos que administra (en la misma carpeta):
  Cotizaciones.csv          una fila por cotizacion (PROV = tercero FSChile, MERC = mercado)
  Busquedas_sin_precio.csv  busquedas que no encontraron precio publico

Conjuntos de datos de referencia (misma carpeta, estructura propia, varios proyectos):
  Arriendo_Equipos.csv      valor hora (UF) de arriendo de equipos por proveedor y plazo P1-P4
  Costos_MO_Spot.csv        costo empresa de mano de obra spot por cargo (CLP)

Comandos:
  buscar    --familia F [--texto "plancha|lamina&3 mm"] [--solo-vigentes]
  arriendo  [--equipo "pluma|grua"] [--capacidad "10"] [--horas 180] [--plazo P1] [--con-atipicos]
  mo        [--cargo "soldador"] [--especialidad "piping"] [--zona Norte]
  cargar    --dataset arriendo|mo --archivo f.csv --proyecto "Nombre" --fuente "archivo origen"
  duplicados --archivo candidatos.json | --stdin   (compara candidatos con la base y sugiere accion)
  historial --texto "..." [--familia F]
  agregar   --archivo datos.json | --stdin      (asigna IDs, escribe, devuelve JSON)
  resumen   [--dias 90]
  verificar                                     (comprueba columnas, IDs y fechas)
  pendientes-sync --archivo lineas.jsonl        (carga filas guardadas offline, sin duplicar)

Salida: siempre JSON por stdout. Codigo de salida distinto de 0 = error (mensaje en stderr).
"""
import argparse, csv, json, os, sys, time, unicodedata, tempfile
from datetime import date, datetime

def _carpeta_datos():
    """Resuelve la carpeta de los CSV (ver docstring)."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.get("BD_PRECIOS_DIR", "").strip()
    if env:
        return os.path.abspath(os.path.expanduser(env))
    raiz = os.path.abspath(os.path.join(aqui, os.pardir, os.pardir))
    es_repo = os.path.exists(os.path.join(raiz, "config", "local.example.json"))
    cfg = os.path.join(raiz, "config", "local.json")
    if os.path.exists(cfg):
        try:
            with open(cfg, "r", encoding="utf-8-sig") as f:
                ruta = (json.load(f).get("bd_precios") or "").strip()
        except (OSError, ValueError) as e:
            sys.stderr.write("No se pudo leer config/local.json: %s\n" % e)
            sys.exit(2)
        if ruta:
            return os.path.abspath(os.path.expanduser(ruta))
    if es_repo:
        sys.stderr.write("Falta la carpeta de BD PRECIOS: define BD_PRECIOS_DIR o la clave "
                         "\"bd_precios\" en config/local.json (ver config/local.example.json).\n")
        sys.exit(2)
    return aqui


CARPETA = _carpeta_datos()
if not os.path.isdir(CARPETA):
    sys.stderr.write("La carpeta de BD PRECIOS no existe o no es accesible: %s\n" % CARPETA)
    sys.exit(2)
F_COT = os.path.join(CARPETA, "Cotizaciones.csv")
F_BUS = os.path.join(CARPETA, "Busquedas_sin_precio.csv")
F_LOCK = os.path.join(CARPETA, ".bd_precios.lock")
F_ARR = os.path.join(CARPETA, "Arriendo_Equipos.csv")
F_MO = os.path.join(CARPETA, "Costos_MO_Spot.csv")
META = ["Proyecto_origen", "Fuente", "Fecha_carga"]
COLS_ARR = ["Equipo", "Tipo", "Capacidad_Modelo", "Horas_Min_Mes", "Requiere_Cert", "Proveedor",
            "Hora_UF_P1", "HoraAdic_UF_P1", "Hora_UF_P2", "HoraAdic_UF_P2", "Hora_UF_P3",
            "HoraAdic_UF_P3", "Hora_UF_P4", "HoraAdic_UF_P4", "Rank_P1", "Periodos_Origen",
            "Oferta", "Moneda_Origen", "Obs"]
COLS_MO = ["Cargo", "Cargo_Homologado", "Cantidad", "Especialidad", "Zona", "Liquido_Diario_Objetivo",
           "Sueldo_Base", "Bono_Parada_Planta", "Asig_Pasajes", "Asig_Colacion", "Asig_Movilizacion",
           "Total_Haberes_Mes", "Leyes_Sociales_Empresa_Mes", "Costo_Empresa_Mes", "Costo_Diario",
           "Costo_Diario_con_Descanso", "Valor_HH", "Valor_HH_Extra", "Liquido_Diario_Calculado", "Obs"]
DATASETS = {"arriendo": (F_ARR, COLS_ARR + META), "mo": (F_MO, COLS_MO + META)}

COLS_COT = ["ID", "Tipo", "Familia", "Fecha_cotizacion", "Fecha_registro", "Descripcion",
            "Unidad", "Precio_neto_CLP", "Proveedor_Fuentes", "Link_o_Ruta_FS",
            "Ubicacion_Detalle", "Notas", "Proyecto_origen", "Empresa_operativa", "GC",
            "Zona", "Usuario", "Estado"]
COLS_BUS = ["Fecha", "Familia", "Descripcion", "Revisado", "Proveedores_a_solicitar",
            "Proyecto_origen", "Usuario"]
REQ_COT = ["tipo", "familia", "fecha_cotizacion", "descripcion", "unidad", "precio_neto",
           "proveedor", "link"]
REQ_BUS = ["familia", "descripcion"]
DELIM = ";"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def familia_norm(s):
    return norm(s).upper()


def leer(path, cols):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f, delimiter=DELIM)
        faltan = [c for c in cols if c not in (r.fieldnames or [])]
        if faltan:
            raise SystemExit("Columnas faltantes en %s: %s" % (os.path.basename(path), faltan))
        return list(r)


def escribir(path, cols, filas):
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".csv", dir=CARPETA)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, delimiter=DELIM, extrasaction="ignore")
            w.writeheader()
            for fila in filas:
                w.writerow({c: fila.get(c, "") for c in cols})
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


class Lock:
    """Bloqueo simple por archivo para que dos sesiones no escriban a la vez."""
    def __enter__(self):
        t0 = time.time()
        while True:
            try:
                self.fd = os.open(F_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, str(os.getpid()).encode())
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(F_LOCK) > 60:  # bloqueo viejo
                        os.remove(F_LOCK)
                        continue
                except OSError:
                    pass
                if time.time() - t0 > 30:
                    raise SystemExit("Base ocupada: otra sesion esta escribiendo. Reintenta en un minuto.")
                time.sleep(0.5)

    def __exit__(self, *a):
        try:
            os.close(self.fd)
        finally:
            if os.path.exists(F_LOCK):
                os.remove(F_LOCK)


def asegurar_archivos():
    if not os.path.exists(F_COT):
        escribir(F_COT, COLS_COT, [])
    if not os.path.exists(F_BUS):
        escribir(F_BUS, COLS_BUS, [])


def edad_dias(fecha_iso):
    try:
        return (date.today() - datetime.strptime(fecha_iso, "%Y-%m-%d").date()).days
    except Exception:
        return None


def coincide(descripcion, texto):
    """texto = 'plancha|lamina&3 mm' -> todas las claves (separadas por &) deben aparecer;
    dentro de cada clave, cualquiera de sus alternativas (separadas por |)."""
    if not texto:
        return True
    d = norm(descripcion)
    for clave in texto.split("&"):
        alts = [norm(a) for a in clave.split("|") if a.strip()]
        if alts and not any(a in d for a in alts):
            return False
    return True


def cmd_buscar(a):
    filas = leer(F_COT, COLS_COT)
    fam = familia_norm(a.familia) if a.familia else None
    out = []
    for f in filas:
        if fam and familia_norm(f["Familia"]) != fam:
            continue
        if a.solo_vigentes and norm(f["Estado"]) not in ("", "vigente"):
            continue
        if not coincide(f["Descripcion"], a.texto):
            continue
        f = dict(f)
        f["edad_dias"] = edad_dias(f["Fecha_cotizacion"])
        out.append(f)
    out.sort(key=lambda x: x["Fecha_cotizacion"], reverse=True)
    bus = []
    for b in leer(F_BUS, COLS_BUS):
        if fam and familia_norm(b["Familia"]) != fam:
            continue
        if coincide(b["Descripcion"], a.texto):
            b = dict(b)
            b["edad_dias"] = edad_dias(b["Fecha"])
            bus.append(b)
    print(json.dumps({"cotizaciones": out, "busquedas_sin_precio": bus}, ensure_ascii=False))


def cmd_historial(a):
    filas = [f for f in leer(F_COT, COLS_COT)
             if coincide(f["Descripcion"], a.texto)
             and (not a.familia or familia_norm(f["Familia"]) == familia_norm(a.familia))]
    filas.sort(key=lambda x: x["Fecha_cotizacion"])
    print(json.dumps([{k: f[k] for k in ("ID", "Fecha_cotizacion", "Descripcion", "Unidad",
                                          "Precio_neto_CLP", "Proveedor_Fuentes", "Proyecto_origen",
                                          "Estado")} for f in filas], ensure_ascii=False))


def siguiente_id(filas, tipo):
    mx = 0
    for f in filas:
        if f["ID"].startswith(tipo + "-"):
            try:
                mx = max(mx, int(f["ID"].split("-")[1]))
            except ValueError:
                pass
    return mx


def validar_fecha(s):
    datetime.strptime(s, "%Y-%m-%d")


def agregar_datos(datos, evitar_duplicados=False):
    cots = datos.get("cotizaciones", [])
    buss = datos.get("busquedas", [])
    hoy = date.today().isoformat()
    for c in cots:
        faltan = [k for k in REQ_COT if c.get(k) in (None, "")]
        if faltan:
            raise SystemExit("Cotizacion incompleta, faltan %s: %s" % (faltan, c.get("descripcion")))
        if c["tipo"] not in ("PROV", "MERC"):
            raise SystemExit("tipo debe ser PROV o MERC")
        validar_fecha(c["fecha_cotizacion"])
        if int(c["precio_neto"]) <= 0:
            raise SystemExit("precio_neto debe ser entero > 0: %s" % c["descripcion"])
    for b in buss:
        faltan = [k for k in REQ_BUS if not b.get(k)]
        if faltan:
            raise SystemExit("Busqueda incompleta, faltan %s" % faltan)

    with Lock():
        asegurar_archivos()
        filas = leer(F_COT, COLS_COT)
        bus_fil = leer(F_BUS, COLS_BUS)
        cont = {"PROV": siguiente_id(filas, "PROV"), "MERC": siguiente_id(filas, "MERC")}
        claves = {(norm(f["Descripcion"]), norm(f["Proveedor_Fuentes"]), f["Fecha_cotizacion"])
                  for f in filas}
        creadas, omitidas, reemplazadas = [], [], []
        for c in cots:
            clave = (norm(c["descripcion"]), norm(c["proveedor"]), c["fecha_cotizacion"])
            if evitar_duplicados and clave in claves:
                omitidas.append(c["descripcion"])
                continue
            cont[c["tipo"]] += 1
            nid = "%s-%04d" % (c["tipo"], cont[c["tipo"]])
            fila = {
                "ID": nid, "Tipo": c["tipo"], "Familia": familia_norm(c["familia"]),
                "Fecha_cotizacion": c["fecha_cotizacion"], "Fecha_registro": hoy,
                "Descripcion": c["descripcion"], "Unidad": c["unidad"],
                "Precio_neto_CLP": int(c["precio_neto"]), "Proveedor_Fuentes": c["proveedor"],
                "Link_o_Ruta_FS": c["link"], "Ubicacion_Detalle": c.get("detalle", ""),
                "Notas": c.get("notas", ""), "Proyecto_origen": c.get("proyecto", ""),
                "Empresa_operativa": c.get("empresa", ""), "GC": c.get("gc", ""),
                "Zona": c.get("zona", ""), "Usuario": c.get("usuario", ""), "Estado": "vigente",
            }
            old = c.get("reemplaza")
            if old:
                for f in filas:
                    if f["ID"] == old:
                        f["Estado"] = "reemplazada por " + nid
                        reemplazadas.append(old)
                if "Reemplaza " + old not in fila["Notas"]:
                    fila["Notas"] = (fila["Notas"] + ". " if fila["Notas"] else "") + "Reemplaza " + old
            filas.append(fila)
            claves.add(clave)
            creadas.append({"ID": nid, "Descripcion": c["descripcion"]})
        nuevas_bus = 0
        for b in buss:
            bus_fil.append({"Fecha": b.get("fecha", hoy), "Familia": familia_norm(b["familia"]),
                            "Descripcion": b["descripcion"], "Revisado": b.get("revisado", ""),
                            "Proveedores_a_solicitar": b.get("proveedores", ""),
                            "Proyecto_origen": b.get("proyecto", ""), "Usuario": b.get("usuario", "")})
            nuevas_bus += 1
        if creadas or reemplazadas:
            escribir(F_COT, COLS_COT, filas)
        if nuevas_bus:
            escribir(F_BUS, COLS_BUS, bus_fil)
    print(json.dumps({"creadas": creadas, "omitidas_por_duplicado": omitidas,
                      "reemplazadas": reemplazadas, "busquedas_sin_precio": nuevas_bus},
                     ensure_ascii=False))


def cmd_agregar(a):
    raw = sys.stdin.read() if a.stdin else open(a.archivo, "r", encoding="utf-8").read()
    agregar_datos(json.loads(raw))


def cmd_pendientes(a):
    cots, buss = [], []
    for linea in open(a.archivo, "r", encoding="utf-8"):
        linea = linea.strip()
        if not linea:
            continue
        d = json.loads(linea)
        (buss if d.get("_tipo") == "busqueda" else cots).append(d)
    agregar_datos({"cotizaciones": cots, "busquedas": buss}, evitar_duplicados=True)


def _num(x):
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return None


def cmd_arriendo(a):
    import statistics
    if not os.path.exists(F_ARR):
        print(json.dumps({"filas": [], "resumen": None})); return
    pl = (a.plazo or "P1").upper()
    if pl not in ("P1", "P2", "P3", "P4"):
        raise SystemExit("--plazo debe ser P1, P2, P3 o P4 (P1 = 1-3 meses, P2 = 4-6, P3 = 7-9, P4 = 10-12)")
    col, cola = "Hora_UF_" + pl, "HoraAdic_UF_" + pl
    out, excl = [], 0
    for f in leer(F_ARR, COLS_ARR + META):
        if a.equipo and not coincide(f["Equipo"] + " " + f["Tipo"], a.equipo): continue
        if a.capacidad and not coincide(f["Capacidad_Modelo"], a.capacidad): continue
        if a.horas and str(f["Horas_Min_Mes"]).strip() != str(a.horas): continue
        v = _num(f[col])
        atip = "atipico" in norm(f["Obs"])
        out.append({"Equipo": f["Equipo"], "Capacidad_Modelo": f["Capacidad_Modelo"],
                    "Horas_Min_Mes": f["Horas_Min_Mes"], "Proveedor": f["Proveedor"],
                    "plazo": pl, "Hora_UF": v, "HoraAdic_UF": _num(f[cola]), "Oferta": f["Oferta"],
                    "Obs": f["Obs"], "Proyecto_origen": f["Proyecto_origen"], "atipico": atip})
    vals = [r["Hora_UF"] for r in out if r["Hora_UF"] is not None and (a.con_atipicos or not r["atipico"])]
    excl = sum(1 for r in out if r["atipico"])
    res = None
    if vals:
        res = {"n": len(vals), "min": round(min(vals), 3), "mediana": round(statistics.median(vals), 3),
               "promedio": round(sum(vals) / len(vals), 3), "max": round(max(vals), 3),
               "atipicos_excluidos": 0 if a.con_atipicos else excl, "unidad": "UF por hora"}
    out.sort(key=lambda r: (r["Hora_UF"] is None, r["Hora_UF"]))
    print(json.dumps({"filas": out[:a.limite], "total_filas": len(out), "resumen": res}, ensure_ascii=False))


def cmd_mo(a):
    if not os.path.exists(F_MO):
        print(json.dumps({"filas": []})); return
    out = []
    for f in leer(F_MO, COLS_MO + META):
        if a.cargo and not coincide(f["Cargo"] + " " + f["Cargo_Homologado"], a.cargo): continue
        if a.especialidad and not coincide(f["Especialidad"], a.especialidad): continue
        if a.zona and norm(f["Zona"]) != norm(a.zona): continue
        out.append({k: f[k] for k in ("Cargo", "Cargo_Homologado", "Cantidad", "Especialidad", "Zona",
                                     "Liquido_Diario_Objetivo", "Costo_Empresa_Mes", "Costo_Diario",
                                     "Costo_Diario_con_Descanso", "Valor_HH", "Valor_HH_Extra",
                                     "Obs", "Proyecto_origen", "Fuente", "Fecha_carga")})
    print(json.dumps({"filas": out, "unidad": "CLP"}, ensure_ascii=False))


def cmd_cargar(a):
    ruta, cols = DATASETS[a.dataset]
    base_cols = [c for c in cols if c not in META]
    with open(a.archivo, "r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh, delimiter=DELIM)
        faltan = [c for c in base_cols if c not in (r.fieldnames or [])]
        if faltan:
            raise SystemExit("El archivo no tiene las columnas: %s" % faltan)
        nuevas = list(r)
    if not nuevas:
        raise SystemExit("El archivo no tiene filas")
    hoy = date.today().isoformat()
    for f in nuevas:
        f["Proyecto_origen"], f["Fuente"], f["Fecha_carga"] = a.proyecto, a.fuente, hoy
    with Lock():
        existentes = leer(ruta, cols) if os.path.exists(ruta) else []
        conservadas = [f for f in existentes if f["Proyecto_origen"] != a.proyecto]
        reemplazadas = len(existentes) - len(conservadas)
        escribir(ruta, cols, conservadas + nuevas)
    print(json.dumps({"dataset": a.dataset, "proyecto": a.proyecto, "filas_cargadas": len(nuevas),
                      "filas_reemplazadas_del_mismo_proyecto": reemplazadas,
                      "filas_de_otros_proyectos_conservadas": len(conservadas)}, ensure_ascii=False))


def _tokens(txt):
    import re
    return {t for t in re.split(r"[^a-z0-9]+", norm(txt)) if len(t) > 1}


def _unidad(u):
    return norm(u).replace(" ", "").replace(".", "")


def cmd_duplicados(a):
    """Compara candidatos {tipo, familia, descripcion, unidad, fecha_cotizacion, [claves]} con la base.
    Regla de prioridad (acordada con el usuario): la cotizacion de proveedor (PROV) prevalece sobre
    el promedio de mercado (MERC); entre filas del mismo tipo, prevalece la de fecha mas reciente."""
    raw = sys.stdin.read() if a.stdin else open(a.archivo, "r", encoding="utf-8").read()
    cands = json.loads(raw)
    if isinstance(cands, dict):
        cands = cands.get("cotizaciones", [])
    filas = [f for f in leer(F_COT, COLS_COT) if norm(f["Estado"]) in ("", "vigente")]
    res = []
    for i, c in enumerate(cands):
        fam = familia_norm(c.get("familia", ""))
        tk = _tokens(c.get("descripcion", ""))
        coin = []
        for f in filas:
            if fam and familia_norm(f["Familia"]) != fam:
                continue
            if c.get("claves"):
                ok = coincide(f["Descripcion"], c["claves"])
            else:
                tf = _tokens(f["Descripcion"])
                ok = bool(tk) and len(tk & tf) / max(len(tk | tf), 1) >= 0.8
            if ok and (not c.get("unidad") or _unidad(c["unidad"]) == _unidad(f["Unidad"])):
                coin.append(f)
        item = {"indice": i, "descripcion": c.get("descripcion"), "coincidencias": [], "sugerencia": "agregar",
                "motivo": "No hay una fila equivalente en la base"}
        for f in coin:
            e = edad_dias(f["Fecha_cotizacion"])
            item["coincidencias"].append({"ID": f["ID"], "Tipo": f["Tipo"], "Descripcion": f["Descripcion"],
                                          "Unidad": f["Unidad"], "Precio_neto_CLP": f["Precio_neto_CLP"],
                                          "Fecha_cotizacion": f["Fecha_cotizacion"], "edad_dias": e,
                                          "Proveedor_Fuentes": f["Proveedor_Fuentes"],
                                          "Proyecto_origen": f["Proyecto_origen"]})
        if coin:
            # referencia: PROV mas reciente si existe, si no MERC mas reciente
            provs = sorted([f for f in coin if f["Tipo"] == "PROV"], key=lambda f: f["Fecha_cotizacion"])
            mercs = sorted([f for f in coin if f["Tipo"] == "MERC"], key=lambda f: f["Fecha_cotizacion"])
            old = provs[-1] if provs else mercs[-1]
            nt, ot = c.get("tipo", "MERC"), old["Tipo"]
            nd, od = c.get("fecha_cotizacion", ""), old["Fecha_cotizacion"]
            if nt == "PROV" and ot == "MERC":
                item.update(sugerencia="reemplazar", reemplaza=old["ID"],
                            motivo="La cotizacion de proveedor tiene prioridad sobre el promedio de mercado")
            elif nt == "MERC" and ot == "PROV":
                if (edad_dias(od) or 0) <= 90:
                    item.update(sugerencia="omitir", reemplaza=old["ID"],
                                motivo="Prevalece la cotizacion de proveedor vigente (<= 90 dias)")
                else:
                    item.update(sugerencia="preguntar", reemplaza=old["ID"],
                                motivo="La cotizacion de proveedor tiene mas de 90 dias: decide el usuario")
            elif nd > od:
                item.update(sugerencia="reemplazar", reemplaza=old["ID"], motivo="Misma clase de fuente y fecha mas reciente")
            else:
                item.update(sugerencia="omitir", reemplaza=old["ID"], motivo="La fila existente es igual o mas reciente")
        res.append(item)
    print(json.dumps(res, ensure_ascii=False))


def cmd_resumen(a):
    filas = leer(F_COT, COLS_COT)
    vig = [f for f in filas if norm(f["Estado"]) in ("", "vigente")]
    por_fam = {}
    for f in vig:
        d = por_fam.setdefault(f["Familia"], {"filas": 0, "antiguas": 0, "ultima": ""})
        d["filas"] += 1
        e = edad_dias(f["Fecha_cotizacion"])
        if e is not None and e > a.dias:
            d["antiguas"] += 1
        d["ultima"] = max(d["ultima"], f["Fecha_cotizacion"])
    por_proy = {}
    for f in filas:
        por_proy[f["Proyecto_origen"] or "(sin proyecto)"] = por_proy.get(f["Proyecto_origen"] or "(sin proyecto)", 0) + 1
    print(json.dumps({"total_filas": len(filas), "vigentes": len(vig),
                      "PROV": sum(1 for f in filas if f["Tipo"] == "PROV"),
                      "MERC": sum(1 for f in filas if f["Tipo"] == "MERC"),
                      "dias_umbral": a.dias, "por_familia": por_fam, "por_proyecto": por_proy,
                      "datasets": {k: (len(leer(v[0], v[1])) if os.path.exists(v[0]) else 0)
                                   for k, v in DATASETS.items()}},
                     ensure_ascii=False))


def cmd_verificar(a):
    problemas, ids = [], set()
    for f in leer(F_COT, COLS_COT):
        if f["ID"] in ids:
            problemas.append("ID repetido: " + f["ID"])
        ids.add(f["ID"])
        if edad_dias(f["Fecha_cotizacion"]) is None:
            problemas.append("%s: fecha invalida '%s'" % (f["ID"], f["Fecha_cotizacion"]))
        if not str(f["Precio_neto_CLP"]).isdigit():
            problemas.append("%s: precio no entero '%s'" % (f["ID"], f["Precio_neto_CLP"]))
    leer(F_BUS, COLS_BUS)
    for k, (ruta, cols) in DATASETS.items():
        if os.path.exists(ruta):
            try:
                leer(ruta, cols)
            except SystemExit as e:
                problemas.append("%s: %s" % (k, e))
    print(json.dumps({"ok": not problemas, "problemas": problemas}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("buscar"); b.add_argument("--familia"); b.add_argument("--texto")
    b.add_argument("--solo-vigentes", action="store_true"); b.set_defaults(fn=cmd_buscar)
    h = sp.add_parser("historial"); h.add_argument("--texto", required=True)
    h.add_argument("--familia"); h.set_defaults(fn=cmd_historial)
    g = sp.add_parser("agregar"); g.add_argument("--archivo"); g.add_argument("--stdin", action="store_true")
    g.set_defaults(fn=cmd_agregar)
    r = sp.add_parser("resumen"); r.add_argument("--dias", type=int, default=90); r.set_defaults(fn=cmd_resumen)
    v = sp.add_parser("verificar"); v.set_defaults(fn=cmd_verificar)
    ar = sp.add_parser("arriendo"); ar.add_argument("--equipo"); ar.add_argument("--capacidad")
    ar.add_argument("--horas"); ar.add_argument("--plazo"); ar.add_argument("--con-atipicos", action="store_true")
    ar.add_argument("--limite", type=int, default=60); ar.set_defaults(fn=cmd_arriendo)
    mo = sp.add_parser("mo"); mo.add_argument("--cargo"); mo.add_argument("--especialidad")
    mo.add_argument("--zona"); mo.set_defaults(fn=cmd_mo)
    ca = sp.add_parser("cargar"); ca.add_argument("--dataset", required=True, choices=list(DATASETS))
    ca.add_argument("--archivo", required=True); ca.add_argument("--proyecto", required=True)
    ca.add_argument("--fuente", required=True); ca.set_defaults(fn=cmd_cargar)
    du = sp.add_parser("duplicados"); du.add_argument("--archivo"); du.add_argument("--stdin", action="store_true")
    du.set_defaults(fn=cmd_duplicados)
    s = sp.add_parser("pendientes-sync"); s.add_argument("--archivo", required=True); s.set_defaults(fn=cmd_pendientes)
    a = p.parse_args()
    if a.cmd in ("agregar", "duplicados") and not (a.archivo or a.stdin):
        p.error("%s necesita --archivo o --stdin" % a.cmd)
    if a.cmd in ("buscar", "historial", "resumen", "verificar") and not os.path.exists(F_COT) \
            and not any(os.path.exists(v[0]) for v in DATASETS.values()):
        print(json.dumps({"cotizaciones": [], "busquedas_sin_precio": []}) if a.cmd == "buscar"
              else json.dumps([]) if a.cmd == "historial" else json.dumps({"total_filas": 0}))
        return
    a.fn(a)


if __name__ == "__main__":
    main()
