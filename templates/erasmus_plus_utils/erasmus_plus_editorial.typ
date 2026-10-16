// Mise en page « éditoriale » (variante 1) : typographie forte, filets fins, numéros en marge.
// Reprend l'API de erasmus_plus_template_utils.typ (form, forms, chap, signatures,
// erasmus_plus_layout...) : un template passe d'une mise en page à l'autre en changeant son import.
#import "erasmus_plus_template_utils.typ" : *

// ── Palette et réglages ──────────────────────────────────────────────
#let navy = rgb("#16235C")
#let jaune = rgb("#FFCC00")
#let gris = rgb("#7A8194")
#let filet = rgb("#D9DCE6")
#let encre = rgb("#1D2233")

#let num_col = 1.5cm          // colonne des numéros de titres (et retrait du corps)
#let label_col = 34%          // colonne des intitulés dans les fiches
#let label_col_wide = 42%

// ── Texte anglais ────────────────────────────────────────────────────
// gris seulement : les templates l'entourent parfois de _..._ (italique)
#let englishStyling(english) = text(fill: gris, english)
#let en(t) = text(fill: gris, style: "italic", t)
#let tr(t, activate: true) = if activate and is_translatable(t) { translate(t) } else { none }

// ── Corps de section ─────────────────────────────────────────────────
#let chap(it, level: 1) = block(width: 100%, inset: (left: num_col), it)

// ── Fiches ───────────────────────────────────────────────────────────
#let form_label(title, activate_translation) = {
  text(size: 8.5pt, weight: "bold", title)
  if activate_translation {
    linebreak()
    text(size: 7.5pt, en(translate(title)))
  }
}

#let form_value(value, activate_translation) = {
  value
  if activate_translation and is_translatable(value) {
    linebreak()
    en(translate(value))
  }
}

#let form_table(fields, activate_translation: true, wide_title: false) = {
  set par(justify: false)
  table(
  columns: (if wide_title { label_col_wide } else { label_col }, 1fr),
  column-gutter: 8pt,
  inset: (x: 0pt, y: 5pt),
  stroke: (x, y) => (bottom: 0.5pt + filet),
  ..fields.pairs().map(((key, value)) => (
    form_label(key, activate_translation),
    form_value(value, activate_translation),
  )).flatten(),
)}

#let form(fields, activate_translation: true, wide_title: false) = block(
  breakable: false, width: 100%, above: 6pt, below: 10pt,
  form_table(fields, activate_translation: activate_translation, wide_title: wide_title))

// intertitre d'une fiche : RÔLE en capitales + traduction
#let role_title(title, activate_translation: true) = {
  text(8pt, weight: "bold", fill: navy, tracking: 0.08em, upper(title))
  let t = tr(title, activate: activate_translation)
  if t != none { h(4pt); text(7.5pt, en(t)) }
}

// plusieurs fiches (personnes) : deux colonnes dès qu'il y en a plus d'une
// title_key : clé affichée en intertitre au-dessus de la fiche (et retirée du tableau)
#let forms(items, activate_translation: true, wide_title: false, title_key: none) = {
  let fiche(fields) = block(breakable: false, width: 100%, {
    if title_key != none and title_key in fields and fields.at(title_key) != "" {
      role_title(fields.at(title_key), activate_translation: activate_translation)
      v(-2pt)
    }
    let rest = (:)
    for (key, value) in fields.pairs() {
      if title_key == none or key != title_key { rest.insert(key, value) }
    }
    form_table(rest, activate_translation: activate_translation, wide_title: wide_title)
  })
  v(6pt)
  block(width: 100%, above: 0pt, below: 12pt,
    grid(columns: if items.len() > 1 { (1fr, 1fr) } else { (1fr,) },
      column-gutter: 16pt, row-gutter: 14pt,
      ..items.map(fiche)))
}

// ── Signatures ───────────────────────────────────────────────────────
#let signature_name(nom, prenom) = if nom in (missing_data, "") {
  missing_data
} else {
  text(weight: "bold", upper(nom)) + if prenom not in (missing_data, "") [ #prenom ]
}

#let signature(title, name, prenom: "", activate_translation: true) = block(
  breakable: false, width: 100%, height: 2.3cm,
  stroke: (left: 2pt + jaune), inset: (left: 10pt, y: 4pt), {
    text(8pt, weight: "bold", title)
    let t = tr(title, activate: activate_translation)
    if t != none { h(4pt); text(7pt, en(t)) }
    linebreak()
    text(9pt, signature_name(name, prenom))
    place(bottom + left, dy: -2pt, {
      line(length: 100%, stroke: 0.5pt + filet)
      v(-6pt)
      text(7pt, fill: gris)[Date, lieu et signature #if activate_translation [· #en(translate("Date, lieu et signature"))]]
    })
  })

// une cellule = ("Titre", "Nom", "Prénom") ; ou plusieurs signataires alternatifs, séparés par « ou » :
//   (("Tuteur légal 1", ...), ("Tuteur légal 2", ...))
#let signatures(cellules, activate_translation: true) = {
  let blocs = cellules.map(cellule => {
    if type(cellule.at(0)) == str {
      signature(cellule.at(0), cellule.at(1), prenom: cellule.at(2, default: ""),
        activate_translation: activate_translation)
    } else {
      stack(spacing: 6pt, ..cellule.map(s => signature(s.at(0), s.at(1), prenom: s.at(2, default: ""),
        activate_translation: activate_translation)).intersperse(text(8pt, fill: gris, "ou")))
    }
  })
  v(4pt)
  grid(columns: (1fr, 1fr), gutter: 12pt, ..blocs)
}

// ── Page de garde ────────────────────────────────────────────────────
// cles : ((intitulé, valeur), ...) — bandeau de chiffres clés (traductions par le dictionnaire)
#let couverture(kicker: "ERASMUS+", title: "", translation: "", participant: none,
                code: none, cles: (), activate_translation: true) = {
  box(fill: jaune, inset: (x: 6pt, y: 3pt),
    text(7.5pt, weight: "bold", fill: navy, tracking: 0.1em, kicker))
  v(6pt)
  text(27pt, weight: "bold", fill: navy, tracking: -0.02em, title)
  if translation != "" { v(-14pt); text(15pt, weight: "light", fill: gris, translation) }
  v(10pt)
  grid(columns: (1fr, auto), align: bottom,
    [#text(7.5pt, fill: gris, tracking: 0.1em, "PARTICIPANT·E") \ #text(17pt, weight: "medium", participant)],
    if code != none { text(8pt, fill: gris)[Code projet \ #text(fill: navy, weight: "bold", code)] })
  v(10pt)
  let cle((label, valeur)) = {
    text(7pt, fill: gris, tracking: 0.08em, upper(label))
    let t = tr(label, activate: activate_translation)
    if t != none { h(3pt); text(6.5pt, en(t)) }
    linebreak()
    v(-2pt)
    text(15pt, weight: "bold", fill: navy, valeur)
  }
  set par(justify: false)
  block(width: 100%, stroke: (top: 2pt + navy, bottom: 0.5pt + filet), inset: (y: 10pt), below: 14pt,
    grid(columns: (1.4fr,) + (1fr,) * calc.max(cles.len() - 1, 0), column-gutter: 12pt, ..cles.map(cle)))
}

// ── Mise en page ─────────────────────────────────────────────────────
#let erasmus_plus_layout(title: "", translation: "", activate_translation: true, header_note: none, doc) = {
  set text(font: "Marianne", size: 9.5pt, fill: encre)
  set par(leading: 0.55em, justify: true)
  set list(marker: text(fill: navy, "•"))

  set document(title: [#title], author: "MOOW By ENSFEA")

  set page(
    paper: "a4",
    margin: (x: 1.8cm, top: 3.1cm, bottom: 1.8cm),
    header: {
      grid(columns: (1fr, auto), align: (left + horizon, right + horizon),
        image("assets/header_logo.png", height: 1.15cm, alt: "Move occitanie over the world by ENSFEA"),
        image("assets/footer_logo.png", height: 0.75cm,
          alt: "Erasmus +, enrichit les vies, ouvre les esprits. Financé par l'Union Européenne"))
      v(-2pt)
      line(length: 100%, stroke: 0.5pt + filet)
    },
    footer: text(7.5pt, fill: gris)[
      #header_note #h(1fr) #title · #context counter(page).display("1/1", both: true)],
  )

  set heading(numbering: "1.1")

  show heading: set par(justify: false)
  show heading.where(level: 1): it => block(above: 16pt, below: 6pt, grid(
    columns: (num_col, 1fr),
    text(24pt, weight: "light", fill: navy, counter(heading).display()),
    {
      v(4pt)
      text(12.5pt, weight: "bold", fill: navy, it.body)
      let t = tr(it.body, activate: activate_translation)
      if t != none { h(6pt); text(9pt, en(t)) }
      v(-4pt)
      line(length: 100%, stroke: 1.2pt + navy)
    }))

  show heading.where(level: 2): it => block(above: 12pt, below: 8pt, inset: (left: num_col), {
    text(10pt, weight: "bold", fill: navy, counter(heading).display() + h(5pt) + it.body)
    let t = tr(it.body, activate: activate_translation)
    if t != none { h(5pt); text(8pt, en(t)) }
  })

  show heading.where(level: 3): it => block(above: 10pt, below: 2pt,
    role_title(it.body, activate_translation: activate_translation))

  // un titre ne reste jamais seul en bas de page (règle placée après les autres : appliquée en premier)
  show heading: it => block(sticky: true, it)

  doc
}
