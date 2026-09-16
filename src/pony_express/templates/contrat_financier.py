import os
from copy import deepcopy
from enum import Enum
from pony_express.service.grist import not_in_grist
from pony_express.service.utils import get_date_from_timestamp
from pony_express.service.ponyexpress import generate_pdf_from_grist
from slugify import slugify


# Access informations to the Grist Data
# https://grist.numerique.gouv.fr/o/pony-express/3a8bd9w2WHfb
GRIST_SERVER = os.environ['GRIST_SERVER']
GRIST_TEAM_SITE = os.environ['GRIST_TEAM_SITE']
GRIST_DOC_ID = os.environ['GRIST_DOC_ID']
GRIST_TABLE = os.environ['GRIST_TABLE']
GRIST_PDF_COLUMN = None #"contrat_financier_pdf_non_signe"

# Access information to the TYPST template
TEMPLATE_NAME = "contrat_financier"
TEMPLATE_FILENAME = "contrat_financier_template"
TEMPLATE_FOLDERNAME = "contrat_financier"

# Valeur a finir : https://mensuel.framapad.org/p/erasmus_plus_pony-ak33?lang=en

# Definition of all the information required by the PDF
# the name of the enum must be the name of the Typst parameter (ex: start_date)
# the value of the enum must be the name of the column in Grist (ex: ref_champs_date_debut_activite_hors_jours_de_voyage)
class PERSON_DATA(Enum):
    code_projet= not_in_grist("code_projet") #MISSING
    type_activite= not_in_grist("type_activite") #MISSING
    date_debut= not_in_grist("date_debut") #MISSING
    date_fin= not_in_grist("date_fin") #MISSING
    participant_nom_complet= not_in_grist("participant_nom_complet") # Computed from other data
    participant_nom = "nom_participant"
    participant_prenom = "prenom_s_participant"
    participant_date_naissance = "date_naissance"
    participant_adresse = "adresse_participant"
    participant_telephone = "telephone_participant"
    participant_email = "mail_participant"
    organisme_envoi_nom= not_in_grist("organisme_envoi_nom") #MISSING
    organisme_envoi_statut_juridique= not_in_grist("organisme_envoi_statut_juridique") #MISSING
    organisme_envoi_adresse= not_in_grist("organisme_envoi_adresse") #MISSING
    organisme_envoi_email= not_in_grist("organisme_envoi_email") #MISSING
    organisme_envoi_code= not_in_grist("organisme_envoi_code") #MISSING
    organisme_envoi_representant_nom_complet= not_in_grist("organisme_envoi_representant_nom_complet") #MISSING
    organisme_envoi_representant_fonction= not_in_grist("organisme_envoi_representant_fonction") #MISSING
    duree_voyage = "nombre_de_jours_de_voyage"
    duree_jours_bourse= not_in_grist("duree_jours_bourse") #MISSING
    valeur_bourse = "montant_bourse"
    frais_sejour= not_in_grist("frais_sejour") #MISSING
    frais_voyage= not_in_grist("frais_voyage")#MISSING
    limite_prolongation= not_in_grist("limite_prolongation") #MISSING
    accompte_pourcentage= not_in_grist("accompte_pourcentage") #MISSING
    option_prise_en_charge= not_in_grist("option_prise_en_charge") #MISSING // value can be one of  ["Option 1", "Option 2"]
    inclut_dans_contribution= not_in_grist("inclut_dans_contribution") #MISSING // value must be a sublist of sublist of ["frais_voyage" , "soutien_individuel" , "soutien_linguistique" , "frais_cours", "soutien_inclusion")
    montant_global= not_in_grist("montant_global") #MISSING
    montant_bourse= not_in_grist("montant_bourse") #MISSING
    autre_montant= not_in_grist("autre_montant") #MISSING
    compagnie_assurance= not_in_grist("compagnie_assurance") #MISSING
    numero_assurance= not_in_grist("numero_assurance") #MISSING
    police_assurance= not_in_grist("police_assurance") #MISSING

# Return true if all lines from the table must be exported and treated
# Add condition if any must be omitted
def should_be_exported(record) -> bool:
    return True

def name_pdf(record) -> str:
    return slugify(record[PERSON_DATA.participant_nom.name]+"_financier")

# Can be used to add any treatment of the data exported from grist
# for instance, date format, address validation etc...
def apply_data_transformation(dict) -> dict:
    transformed_dict = deepcopy(dict)
    transformed_dict[PERSON_DATA.participant_date_naissance.name] = get_date_from_timestamp(dict[PERSON_DATA.participant_date_naissance.name])
    transformed_dict[PERSON_DATA.participant_nom_complet.name] = dict[PERSON_DATA.participant_prenom.name] + " " + dict[PERSON_DATA.participant_nom.name]
    # le template attend un tableau : colonne Grist "Choice List" -> ["L", "frais_voyage", ...]
    contribution = dict[PERSON_DATA.inclut_dans_contribution.name]
    transformed_dict[PERSON_DATA.inclut_dans_contribution.name] = contribution[1:] if isinstance(contribution, list) else []
    return transformed_dict

if __name__ == '__main__':
    print("GENERATE CONTRAT FINANCIER")
    generate_pdf_from_grist(
        GRIST_DOC_ID,
        GRIST_TEAM_SITE,
        GRIST_TABLE,
        PERSON_DATA,
        TEMPLATE_FOLDERNAME,
        TEMPLATE_FILENAME,
        TEMPLATE_NAME,
        should_be_exported,
        apply_data_transformation,
        name_pdf,
        GRIST_SERVER,
        GRIST_PDF_COLUMN,
    )
