#import "erasmus_translation.typ" : * 

#set text(font: "marianne")
#let blue_line =  line(length: 100%, stroke: (paint: rgb("#333399")))
#let black_line =  line(length: 85%, stroke: (paint: black))

// taille des numeros de titres (1, 2...) et de sous-titres (le 2 de 4.2)
#let heading_number_size = 20pt
#let subheading_number_size = 17pt

#let missing_data = "[donnée manquante]"

#let custom_data(it) = if (it == missing_data) {
  text(red, it)
} else {
  text(blue, it)
}

#let chap(it) = block(inset: (left: 12%), it) 

#let englishStyling(english) = {
  text(gray, [#english])
}

#let unbreakable(content) = {
  block(
    breakable: false,
    content
  )
}

#let conditionnal_content(test_mode, it) = {
  if test_mode {
    text(weight: "bold", grey, "Ce contenu apparait en mode test seulement et ne s'appliquerait pas en production" + linebreak())
    text(grey, it)
  } else {
    it
  }
}

///////////
// Forms //
///////////

#let form_item(title, value, activate_translation: true, wide_title:false) = {
  set par( 
    justify: false,
    spacing: 0.65em)

  let width = 30%
  if wide_title {width = 40%}

  let cells = ([*#title*], value)
  if activate_translation{
    cells.push(englishStyling(translate(title)))
    if (is_translatable(value)) {
      cells.push(englishStyling([_#translate(value)_]))
    }
  }

  {
    blue_line
    grid(
      columns: (width, 100%-width),
      gutter: 8pt,
      ..cells
    )
  }
}

#let form(fields, activate_translation: true, wide_title: false) = {
  block(
    breakable: false,
    inset: 5pt,
    {
      for key in fields.keys() { 
        form_item(
          key, 
          fields.at(key),
          activate_translation: activate_translation, 
          wide_title: wide_title)
      }
    }
  )
  
}

// plusieurs fiches a la suite (personnes) : meme espacement qu'entre les lignes d'une fiche
#let forms(items, activate_translation: true, wide_title: false) = block(
  inset: 5pt,
  for fields in items {
    block(breakable: false, spacing: 0.65em,
      for key in fields.keys() {
        form_item(key, fields.at(key),
          activate_translation: activate_translation, wide_title: wide_title)
      })
  })

////////////////
// Signatures //
////////////////

#let signature(title, name, activate_translation: true, wide_title: true) = {
  box(fill: rgb("#e5e5e5"), outset:(x: 6pt, y: 6pt),
  [
    === #title
    #form((
        "Nom" : custom_data(name),
        "Date et lieu":"",
        "Signature":"",
        
    ),
      activate_translation: activate_translation,
      wide_title: wide_title
    )]
  )
}

#let signatures(signataires, activate_translation: true) = {
  let signatures_list = ()
  for key in signataires.keys() { 
    signatures_list.push(signature(
      key, 
      signataires.at(key), 
      activate_translation: activate_translation
      )
    )
  }
  grid(columns: (1fr, 1fr), 
  gutter: 20pt,
  ..signatures_list
  )
}

#let erasmus_title(title, translation: "") = {

    text(16pt, strong(title)) 

    if translation != "" {
      [\ ] + englishStyling(strong[#text(16pt, translation)])
    }
  }

////////////
// Layout //
////////////

#let erasmus_plus_layout(title: "", translation: "", activate_translation: true, header_note: none, doc) = {
  set text(font: "Marianne")
  
  let moow_logo = image("assets/header_logo.png",
  alt: "Move occitanie over the world by ENSFEA")

  let erasmus_logo = image("assets/footer_logo.png",
    alt: "Erasmus +, enrichit les vies, ouvre les esprits. Financé par l'Union Européenne",)

  let header = {
    grid(
      columns: (1fr, 3fr),
      gutter: 1em,
      moow_logo,
      erasmus_logo
    )
    black_line
    if header_note != none {
      v(-0.4em)
      align(right, text(9pt, header_note))
    }
        align(center, erasmus_title(title, translation: translation))
  }

  set document(
    title: [#title],
    author: "MOOW By ENSFEA",
  )

  set page(
    numbering: "- 1/1 -",
    margin: (top: 150pt, right: 15%),
    header-ascent: 15%,
    header: {header},
  )

  set heading(numbering: "1.1")

  show heading.where(level: 1): it => {

    let titleBlock = {
      text(15pt, it.body) 
      if (activate_translation) {
        linebreak()
        englishStyling(text(13pt, translate(it.body)))
      }
    }

    pad(y: 10pt,
      grid(
        columns: (1fr, 9fr),
        column-gutter: 10pt,
        align(right, text(heading_number_size, counter(heading).display())),
        align(horizon, titleBlock), 
    ))
  }

  show heading.where(level: 2): it => {
    let titleBlock = {
      text(15pt, it.body) 
      if (activate_translation) {
        linebreak()
        englishStyling(text(13pt, translate(it.body)))
      }
    }

    let heading_counter = counter(heading).get()
    let level1 = [#text(heading_number_size, weight: "bold", [#heading_counter.at(0)])]
    let level2 = [#text(subheading_number_size, weight: "bold", [#heading_counter.at(1)])]

    pad(y: 10pt,
      grid(
        columns: (1fr, 9fr),
        column-gutter: 10pt,
        align(right, text(heading_number_size, [#level1.#level2])),
        align(horizon, titleBlock), 
      )  
    )
  }

  show heading.where(level: 3): it => {
    strong(it.body)
    
    if (activate_translation) {
    let translation = translate(it)

    if (translation != to-string(it.body)){
      linebreak()
      englishStyling[#translation]
    }    
    }
  }

  // un titre ne reste jamais seul en bas de page (regle placee apres les autres : appliquee en premier)
  show heading: it => block(sticky: true, it)

  set par(
    justify: true,
  )

  doc
}

}

