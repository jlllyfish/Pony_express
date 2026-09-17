import os
from copy import deepcopy
from enum import Enum

from slugify import slugify

from pony_express.service.grist import GristService
from pony_express.service.ponyexpress import generate_pdf_from_grist
from pony_express.service.utils import clean_text, get_date_from_timestamp, group_blocks

# Accès au document Grist
GRIST_SERVER = os.environ["GRIST_SERVER"]
GRIST_TEAM_SITE = os.environ["GRIST_TEAM_SITE"]
GRIST_DOC_ID = os.environ["GRIST_DOC_ID"]
GRIST_TABLE = os.environ[
    "GRIST_TABLE"
]  # table principale (ex : Demarche_128447_annotations)
GRIST_PDF_COLUMN = None

# Template Typst
TEMPLATE_NAME = "contrat_pedagogique"
TEMPLATE_FILENAME = "contrat_pedagogique_template"
TEMPLATE_FOLDERNAME = "contrat_pedagogique"

# Tables OTP de la démarche, toutes reliées par le numéro de dossier
DEMARCHE = "128447"
TABLE_CHAMPS = f"Demarche_{DEMARCHE}_champs"
TABLE_ACQUIS = f"Demarche_{DEMARCHE}_repetable_acquis_d_apprentissage"
TABLE_ACTIVITES = f"Demarche_{DEMARCHE}_repetable_activites_et_taches"
TABLE_ACCOMPAGNATEURS = (
    f"Demarche_{DEMARCHE}_repetable_information_personnelle_accompagnateur"
)
BLOCK_KEY = "dossier_number"  # numéro de dossier dans les tables de blocs
BLOCK_ORDER = "block_row_index"  # ordre des blocs


# =====================================================================
# RUBRIQUES : {paramètre du template Typst : colonne Grist}
# Un paramètre déclaré nulle part s'affiche « [donnée manquante] ».
# =====================================================================

# Table principale (GRIST_TABLE)
PRINCIPALE = {
    "numero_dossier": "dossier_number",  # relie toutes les autres tables
    "code_projet": "code_projet",
    "participant_nom": "nom_participant",
    "participant_prenom": "prenom_s_participant",
    "participant_adresse": "adresse_participant",
    "participant_email": "mail_participant",
    "participant_telephone": "telephone_participant",
    "tuteur_1_nom": "nom_parent_tuteur_legal_1",
    "tuteur_1_prenom": "prenom_parent_tuteur_legal_1",
    "tuteur_1_email": "mail_parent_tuteur_legal_1",
    "tuteur_1_telephone": "telephone_parent_tuteur_legal_1",
    "tuteur_2_nom": "nom_parent_tuteur_legal_2",
    "tuteur_2_prenom": "prenom_parent_tuteur_legal_2",
    "tuteur_2_email": "mail_parent_tuteur_legal_2",
    "tuteur_2_telephone": "telephone_parent_tuteur_legal_2",
}

# Tables jointes : une ligne par dossier
JOINTES = {
    TABLE_CHAMPS: {
        "type_activite": "mobilite_apprenant",
        "date_debut": "date_debut_activite_hors_jours_de_voyage",
        "date_fin": "date_fin_activite_hors_jours_de_voyage",
        "pays": "pays_d_accueil",
        "ville": "ville_pays_d_accueil",
    },
}

# Blocs répétables : plusieurs lignes par dossier
#   paramètre: (table, "colonne")              -> liste de textes
#   paramètre: (table, {champ: "colonne"})     -> liste de fiches
BLOCS = {
    "acquis_list": (TABLE_ACQUIS, "acquis"),
    "activites": (TABLE_ACTIVITES, "activite"),
    "tutorings": (TABLE_ACTIVITES, "tutorat_et_suivi_de_cette_activite"),
    "accompagnants": (
        TABLE_ACCOMPAGNATEURS,
        {
            "nom": "nom",
            "prenom": "prenom",
            "email": "adresse_electronique",
            "telephone": "numero_de_telephone",
            "responsabilites": "fonction",
        },
    ),
}

# Tuteurs légaux : une fiche par tuteur dont le nom est renseigné
TUTEURS = [
    {
        "nom": "tuteur_1_nom",
        "prenom": "tuteur_1_prenom",
        "email": "tuteur_1_email",
        "telephone": "tuteur_1_telephone",
    },
    {
        "nom": "tuteur_2_nom",
        "prenom": "tuteur_2_prenom",
        "email": "tuteur_2_email",
        "telephone": "tuteur_2_telephone",
    },
]

# Calculés dans apply_data_transformation : pays_ville, tuteurs_legaux
# Pas encore dans Grist (-> « [donnée manquante] ») :
#   annee_scolaire, participant_qualification, participant_niveau_cerp,
#   organisation_envoi_nom / _adresse / _email / _telephone,
#   organisation_accueil_nom / _adresse / _email / _telephone,
#   personnel_qualification, personnel_niveau_cerp,
#   responsables_envoi, responsables_accueil


# =====================================================================
# Construction automatique (rien à modifier ici pour le mapping)
# =====================================================================


def build_enum(name: str, principale: dict, jointes: dict) -> Enum:
    """Enum attendue par PonyExpress : nom = paramètre Typst, valeur = colonne ou "Table.colonne"."""
    members = dict(principale)
    for table, columns in jointes.items():
        for param, column in columns.items():
            if param in members:
                raise ValueError(f"Paramètre déclaré deux fois : {param}")
            members[param] = f"{table}.{column}"
    return Enum(name, members, module=__name__)


def build_extra_tables(blocs: dict) -> dict:
    """Colonnes attendues dans chaque table de blocs (contrôlées par check_mapping.py)."""
    tables = {}
    for table, columns in blocs.values():
        expected = tables.setdefault(table, [BLOCK_KEY, BLOCK_ORDER])
        for column in [columns] if isinstance(columns, str) else columns.values():
            if column not in expected:
                expected.append(column)
    return tables


STUDENT_DATA = build_enum("STUDENT_DATA", PRINCIPALE, JOINTES)
EXTRA_TABLES = build_extra_tables(BLOCS)


def should_be_exported(record: dict) -> bool:
    """True si la ligne doit produire un PDF (ajouter ici un filtre, ex : statut)."""
    return True


def name_pdf(record) -> str:
    return slugify(
        f"{record['participant_nom']}_{record['participant_prenom']}_{record['id']}_pedagogique"
    )


def apply_data_transformation(data: dict) -> dict:
    transformed = deepcopy(data)
    set_date(transformed, "date_debut")
    set_date(transformed, "date_fin")
    set_joined(transformed, "pays_ville", [value(data, "pays"), value(data, "ville")])
    set_people(
        transformed, "tuteurs_legaux", [data] * len(TUTEURS), TUTEURS, required="nom"
    )
    transformed.setdefault(
        "tuteurs_legaux", []
    )  # aucun tuteur (majeur) : pas de rubrique

    dossier = data.get("numero_dossier")
    for param, (table, columns) in BLOCS.items():
        blocks = get_blocks(table, dossier)
        if isinstance(columns, str):
            set_list(transformed, param, [block.get(columns) for block in blocks])
        else:
            set_people(transformed, param, blocks, columns)
    return transformed


# =====================================================================
# Outils
# =====================================================================

_blocks_cache: dict[str, dict] = {}


def fetch_table(table: str) -> list[dict]:
    """Lit une table Grist entière (remplacée par check_mapping.py en mode hors-ligne)."""
    return GristService(GRIST_DOC_ID, GRIST_TEAM_SITE, GRIST_SERVER).get_table_records(
        table
    )


def get_blocks(table: str, dossier_number) -> list[dict]:
    """Blocs répétables d'un dossier, dans l'ordre. Chaque table n'est lue qu'une fois."""
    if table not in _blocks_cache:
        _blocks_cache[table] = group_blocks(fetch_table(table), BLOCK_KEY, BLOCK_ORDER)
    try:
        return _blocks_cache[table].get(int(dossier_number), [])
    except (TypeError, ValueError):
        return []


def value(row: dict, key: str) -> str:
    """Texte nettoyé ; "" si la colonne est vide ou introuvable."""
    text = clean_text(row.get(key))
    return "" if text.endswith(" is not in GRIST") else text


def set_date(data: dict, key: str) -> None:
    """Date au format jj-mm-aa ; si absente ou illisible : [donnée manquante]."""
    try:
        data[key] = get_date_from_timestamp(data[key])
    except (KeyError, TypeError, ValueError):
        data.pop(key, None)


def set_joined(data: dict, key: str, values: list, separator: str = ", ") -> None:
    """Assemble les valeurs renseignées ("Espagne, Madrid") ; si aucune : [donnée manquante]."""
    parts = [part for part in values if part]
    if parts:
        data[key] = separator.join(parts)
    else:
        data.pop(key, None)


def set_list(data: dict, key: str, values: list) -> None:
    """Liste de textes non vides ; si elle est vide : [donnée manquante]."""
    values = [clean_text(v) for v in values if clean_text(v)]
    if values:
        data[key] = values
    else:
        data.pop(key, None)


def set_people(
    data: dict, key: str, rows: list[dict], columns, required: str | None = None
) -> None:
    """
    Une fiche par ligne : {champ du template : colonne}.
    `columns` : un dictionnaire commun à toutes les lignes, ou une liste (un par ligne).
    Fiche ignorée si elle est vide (ou si le champ `required` est vide). Aucune fiche : [donnée manquante].
    """
    mappings = columns if isinstance(columns, list) else [columns] * len(rows)
    people = [
        {field: value(row, column) for field, column in mapping.items()}
        for row, mapping in zip(rows, mappings)
    ]
    people = [p for p in people if (p[required] if required else any(p.values()))]
    if people:
        data[key] = people
    else:
        data.pop(key, None)


if __name__ == "__main__":
    print("GENERATE CONTRATS PEDAGOGIQUES")
    generate_pdf_from_grist(
        GRIST_DOC_ID,
        GRIST_TEAM_SITE,
        GRIST_TABLE,
        STUDENT_DATA,
        TEMPLATE_FOLDERNAME,
        TEMPLATE_FILENAME,
        TEMPLATE_NAME,
        should_be_exported,
        apply_data_transformation,
        name_pdf,
        GRIST_SERVER,
        GRIST_PDF_COLUMN,
    )
