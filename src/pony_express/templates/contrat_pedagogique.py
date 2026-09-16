import os
from copy import deepcopy
from enum import Enum

from pony_express.service.grist import not_in_grist
from pony_express.service.ponyexpress import generate_pdf_from_grist
from pony_express.service.utils import get_date_from_timestamp, concat_values
from slugify import slugify

# Access informations to the Grist Data
GRIST_SERVER = os.environ['GRIST_SERVER']
GRIST_TEAM_SITE = os.environ['GRIST_TEAM_SITE']
GRIST_DOC_ID = os.environ['GRIST_DOC_ID']
GRIST_TABLE = os.environ['GRIST_TABLE']
GRIST_PDF_COLUMN = None

# Access information to the TYPST template
TEMPLATE_NAME = "contrat_pedagogique"
TEMPLATE_FILENAME = "contrat_pedagogique_template"
TEMPLATE_FOLDERNAME = "contrat_pedagogique"


"""
Definition of all the information required by the PDF
the name of the enum must be the name of the Typst parameter (ex: start_date)
the value of the enum must be the name of the column in Grist (ex: ref_champs_date_debut_activite_hors_jours_de_voyage)
"""
class STUDENT_DATA(Enum):
  code_projet = not_in_grist('code_projet')  # MISSING
  type_activite = "ref_champs_indiquer_le_type_de_mobilite"
  annee_scolaire = not_in_grist("annee_scolaire")  # MISSING
  date_debut = "ref_champs_date_debut_activite_hors_jours_de_voyage"
  date_fin = "ref_champs_date_fin_activite_hors_jours_de_voyage"
  pays_ville = "ref_champs_pays_d_accueil"
  acquis_1 = "Acquis_1"
  acquis_2 = "Acquis_2"
  acquis_3 = "Acquis_3"
  acquis_list = not_in_grist("acquis_list") #Computed from others data
  activite_1 = "Activite_1"
  activite_2 = "Activite_2"
  activite_3 = "Activite_3"
  activites = not_in_grist("activities") #Computed from others data
  tutoring_1 = "Ref_table_tutorat_et_suivi_de_cette_activite_1"
  tutoring_2 = "Ref_table_tutorat_et_suivi_de_cette_activite_2"
  tutoring_3 = "Ref_table_tutorat_et_suivi_de_cette_activite_3"
  tutorings = not_in_grist("tutorings") #Computed from others data
  participant_nom = "nom_participant"
  participant_prenom = "prenom_s_participant"
  participant_adresse = "adresse_participant"
  participant_email = "mail_participant"
  participant_telephone = "telephone_participant"
  participant_qualification = not_in_grist("participant_qualification") # MISSING
  participant_niveau_cerp = not_in_grist("participant_niveau_cerp") # MISSING
  tuteur_1_nom = "Nom Parent -tuteur légal 1"
  tuteur_1_prenom = "Prénom Parent -tuteur légal 1"
  tuteur_1_email = "Mail Parent -tuteur légal 1"
  tuteur_1_telephone = "Téléphone Parent -tuteur légal 1"
  tuteur_2_nom = "Nom Parent -tuteur légal 2"
  tuteur_2_prenom = "Prénom Parent -tuteur légal 2"
  tuteur_2_email = "Mail Parent -tuteur légal 2"
  tuteur_2_telephone = "Téléphone Parent -tuteur légal 2"
  tuteurs_legaux = not_in_grist("tuteurs_legaux") #Computed from others data
  organisation_envoi_nom = not_in_grist("organisation_envoi_nom")  # MISSING
  organisation_envoi_adresse = not_in_grist("organisation_envoi_adresse")  # MISSING
  organisation_envoi_email = not_in_grist("organisation_envoi_email") # MISSING
  organisation_envoi_telephone = not_in_grist("organisation_envoi_telephone") # MISSING
  organisation_accueil_nom = not_in_grist("organisation_accueil_nom") # MISSING
  organisation_accueil_adresse = not_in_grist("organisation_accueil_adresse") # MISSING
  organisation_accueil_email = not_in_grist("organisation_accueil_email") # MISSING
  organisation_accueil_telephone = not_in_grist("organisation_accueil_telephone") # MISSING
  personnel_qualification = not_in_grist("personnel_qualification") # MISSING
  personnel_niveau_cerp = not_in_grist("personnel_niveau_cerp") # MISSING
  responsables_accueil = not_in_grist("responsables_accueil") # MISSING
  responsables_envoi = not_in_grist("responsables_envoi") # MISSING
  accompagnants = not_in_grist("accompagnants") # MISSING

"""
Return true if all lines from the table must be exported and treated
Add condition if any must be omitted
"""
def should_be_exported(record: dict) -> bool:
    return True
    if 'status' in record:
        return record['status'] == "instruction"
    else:
        return False

def name_pdf(record) -> str:
    return slugify(record[STUDENT_DATA.participant_nom.name]+"_pedagogique")


"""
Can be used to add any treatment of the data exported from grist
for instance, date format, address validation etc...
"""
def apply_data_transformation(data: dict) -> dict:
    transformed_dict = deepcopy(data)
    transformed_dict[STUDENT_DATA.date_debut.name] = get_date_from_timestamp(data[STUDENT_DATA.date_debut.name])
    transformed_dict[STUDENT_DATA.date_fin.name] = get_date_from_timestamp(data[STUDENT_DATA.date_fin.name])
    transformed_dict[STUDENT_DATA.activites.name] = concat_values(data, [STUDENT_DATA.activite_1.name, STUDENT_DATA.activite_2.name,STUDENT_DATA.activite_3.name])
    transformed_dict[STUDENT_DATA.tuteurs_legaux.name] = get_guardians(data)
    transformed_dict[STUDENT_DATA.acquis_list.name] = concat_values(data, [STUDENT_DATA.acquis_1.name, STUDENT_DATA.acquis_2.name, STUDENT_DATA.acquis_3.name])
    transformed_dict[STUDENT_DATA.tutorings.name] = concat_values(data, [STUDENT_DATA.tutoring_1.name, STUDENT_DATA.tutoring_2.name, STUDENT_DATA.tutoring_3.name])
    transformed_dict[STUDENT_DATA.accompagnants.name] = get_accompagnants(data)
    transformed_dict[STUDENT_DATA.responsables_envoi.name] = get_responsables_envoi(data)
    transformed_dict[STUDENT_DATA.responsables_accueil.name] = get_responsables_accueil(data)
    return transformed_dict


def get_accompagnants(data: dict) -> list[dict]:
    return [{'nom': "",
        'prenom': "",
        'email': "",
        'telephone': "",
        'responsabilites': ""}]

def get_responsables_envoi(data: dict) -> list[dict]:
    return [{'nom': "",
        'prenom': "",
        'email': "",
        'telephone': "",
        'responsabilites': ""}]

def get_responsables_accueil(data: dict) -> list[dict]:
    return [{'nom': "",
        'prenom': "",
        'email': "",
        'telephone': "",
        'responsabilites': ""}]



def get_guardians(data: dict) -> list[dict]:
    guardians = []
    if data[STUDENT_DATA.tuteur_1_nom.name]:
        guardians.append({
            "nom": data[STUDENT_DATA.tuteur_1_nom.name],
            "prenom": data[STUDENT_DATA.tuteur_1_prenom.name],
            "email": data[STUDENT_DATA.tuteur_1_email.name],
            "telephone": data[STUDENT_DATA.tuteur_1_telephone.name]
        })
    if data[STUDENT_DATA.tuteur_2_nom.name]:
        guardians.append({
            "nom": data[STUDENT_DATA.tuteur_2_nom.name],
            "prenom": data[STUDENT_DATA.tuteur_2_prenom.name],
            "email": data[STUDENT_DATA.tuteur_2_email.name],
            "telephone": data[STUDENT_DATA.tuteur_2_telephone.name]
        })
    return guardians

if __name__ == '__main__':
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
