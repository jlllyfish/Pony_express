import os
from copy import deepcopy
from enum import Enum

from slugify import slugify

from pony_express.service.grist import GristService, not_in_grist
from pony_express.service.ponyexpress import generate_pdf_from_grist
from pony_express.service.utils import clean_text, get_date_from_timestamp, group_blocks

# Access informations to the Grist Data
GRIST_SERVER = os.environ["GRIST_SERVER"]
GRIST_TEAM_SITE = os.environ["GRIST_TEAM_SITE"]
GRIST_DOC_ID = os.environ["GRIST_DOC_ID"]
GRIST_TABLE = os.environ["GRIST_TABLE"]
GRIST_PDF_COLUMN = None

# Access information to the TYPST template
TEMPLATE_NAME = "contrat_pedagogique"
TEMPLATE_FILENAME = "contrat_pedagogique_template"
TEMPLATE_FOLDERNAME = "contrat_pedagogique"

# Tables OTP de la démarche, reliées à la table principale par le numéro de dossier
DEMARCHE = "128447"
TABLE_CHAMPS = f"Demarche_{DEMARCHE}_champs"
TABLE_ACQUIS = f"Demarche_{DEMARCHE}_repetable_acquis_d_apprentissage"
TABLE_ACTIVITES = f"Demarche_{DEMARCHE}_repetable_activites_et_taches"
TABLE_ACCOMPAGNATEURS = f"Demarche_{DEMARCHE}_repetable_information_personnelle_accompagnateur"
BLOCK_KEY = "dossier_number"  # numéro de dossier dans les tables de blocs
BLOCK_ORDER = "block_row_index"  # ordre des blocs
# colonnes attendues dans chaque table (contrôlées par check_mapping.py)
EXTRA_TABLES = {
    TABLE_ACQUIS: [BLOCK_KEY, BLOCK_ORDER, "acquis"],
    TABLE_ACTIVITES: [
        BLOCK_KEY,
        BLOCK_ORDER,
        "activite",
        "tutorat_et_suivi_de_cette_activite",
    ],
    TABLE_ACCOMPAGNATEURS: [BLOCK_KEY, BLOCK_ORDER, "nom", "prenom", "adresse_electronique",
                            "numero_de_telephone", "fonction"],
}

# champ du PDF -> colonne de TABLE_ACCOMPAGNATEURS
ACCOMPAGNATEUR_COLUMNS = {
    "nom": "nom",
    "prenom": "prenom",
    "email": "adresse_electronique",
    "telephone": "numero_de_telephone",
    "responsabilites": "fonction",
}


"""
Definition of all the information required by the PDF
the name of the enum must be the name of the Typst parameter (ex: start_date)
the value of the enum must be the name of the column in Grist (ex: ref_champs_date_debut_activite_hors_jours_de_voyage)
or "Table.colonne" for a column of another table joined on dossier_number (ex: f"{TABLE_CHAMPS}.pays_d_accueil")
"""


class STUDENT_DATA(Enum):
    numero_dossier = "dossier_number"  # colonne de la table principale qui relie aux blocs répétables
    code_projet = "code_projet"
    type_activite = f"{TABLE_CHAMPS}.mobilite_apprenant"
    annee_scolaire = not_in_grist("annee_scolaire")  # MISSING
    date_debut = f"{TABLE_CHAMPS}.date_debut_activite_hors_jours_de_voyage"
    date_fin = f"{TABLE_CHAMPS}.date_fin_activite_hors_jours_de_voyage"
    pays_ville = f"{TABLE_CHAMPS}.pays_d_accueil"
    acquis_list = not_in_grist("acquis_list")  # calculé depuis TABLE_ACQUIS
    activites = not_in_grist("activites")  # calculé depuis TABLE_ACTIVITES
    tutorings = not_in_grist("tutorings")  # calculé depuis TABLE_ACTIVITES
    participant_nom = "nom_participant"
    participant_prenom = "prenom_s_participant"
    participant_adresse = "adresse_participant"
    participant_email = "mail_participant"
    participant_telephone = "telephone_participant"
    participant_qualification = not_in_grist("participant_qualification")  # MISSING
    participant_niveau_cerp = not_in_grist("participant_niveau_cerp")  # MISSING
    tuteur_1_nom = "nom_parent_tuteur_legal_1"
    tuteur_1_prenom = "prenom_parent_tuteur_legal_1"
    tuteur_1_email = "mail_parent_tuteur_legal_1"
    tuteur_1_telephone = "telephone_parent_tuteur_legal_1"
    tuteur_2_nom = "nom_parent_tuteur_legal_2"
    tuteur_2_prenom = "prenom_parent_tuteur_legal_2"
    tuteur_2_email = "mail_parent_tuteur_legal_2"
    tuteur_2_telephone = "telephone_parent_tuteur_legal_2"
    tuteurs_legaux = not_in_grist("tuteurs_legaux")  # Computed from others data
    organisation_envoi_nom = not_in_grist("organisation_envoi_nom")  # MISSING
    organisation_envoi_adresse = not_in_grist("organisation_envoi_adresse")  # MISSING
    organisation_envoi_email = not_in_grist("organisation_envoi_email")  # MISSING
    organisation_envoi_telephone = not_in_grist(
        "organisation_envoi_telephone"
    )  # MISSING
    organisation_accueil_nom = not_in_grist("organisation_accueil_nom")  # MISSING
    organisation_accueil_adresse = not_in_grist(
        "organisation_accueil_adresse"
    )  # MISSING
    organisation_accueil_email = not_in_grist("organisation_accueil_email")  # MISSING
    organisation_accueil_telephone = not_in_grist(
        "organisation_accueil_telephone"
    )  # MISSING
    personnel_qualification = not_in_grist("personnel_qualification")  # MISSING
    personnel_niveau_cerp = not_in_grist("personnel_niveau_cerp")  # MISSING
    responsables_accueil = not_in_grist("responsables_accueil")  # MISSING
    responsables_envoi = not_in_grist("responsables_envoi")  # MISSING
    accompagnants = not_in_grist("accompagnants")  # MISSING


"""
Return true if all lines from the table must be exported and treated
Add condition if any must be omitted
"""


def should_be_exported(record: dict) -> bool:
    return True
    if "status" in record:
        return record["status"] == "instruction"
    else:
        return False


def name_pdf(record) -> str:
    return slugify(
        f"{record[STUDENT_DATA.participant_nom.name]}_{record[STUDENT_DATA.participant_prenom.name]}_{record['id']}_pedagogique"
    )


"""
Can be used to add any treatment of the data exported from grist
for instance, date format, address validation etc...
"""


def apply_data_transformation(data: dict) -> dict:
    transformed_dict = deepcopy(data)
    set_date(transformed_dict, STUDENT_DATA.date_debut.name)
    set_date(transformed_dict, STUDENT_DATA.date_fin.name)
    transformed_dict[STUDENT_DATA.tuteurs_legaux.name] = get_guardians(data)

    dossier = data[STUDENT_DATA.numero_dossier.name]
    acquis = get_blocks(TABLE_ACQUIS, dossier)
    activites = get_blocks(TABLE_ACTIVITES, dossier)
    set_list(
        transformed_dict,
        STUDENT_DATA.acquis_list.name,
        [b.get("acquis") for b in acquis],
    )
    set_list(
        transformed_dict,
        STUDENT_DATA.activites.name,
        [b.get("activite") for b in activites],
    )
    set_list(
        transformed_dict,
        STUDENT_DATA.tutorings.name,
        [b.get("tutorat_et_suivi_de_cette_activite") for b in activites],
    )
    set_people(transformed_dict, STUDENT_DATA.accompagnants.name,
               get_blocks(TABLE_ACCOMPAGNATEURS, data[STUDENT_DATA.numero_dossier.name]),
               ACCOMPAGNATEUR_COLUMNS)
    transformed_dict[STUDENT_DATA.responsables_envoi.name] = get_responsables_envoi(
        data
    )
    transformed_dict[STUDENT_DATA.responsables_accueil.name] = get_responsables_accueil(
        data
    )
    return transformed_dict


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


def set_date(data: dict, key: str) -> None:
    """Date au format jj-mm-aa ; si absente ou illisible, le template affiche [donnée manquante]."""
    try:
        data[key] = get_date_from_timestamp(data[key])
    except (KeyError, TypeError, ValueError):
        data.pop(key, None)


def set_list(data: dict, key: str, values: list) -> None:
    """Liste nettoyée ; si elle est vide, le template affiche [donnée manquante]."""
    values = [clean_text(v) for v in values if clean_text(v)]
    if values:
        data[key] = values
    else:
        data.pop(key, None)


def set_people(data: dict, key: str, blocks: list[dict], columns: dict[str, str]) -> None:
    """Une fiche par bloc (champ du PDF -> colonne Grist) ; sans bloc : [donnee manquante]."""
    people = [{field: clean_text(block.get(column)) for field, column in columns.items()} for block in blocks]
    people = [person for person in people if any(person.values())]
    if people:
        data[key] = people
    else:
        data.pop(key, None)

def get_responsables_envoi(data: dict) -> list[dict]:
    return [
        {"nom": "", "prenom": "", "email": "", "telephone": "", "responsabilites": ""}
    ]


def get_responsables_accueil(data: dict) -> list[dict]:
    return [
        {"nom": "", "prenom": "", "email": "", "telephone": "", "responsabilites": ""}
    ]


def get_guardians(data: dict) -> list[dict]:
    guardians = []
    if data[STUDENT_DATA.tuteur_1_nom.name]:
        guardians.append(
            {
                "nom": data[STUDENT_DATA.tuteur_1_nom.name],
                "prenom": data[STUDENT_DATA.tuteur_1_prenom.name],
                "email": data[STUDENT_DATA.tuteur_1_email.name],
                "telephone": data[STUDENT_DATA.tuteur_1_telephone.name],
            }
        )
    if data[STUDENT_DATA.tuteur_2_nom.name]:
        guardians.append(
            {
                "nom": data[STUDENT_DATA.tuteur_2_nom.name],
                "prenom": data[STUDENT_DATA.tuteur_2_prenom.name],
                "email": data[STUDENT_DATA.tuteur_2_email.name],
                "telephone": data[STUDENT_DATA.tuteur_2_telephone.name],
            }
        )
    return guardians


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
