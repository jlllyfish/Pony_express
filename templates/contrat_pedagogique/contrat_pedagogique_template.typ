#import "../erasmus_plus_utils/erasmus_plus_template_utils.typ" : * 

// taille des paragraphes d'introduction (FR + traduction) sous les titres
#let intro(body) = text(size: 8pt, body)

#let contrat_pedagogique(
  code_projet: missing_data,
  type_activite: missing_data,
  annee_scolaire: missing_data,
  date_debut: missing_data,
  date_fin: missing_data,
  pays_ville: missing_data,
  acquis_list: (missing_data,),
  activites: (missing_data,),
  tutorings: (missing_data,),
  participant_nom : missing_data,
  participant_prenom : missing_data,
  participant_adresse: missing_data,
  participant_email: missing_data,
  participant_telephone: missing_data,
  participant_qualification: missing_data,
  participant_niveau_cerp: missing_data,
  tuteurs_legaux: (
    (nom: missing_data,
    prenom: missing_data,
    email: missing_data,
    telephone: missing_data,),
  ),
  organisation_envoi_nom: missing_data,
  organisation_envoi_adresse: missing_data,
  organisation_envoi_email: missing_data,
  organisation_envoi_telephone: missing_data,
  organisation_accueil_nom: missing_data,
  organisation_accueil_adresse: missing_data,
  organisation_accueil_email: missing_data,
  organisation_accueil_telephone: missing_data,
  personnel_qualification: missing_data,
  personnel_niveau_cerp: missing_data,
  responsables_accueil: (
    (nom: missing_data,
    prenom: missing_data,
    email: missing_data,
    telephone: missing_data,
    responsabilites: missing_data),
  ),
  responsables_envoi: (
    (nom: missing_data,
    prenom: missing_data,
    email: missing_data,
    telephone: missing_data,
    responsabilites: missing_data),
  ),
  accompagnants : (
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
    
    #intro[
    Ce contrat pédagogique définit les conditions et les acquis d’apprentissage attendus d’une mobilité à des fins d’apprentissage organisée dans le cadre du programme Erasmus+. Les parties prenantes à ce contrat doivent se conformer aux règles et aux standards de qualité du programme.

    _#englishStyling[This learning agreement defines the conditions and learning outcomes expected from a learning mobility organised as part of the Erasmus+ programme. The parties to this contract must comply with the programme’s rules and quality standards]_
    ]

]

= Information sur la mobilité à des fins d’apprentissage
#chap[
    
  #form((
    "Secteur": "Enseignement et formation professionnels",
    "Type d’activité":type_activite,
    "Pays, Ville":pays_ville,
    "Date de début":date_debut,
    "Date de fin":date_fin, 
  ))

]


= Parties prenantes au contrat pédagogique
#chap[
    
    #intro[
    Le contrat pédagogique est conclu entre le participant à la mobilité à des fins d’apprentissage, l’organisme d’envoi et l’organisme d’accueil. 
    
    _#englishStyling[The learning agreement is concluded between the participant in the learning mobility, the sending organisation and the hosting organisation.]_
    ]

]

= Participant à la mobilité à des fins d’apprentissage
#chap[

=== Participant
  #form((
      "Nom":participant_nom,
      "Prénom":participant_prenom,
      "Adresse":participant_adresse,
      "Adresse mail":participant_email,
      "Téléphone":participant_telephone,
    )
  )
  
#let index = 1
#for guardian in tuteurs_legaux {
  
  let displayed_index = if tuteurs_legaux.len() == 1 {""} else {index} 
  if tuteurs_legaux.len() == 1 [=== Tuteur légal] else [=== Tuteur légal #index]
  form((
      "Nom":guardian.nom,
      "Prénom" :guardian.prenom,
      "Adresse mail":guardian.email,
      "Téléphone":guardian.telephone
    ))
  index = index + 1

}
]

== Organisme d’envoi
#chap[

  #form((
        "Nom de l'organisme":organisation_envoi_nom,
        "Adresse":organisation_envoi_adresse,
        "Adresse mail":organisation_envoi_email,
        "Téléphone":organisation_envoi_telephone
      ))
]

== Organisme d’accueil
#chap[
  
  #form((
        "Nom de l'organisme":organisation_accueil_nom,
        "Adresse":organisation_accueil_adresse,
        "Adresse mail":organisation_accueil_email,
        "Téléphone":organisation_accueil_telephone
      )
    )
]

= Contexte d’apprentissage
#chap[

  #intro[
  Au sein de l’organisme d’envoi, le participant est actuellement inscrit à :
  
  #englishStyling[At the sending organisation, the participant is currently enrolled in :]
  ]

  === Apprenant
  #form((
    "Titre qualification / profession": participant_qualification,
    "Année scolaire": annee_scolaire,
    "Niveau dans le Cadre Européen des Certifications": participant_niveau_cerp
  ),wide_title: true)

  #intro[
  Au sein de l’organisme d’envoi, le participant occupe actuellement la fonction de :
  
  #englishStyling[At the sending organisation, the participant is currently working in the following capacity :]
  ]

  === Personnel
  #form((
    "Titre qualification / profession":personnel_qualification,
    "Année scolaire":annee_scolaire,
    "Niveau dans le Cadre Européen des Certifications":personnel_niveau_cerp
  ),wide_title: true)

]
= Acquis d’apprentissage
#chap[

  #intro[
  Les parties ont convenu que les acquis d’apprentissage suivants devraient être atteints au cours de la mobilité à des fins d’apprentissage :
  
  _#englishStyling[The parties have agreed that the following learning outcomes should be achieved during the learning mobility :]_
  ]

  #for acquis in acquis_list {
    [- #acquis]
  }

]
  
= Programme d’apprentissage et tâches

#chap[
  #intro[
  Pour atteindre les acquis d’apprentissage convenus, le participant réalisera les activités et tâches suivantes au cours de son activité de mobilité.
  
  _#englishStyling[To achieve the agreed learning outcomes, the participant will complete the following activities and tasks during their mobility activity.]_
  ]
    
  #for activity in activites {
    [- #activity]
  }
]

= Suivi et tutorat du participant durant l’activité

== Personnes responsables au sein de l’organisme d’accueil

#chap[

  #intro[
  La (les) personne(s) suivante(s) de l’organisme d’accueil est (sont) chargée(s) de présenter au participant ses activités et ses tâches au sein de l’organisme d’accueil, de lui fournir un soutien pratique, de suivre ses progrès d’apprentissage, de l’aider à atteindre les acquis d’apprentissage attendus et de l’aider à s’intégrer dans lesroutines quotidiennes et le contexte social de l’organisme d’accueil. 
  
  _#englishStyling[The following person(s) at the hosting organisation are tasked with introducing the participant to their activities and tasks at the hosting organisation, providing practical support, monitoring their learning progress, supporting them to achieve the expected learning outcomes, and helping them to integrate into the daily routines and the social context at the hosting organisation.]_
  ]

  #forms(responsables_accueil.map(personne => (
    "Nom": personne.nom,
    "Prénom":personne.prenom,
    "Adresse mail":personne.email,
    "Téléphone":personne.telephone,
    "Responsabilités":personne.responsabilites,
  )))

]


== Personnes responsables au sein de l’organisme d’envoi

#chap[
  #intro[
  La (les) personne(s) suivante(s) de l’organisme d’envoi est (sont) chargée(s) de suivre les progrès des participants et de fournir un contenu ou un soutien pratique de la part de l’organisme d’envoi.
  
  #englishStyling[The following person(s) at the sending organisation are tasked with following the participants' progress and providing content or practical support from the side of the sending organisation.]
  ]

  #forms(responsables_envoi.map(personne => (
    "Nom": personne.nom,
    "Prénom":personne.prenom,
    "Adresse mail":personne.email,
    "Téléphone":personne.telephone,
    "Responsabilités":personne.responsabilites,
  )))
]

= Accompagnateurs

#chap[

  #intro[
  La ou les personnes suivantes accompagneront le participant pendant sa période de mobilité.
  
  #englishStyling[The following person(s) will accompany the participant during their mobility period]
  ]

  #forms(accompagnants.map(personne => (
    "Nom": personne.nom,
    "Prénom":personne.prenom,
    "Adresse mail":personne.email,
    "Téléphone":personne.telephone,
    "Responsabilités":personne.responsabilites,
  )))
]

== Modalités de suivi et de tutorat

#chap[

    #for tutoring in tutorings {
      [- #tutoring]
    }
  
]

= Évaluation des acquis d’apprentissage

= Reconnaissance des acquis d’apprentissage

= Réintégration dans l’organisme d’envoi

= Disposition supplémentaires

= Signatures

#chap[
  #intro[
  Les signataires confirment qu’ils ont compris et approuvent le contenu de cet accord.
  
  #englishStyling[The signatories confirm that they understood and approve the content of this agreement.]
  ]

  #let signatures_dict = (
    "Organisme d’envoi": organisation_envoi_nom,
    "Organisme d’accueil": organisation_envoi_nom
  )
  
  #let index = 1
  #for tuteur in tuteurs_legaux {
     signatures_dict.insert("Tuteur légal", tuteur.nom + " " + tuteur.prenom)
    index = index + 1
  }
  #signatures_dict.insert("Participant", participant_nom + " " + participant_prenom )

  #signatures(signatures_dict)
]

]
