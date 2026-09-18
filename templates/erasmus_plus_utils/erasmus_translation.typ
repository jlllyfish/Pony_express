// WARNING : le caractere <'> (simple guillement) n'est pas toléré pour l'instant, 
// en cas d'erreur de traduction assurez vous de remplacer <'> par <’> (apostrophe)

#let translations = (

  // Identity informations
  "Nom": "Name",
  "Nom complet": "Full name",
  "Prénom": "Firstname",
  "Adresse": "Address",
  "Adresse mail": "Email",
  "Téléphone": "Phone number",

  // A B C
  "Accompagnateurs": "Accompanying persons",
  "Acquis d’apprentissage": "Learning outcomes",
  "Année scolaire": "School year",
  "Agent": "Agent",
  "08 – Agriculture, forestry, fisheries and veterinary" : "",
  "Apprenant": "Learner",
  "attestation de stage" : "traineeship certificate",
  "Contexte d’apprentissage": "Learning context",
  "Coordonnées des contacts": "Contact Information",

  // D E F G H I
  "Date de début": "Start date",
  "Date de fin": "End date",
  "Date et lieu": "Date and place",
  "Disposition supplémentaires": "Additional provisions",
  "Enseignement et formation professionnels": "Vocational education and training",
  "entretien": "interview",
  "Évaluation des acquis d’apprentissage": "Evaluation of des learning acquis outcomes",
  "Information sur la mobilité à des fins d’apprentissage": "Information about the learning mobility",

  // L M N O
  "Modalités de suivi et de tutorat": "Mentoring and monitoring arrangements",
  "Moins de 250 employés": "Less than 250 employees",
  "Niveau dans le Cadre Européen des Certifications": "Level in the European Qualifications Framework",
  "Nom de l'organisme": "Organism name",
  "Objectifs du contrat pédagogique": "Purpose of the learning agreement",
  "Organisme d’accueil": "Receiving organisation",
  "Organisme d’envoi": "Sending organisation",

  // P Q
  "Participant": "Participant",
  "Participant à la mobilité à des fins d’apprentissage": "Participant in the learning mobility",
  "Parties prenantes au contrat pédagogique": "Parties to the learning agreement",
  "Pays, Ville": "Country, Town",
  "Personnel": "Staff",
  "Personne responsable dans l’organisme d’envoi": "Supervisor at the sending organisation",
  "Personnes responsables au sein de l’organisme d’envoi": "Supervisors at the sending organisation",
  "Personne responsable dans l’organisme d’accueil": "Supervisor at the receiving organisation",
  "Personnes responsables au sein de l’organisme d’accueil": "Supervisors at the hosting organisation",
  "Plus de 250 employés": "More than 250 employees",
  "Programme d’apprentissage et tâches": "Learning program and tasks",
  "rapport final": "final report",

  // R S T
  "Format et procédures d’évaluation": "Assessment format and procedures",
  "Critères d’évaluation": "Assessment criteria",
  "Lieu du retour": "Place of return",
  "Conditions du retour": "Conditions of return",
  "Reconnaissance des acquis d’apprentissage": "Recognition of learning outcomes",
  "Réintégration dans l’organisme d’envoi": "Reintégration at the sending organisation",
  "Responsabilités": "Responsabilities",
  "Responsable organisme d’accueil": "Receiving organisation contact",
  "Responsable organisme d’envoi": "Sending organisation contact",
  "Rôle": "Role",
  "Secteur": "Field",
  "Signatures": "Signatures",
  "Signature": "Signature",
  "Signatures avant le départ": "Signatures before mobility",
  "Signatures après la mobilité" : "Signatures after mobility",
  "Statut au sein de l'organisme d'envoi": "Position in the sending organisation",
  "Suivi et tutorat du participant durant l’activité": "Monitoring and support during the activity",
  "Titre qualification / profession": "Title of the qualification /profession",
  "Tuteur légal": "Legal guardian",
  "Tuteur légal 1": "Legal guardian 1",
  "Tuteur légal 2": "Legal guardian 2",
  "Type d’activité":"Activity type",
)

// cf : https://github.com/typst/typst/issues/2196#issuecomment-1728135476
#let to-string(it) = {
  if type(it) == str {
    it
  } else if type(it) != content {
    str(it)
  } else if it.has("text") {
    it.text
  } else if it.has("children") {
    it.children.map(to-string).join()
  } else if it.has("body") {
    to-string(it.body)
  } else if it == [ ] {
    " "
  }
}

#let missing_translation = "missing translation"

#let translate(data) = {
  let string = to-string(data)
  if translations.keys().contains(string) {
    return translations.at(string)
  } else {
    return [#metadata(string)<missing-translation>#text(red, "missing translation : " + string)]
  }
}

#let is_translatable(data) = {
  let string = to-string(data)
  return translations.keys().contains(string)
}
