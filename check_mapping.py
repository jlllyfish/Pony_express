"""
Vérifie le mapping Grist -> Typst d'une config PonyExpress, puis (option) génère les PDF.

Usage :
    poetry run python check_mapping.py contrat_pedagogique
    poetry run python check_mapping.py contrat_pedagogique --compile --limit 3
    poetry run python check_mapping.py contrat_financier --records exemple.json --compile

--records : CSV ou JSON de la table principale (ID de colonnes Grist) pour tester sans Grist.
--table NOM=FICHIER : en hors-ligne, contenu (CSV ou JSON) d'une table annexe (EXTRA_TABLES).
Rien n'est jamais renvoyé vers Grist.
"""
import argparse
import csv
import difflib
import importlib
import io
import json
import os
import re
import subprocess
import sys
import traceback
from enum import Enum, EnumType
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
OUT_DIR = ROOT / "generated" / "_check"
NOT_IN_GRIST = " is not in GRIST"

if os.name == "nt":
    os.system("")  # active les couleurs ANSI dans la console Windows
sys.stdout.reconfigure(encoding="utf-8")

ok = lambda m: print(f"  \033[32m✔\033[0m {m}")
warn = lambda m: print(f"  \033[33m⚠\033[0m {m}")
err = lambda m: print(f"  \033[31m✘\033[0m {m}")
title = lambda m: print(f"\n\033[1m{m}\033[0m")
errors = 0


def fail(m):
    global errors
    errors += 1
    err(m)


# ---------------------------------------------------------------- Typst
def typst_params(typ_file: Path, func: str) -> tuple[dict[str, str], bool]:
    """{paramètre: valeur par défaut} de `#let func(...)`, + présence d'un `..sink`."""
    src = typ_file.read_text(encoding="utf-8")
    m = re.search(rf"#let\s+{re.escape(func)}\s*\(", src)
    if not m:
        raise ValueError(f"'#let {func}(' introuvable dans {typ_file}")
    i, depth, buf, parts, in_str = m.end(), 1, "", [], False
    while depth:
        c = src[i]
        if c == '"' and src[i - 1] != "\\":
            in_str = not in_str
        if not in_str:
            if src.startswith("//", i):  # commentaire : ignoré jusqu'à la fin de ligne
                i = src.find("\n", i)
                continue
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            if c == "," and depth == 1:
                parts.append(buf); buf = ""; i += 1; continue
        if depth:
            buf += c
        i += 1
    parts.append(buf)
    params, sink = {}, False
    for p in (p.strip() for p in parts):
        if not p or p.startswith("//"):
            continue
        if p.startswith(".."):
            sink = True
        else:
            name, _, default = p.partition(":")
            params[name.strip()] = default.strip()
    return params, sink


# ---------------------------------------------------------------- Helpers
def load_file(path: Path) -> list[dict]:
    """Lignes d'un export CSV (Grist / tableur) ou d'un JSON."""
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8-sig")
    dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))


def find_enum(mod) -> EnumType:
    enums = [v for v in vars(mod).values()
             if isinstance(v, EnumType) and issubclass(v, Enum) and v is not Enum
             and v.__module__ == mod.__name__]
    if len(enums) != 1:
        raise SystemExit(f"1 Enum attendue dans le module, trouvé : {[e.__name__ for e in enums]}")
    return enums[0]


def map_record(raw: dict, enum) -> dict:
    """Réplique exacte de GristService.get_grist_data."""
    data = {"id": raw["id"]}
    for item in enum:
        data[item.name] = raw[item.value] if item.value in raw else item.name + NOT_IN_GRIST
    return data


def walk(value, path=""):
    """Itère (chemin, valeur scalaire) dans une structure imbriquée."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for n, v in enumerate(value):
            yield from walk(v, f"{path}[{n}]")
    else:
        yield path, value


# ---------------------------------------------------------------- Main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="nom du module dans src/pony_express/templates (ex: contrat_pedagogique)")
    ap.add_argument("--records", help="JSON de lignes Grist (mode hors-ligne)")
    ap.add_argument("--limit", type=int, default=5, help="nb de lignes testées (défaut 5, 0 = toutes)")
    ap.add_argument("--table", action="append", default=[], metavar="NOM=FICHIER",
                    help="hors-ligne : contenu CSV/JSON d'une table annexe (répétable)")
    ap.add_argument("--compile", action="store_true", help="génère les .typ et PDF dans generated/_check/")
    args = ap.parse_args()

    if args.records:  # les modules lisent os.environ à l'import
        for k in ("GRIST_SERVER", "GRIST_TEAM_SITE", "GRIST_DOC_ID", "GRIST_TABLE"):
            os.environ.setdefault(k, "offline")
    else:
        missing = [k for k in ("GRIST_API_KEY", "GRIST_TEAM_SITE", "GRIST_DOC_ID", "GRIST_TABLE")
                   if not os.environ.get(k)]
        if missing:
            raise SystemExit(f"Variables d'environnement manquantes : {', '.join(missing)}")

    try:
        mod = importlib.import_module(f"pony_express.templates.{args.config}")
    except KeyError as e:
        raise SystemExit(f"Variable d'environnement manquante lue par le module : {e}")
    enum = find_enum(mod)
    typ_file = TEMPLATES / mod.TEMPLATE_FOLDERNAME / f"{mod.TEMPLATE_FILENAME}.typ"

    # 1. Enum ------------------------------------------------------------
    title(f"1. Enum {enum.__name__} ({len(enum.__members__)} entrées)")
    aliases = [n for n, m in enum.__members__.items() if m.name != n]
    if aliases:
        fail(f"Valeurs dupliquées -> entrées ignorées par Python (alias) : {aliases}")
    else:
        ok("Aucune valeur dupliquée")
    mapped = [m for m in enum if not m.value.endswith(NOT_IN_GRIST)]
    unmapped = [m.name for m in enum if m.value.endswith(NOT_IN_GRIST)]
    print(f"  {len(mapped)} mappées sur une colonne, {len(unmapped)} marquées not_in_grist")

    # 2. Typst -----------------------------------------------------------
    title(f"2. Template {typ_file.relative_to(ROOT)} -> #{mod.TEMPLATE_NAME}()")
    params, sink = typst_params(typ_file, mod.TEMPLATE_NAME)
    print(f"  {len(params)} paramètres déclarés{' + ..sink' if sink else ''}")
    extra = [m.name for m in enum if m.name not in params]
    if extra:
        (warn if sink else fail)(
            f"Clés de l'Enum absentes du template ({'ignorées silencieusement' if sink else 'erreur Typst'}) : {extra}")
    else:
        ok("Toutes les clés de l'Enum existent dans le template")

    # 3. Colonnes Grist -------------------------------------------------
    title("3. Colonnes Grist")
    if args.records:
        raw_records = load_file(Path(args.records))
        col_ids = set().union(*(r.keys() for r in raw_records)) - {"id"}
        labels = {}
        print(f"  (hors-ligne : colonnes déduites de {args.records})")
    else:
        from pony_express.service.grist import GristService
        svc = GristService(mod.GRIST_DOC_ID, mod.GRIST_TEAM_SITE, mod.GRIST_SERVER)
        st, cols = svc.grist.list_cols(mod.GRIST_TABLE, hidden=True)
        if st != 200:
            raise SystemExit(f"list_cols -> HTTP {st} : {cols}")
        col_ids = {c["id"] for c in cols}
        labels = {c["fields"].get("label", ""): c["id"] for c in cols}
        st, raw_records = svc.grist.list_records(mod.GRIST_TABLE)
        if st != 200:
            raise SystemExit(f"list_records -> HTTP {st} : {raw_records}")
    print(f"  {len(col_ids)} colonnes, {len(raw_records)} lignes")
    bad = 0
    for m in mapped:
        if m.value in col_ids:
            continue
        bad += 1
        hint = ""
        if m.value in labels:
            hint = f" -> c'est un LIBELLÉ, l'ID est '{labels[m.value]}'"
        else:
            close = difflib.get_close_matches(m.value, list(col_ids), n=2, cutoff=0.6)
            if close:
                hint = f" -> proche de : {close}"
        fail(f"{m.name} = '{m.value}' : colonne introuvable{hint}")
    if not bad:
        ok("Toutes les colonnes mappées existent")

    # 3b. Tables annexes (blocs répétables) ------------------------------
    extra_tables = getattr(mod, "EXTRA_TABLES", {})
    if extra_tables:
        title("3b. Tables annexes")
        offline_tables = {}
        for spec in args.table:
            name, _, path = spec.partition("=")
            offline_tables[name] = load_file(Path(path))
        for table, required in extra_tables.items():
            if args.records:
                rows = offline_tables.get(table)
                if rows is None:
                    warn(f"{table} : pas de --table fourni -> considérée vide")
                    rows = []
                cols = set().union(*(r.keys() for r in rows)) if rows else set(required)
            else:
                st, info = svc.grist.list_cols(table, hidden=True)
                if st != 200:
                    fail(f"{table} : table introuvable (HTTP {st})")
                    continue
                cols = {c["id"] for c in info}
                rows = svc.get_table_records(table)
            absent = [c for c in required if c not in cols]
            if absent:
                fail(f"{table} : colonnes introuvables {absent}"
                     + "".join(f" (proche de {difflib.get_close_matches(a, list(cols), n=1)})" for a in absent
                               if difflib.get_close_matches(a, list(cols), n=1)))
            else:
                key = getattr(mod, "BLOCK_KEY", None)
                nb = len({r.get(key) for r in rows}) if key else "?"
                ok(f"{table} : {len(rows)} lignes, {nb} dossiers")
            if args.records and hasattr(mod, "fetch_table"):
                offline_tables.setdefault(table, rows)
        if args.records and hasattr(mod, "fetch_table"):
            mod.fetch_table = lambda t: offline_tables.get(t, [])

    # 4. Données transformées -------------------------------------------
    title("4. Lignes exportées + apply_data_transformation")
    exported = [r for r in raw_records if mod.should_be_exported(r)]
    print(f"  {len(exported)}/{len(raw_records)} lignes retenues par should_be_exported")
    sample = exported if args.limit == 0 else exported[:args.limit]
    from pony_express.service.pdf import to_typst_string
    escapes = to_typst_string('"') != '"""'  # pdf.py échappe-t-il les guillemets ?
    names, results = {}, []
    for raw in sample:
        rid = raw["id"]
        data = map_record(raw, enum)
        try:
            t = mod.apply_data_transformation(data)
            pdf_name = mod.name_pdf(t)
        except Exception as e:
            fr = traceback.extract_tb(e.__traceback__)[-1]
            fail(f"ligne {rid} : transformation en échec -> {type(e).__name__}: {e}")
            print(f"    {Path(fr.filename).name}:{fr.lineno}  {fr.line}")
            continue
        names.setdefault(pdf_name, []).append(rid)
        print(f"  ligne {rid} -> {pdf_name}.pdf")
        if not sink:
            for k in t:
                if k != "id" and k not in params:
                    fail(f"{k} inconnu du template (erreur Typst)")
        # seules les clés réellement lues par le template comptent
        used = {k: v for k, v in t.items() if k in params}
        for k, v in used.items():
            if params[k].startswith("(") and not isinstance(v, (list, tuple, dict)):
                fail(f"{k} : le template attend un tableau/dictionnaire, reçoit {type(v).__name__} {v!r:.40}")
            if isinstance(v, list) and v[:1] == ["L"]:
                fail(f"{k} : liste Grist brute ['L', ...] -> retirer le 'L' dans apply_data_transformation")
        empty, nones = [], []
        for path, v in walk(used):
            path = path[1:]
            if isinstance(v, str) and v.endswith(NOT_IN_GRIST):
                empty.append(path)
            elif v is None:
                nones.append(path)
            elif not escapes and isinstance(v, str) and ('"' in v or "\\" in v):
                fail(f"{path} contient \" \\ -> casse le .typ généré")
        if empty:
            warn(f"« xxx is not in GRIST » imprimé pour : {', '.join(empty)}")
        if nones:
            warn(f"« None » imprimé pour : {', '.join(nones)}")
        empty_lists = [k for k, d in params.items() if d.startswith("(") and not t.get(k)]
        if empty_lists:
            warn(f"« [donnée manquante] » imprimé pour les listes vides : {', '.join(empty_lists)}")
        not_given = [p for p in params if p not in t and p not in empty_lists]
        if not_given:
            print(f"    défauts du template utilisés : {', '.join(not_given)}")
        results.append((rid, pdf_name, t))
    for n, ids in names.items():
        if len(ids) > 1:
            fail(f"Nom de PDF '{n}' partagé par les lignes {ids} -> écrasement")

    # 5. Compilation -----------------------------------------------------
    if args.compile:
        title(f"5. Compilation Typst -> {OUT_DIR.relative_to(ROOT)}/")
        from pony_express.service.pdf import create_call_to_template_string
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        import_path = os.path.relpath(typ_file, OUT_DIR).replace(os.sep, "/")
        for rid, pdf_name, t in results:
            typ = OUT_DIR / f"{pdf_name}.typ"
            typ.write_text(f'#import "{import_path}": *\n'
                           + create_call_to_template_string(mod.TEMPLATE_NAME, t), encoding="utf-8")
            p = subprocess.run(["typst", "compile", "--root", str(ROOT), str(typ), "--font-path", str(TEMPLATES)],
                               capture_output=True, text=True, encoding="utf-8")
            if p.returncode == 0:
                ok(f"ligne {rid} -> {typ.with_suffix('.pdf').relative_to(ROOT)}")
            else:
                fail(f"ligne {rid} : typst en échec (.typ conservé : {typ.relative_to(ROOT)})")
                print("    " + "\n    ".join(l[:160] for l in p.stderr.strip().splitlines()[:6]))

    title("Résultat : " + ("OK" if not errors else f"{errors} erreur(s)"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
