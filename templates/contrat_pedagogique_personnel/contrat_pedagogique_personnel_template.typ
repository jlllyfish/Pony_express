#import "../erasmus_plus_utils/erasmus_plus_editorial.typ" : * 

#let contrat_pedagogique_personnel(
  participant_nom: missing_data,
  participant_prenom: missing_data,
  participant_statut: missing_data,
  participant_mail: missing_data,
  participant_telephone: missing_data, 
  organisme_accueil: missing_data,
  organisme_accueil_pays: missing_data,
  organisme_accueil_ville: missing_data,
  organisme_accueil_adresse: missing_data,
  organisme_accueil_email: missing_data,
  organisme_accueil_telephone: missing_data,
  organisme_envoi_responsable_nom: missing_data,
  organisme_accueil_responsable_nom: missing_data,
  acquis_list: (missing_data,),
  activites: (missing_data,),
  tutorings: (missing_data,),
  responsables_envoi: (
    (nom: missing_data,
    prenom: missing_data,
    email: missing_data,
    telephone: missing_data,
    responsabilites: missing_data),
  ),
  responsables_accueil: (
    (nom: missing_data,
    prenom: missing_data,
    email: missing_data,
    telephone: missing_data,
    responsabilites: missing_data),
  ),
  ..superfluous_arguments
) = [

#show: doc => erasmus_plus_layout(
  title:[CONTRAT PÉDAGOGIQUE ERASMUS+], 
  translation: "ERASMUS+ learning agreement",
  doc
)

= Objectifs du contrat pédagogique

#chap[

  Ce contrat pédagogique définit les conditions et les acquis d’apprentissage attendus d’une mobilité à des fins d’apprentissage organisée dans le cadre du programme Erasmus+. Les parties prenantes à ce contrat doivent se conformer aux règles et aux standards de qualité du programme.

  _#englishStyling[This learning agreement defines the conditions and learning outcomes expected from a learning mobility organised as part of the Erasmus+ programme. The parties to this contract must comply with the programme’s rules and quality standards]_

]
= Information sur la mobilité à des fins d’apprentissage

=== Agent
#chap[
  #form(( 
      "Statut au sein de l'organisme d'envoi": custom_data(participant_statut),
  ))
]

=== Organisme d’accueil
#chap[

  #form((
      "Organisme d’accueil" : custom_data(organisme_accueil),
      "Pays, Ville" : [#custom_data(organisme_accueil_pays) , #custom_data(organisme_accueil_ville)],
      "Adresse": custom_data(organisme_accueil_adresse),
      "Adresse mail": custom_data(organisme_accueil_email),
      "Téléphone": custom_data(organisme_accueil_telephone)
  
    ), wide_title: true)

]

#pagebreak()

= Acquis d’apprentissage
#chap[
      Les parties ont convenu que les acquis d’apprentissage suivants devraient être atteints au cours de la mobilité à des fins d’apprentissage :
      
      #englishStyling[The parties have agreed that the following learning outcomes should be achieved during the learning mobility :]

    #for acquis in acquis_list {

      unbreakable({
        [- #custom_data(acquis)]
        }
      )
    }
]

 
= Programme d’apprentissage et tâches

#chap[
    Pour atteindre les acquis d’apprentissage convenus, le participant réalisera les activités et tâches suivantes au cours de son activité de mobilité.
    
    #englishStyling[To achieve the agreed learning outcomes, the participant will complete the following activities and tasks during their mobility activity.]

    #for activity in activites {
      [- #custom_data(activity)]
    }
]

= Modalités de suivi et de tutorat

#chap[

    Afin de permettre un suivi de qualité lors de la période de mobilité, les modalités suivantes seront mises en place

    #for tutoring in tutorings {
      [- #custom_data(tutoring)]
    }
]

= Coordonnées des contacts 

=== Participant
#chap[

#form(( 
      "Nom complet": [#custom_data(participant_nom) #custom_data(participant_prenom)],
      "Adresse mail": custom_data(participant_mail),
      "Téléphone": custom_data(participant_telephone)
  ))
]

=== Personne responsable dans l’organisme d’envoi
#chap[
#for responsable in responsables_envoi {
form(( 
      "Nom complet": [#custom_data(responsable.nom) #custom_data(responsable.prenom)],
      "Rôle": custom_data(responsable.responsabilites),
      "Adresse mail": custom_data(responsable.email),
      "Téléphone": custom_data(responsable.telephone)
  ))
}
]
=== Personne responsable dans l’organisme d’accueil
#chap[
#for responsable in responsables_accueil {
form(( 
      "Nom complet": [#custom_data(responsable.nom) #custom_data(responsable.prenom)],
      "Rôle": custom_data(responsable.responsabilites),
      "Adresse mail": custom_data(responsable.email),
      "Téléphone": custom_data(responsable.telephone)
  ))
}
]

#pagebreak()
= Signatures avant le départ

#chap(
signatures((
    "Responsable organisme d’accueil": custom_data(organisme_envoi_responsable_nom),
    "Responsable organisme d’envoi": custom_data(organisme_accueil_responsable_nom),
    "Participant": custom_data(participant_nom),
))
)

#pagebreak()
= Signatures après la mobilité

#chap[
Après la mobilité : la signature de l’organisme d'envoi ou de l’organisme d'accueil est obligatoire.

_#englishStyling[Après la mobilité : la signature de l’organisme d'envoi ou de l’organisme d'accueil est obligatoire.]_

#signatures((
    "Responsable organisme d’accueil": custom_data(organisme_envoi_responsable_nom),
    "Responsable organisme d’envoi": custom_data(organisme_accueil_responsable_nom),
    "Participant": custom_data(participant_nom),
))
]
]

