#!/usr/bin/env python3
"""Deterministic Programmatic SEO Generator — Observatoire ADEME DPE & Artisans RGE France.

Pure Python 3 stdlib (zero dependencies). Reads data/villes_top100.json (authentic INSEE,
postal codes, departments, regions, populations, and official ADEME DPE aggregates) and generates:
  - index.html (National observatory + live client-side ADEME DPE & SIRENE RGE explorer)
  - villes/index.html (Searchable + region-filterable directory of 100 French cities)
  - villes/<slug>.html (100 city pages with real ADEME DPE stats, live explorer, JSON-LD)
  - sitemap.xml (102 URLs) & robots.txt
"""
from __future__ import annotations

import html
import json
from pathlib import Path

SITE_BASE = "https://yannabadie.github.io/observatoire-dpe-rge-france"
LASTMOD = "2026-11-21"
INDEXNOW_KEY = "f4c8e2a91b7d40369e5a2c8f1d6b3e90"
API_WORKER_URL = "https://eu-public-intelligence-worker.eu-us-opendata-worker.workers.dev"
FACTURKIT_URL = "https://yannabadie.github.io/facturkit-2027/"
FACTURKIT_METIERS_URL = "https://yannabadie.github.io/facturkit-2027/metiers/"
APIFY_PARTNER_URL = "https://apify.com/?fpr=zuvzfw"


def fmt_int(n: int) -> str:
    return f"{int(n):,}".replace(",", "\u202f")


def render_header(prefix: str) -> str:
    return f"""  <header class="site-header">
    <div class="container header-inner">
      <a class="brand-lockup" href="{prefix}index.html" aria-label="Observatoire DPE &amp; RGE France Accueil">
        <span class="brand-mark" aria-hidden="true">DPE</span>
        <span class="brand-text">
          <span class="brand-name">Observatoire DPE &amp; RGE</span>
          <span class="brand-sub">Open Data ADEME &amp; SIRENE · 100 Villes de France</span>
        </span>
      </a>
      <nav class="header-nav" aria-label="Navigation principale">
        <a class="nav-link" href="{prefix}index.html#explorateur-live">Explorateur Live</a>
        <a class="nav-link" href="{prefix}villes/index.html">100 Villes</a>
        <a class="nav-link" href="{prefix}index.html#calendrier-passoires">Loi Climat 2025–2034</a>
        <a class="nav-link" href="{FACTURKIT_METIERS_URL}" target="_blank" rel="noopener">Artisans Factur-X</a>
        <a class="btn-nav" href="{prefix}villes/index.html">Explorer les Villes</a>
      </nav>
    </div>
  </header>"""


def render_footer(prefix: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="container">
      <p>
        <strong>Observatoire DPE &amp; RGE France (Open Data)</strong> · Données officielles ADEME (<code>dpe03existant</code>), DINUM/INSEE SIRENE (<code>est_rge=true</code>) &amp; IGN/Etalab ·
        <a href="{prefix}index.html">Accueil</a> ·
        <a href="{prefix}villes/index.html">Annuaire 100 Villes</a> ·
        <a href="{prefix}sitemap.xml">Sitemap</a> ·
        <a href="{FACTURKIT_URL}" target="_blank" rel="noopener">FacturKit 2027 (BTP &amp; TPE)</a> ·
        <a href="{APIFY_PARTNER_URL}" target="_blank" rel="noopener noreferrer sponsored">Apify Open-Data</a>
      </p>
      <p class="disclosure">Portail informatif indépendant en accès libre (Licence Ouverte v2.0). Les données live sont interrogées directement depuis votre navigateur sur les APIs publiques officielles ADEME et DINUM sans intermédiaire payant. Certains liens partenaires peuvent inclure un suivi affilié transparent (<code>rel="sponsored"</code>) sans aucun surcoût.</p>
    </div>
  </footer>"""


def render_ecosystem_cta() -> str:
    return f"""        <div class="cta-dark">
          <div>
            <h3>Développeurs, PropTech &amp; Artisans RGE : automatisez vos données &amp; votre conformité</h3>
            <p>
              Intégrez nos données ADEME DPE (avec flag <code>isThermalSieve</code>) et BODACC via notre API JSON dédiée (<code>eu-public-intelligence-worker</code>), préparez votre conformité <strong>Factur-X 2026–2027</strong> (BTP / artisans RGE), ou automatisez vos extractions à grande échelle sur Apify.
            </p>
          </div>
          <div class="cta-actions">
            <a class="btn-teal" href="https://github.com/yannabadie/observatoire-dpe-rge-france#écosystème--apis-développeurs-associés" target="_blank" rel="noopener">API ADEME DPE &amp; Open-Data →</a>
            <a class="btn-white" href="{FACTURKIT_METIERS_URL}" target="_blank" rel="noopener">Artisans RGE : Guides Factur-X →</a>
            <a class="btn-white" href="{APIFY_PARTNER_URL}" target="_blank" rel="noopener noreferrer sponsored">Actors Open-Data Apify →</a>
          </div>
        </div>"""


def render_dpe_bars_html(counts: dict[str, int], total: int) -> str:
    rows = []
    for k in "ABCDEFG":
        val = int(counts.get(k, 0))
        pct = round((val / total) * 100.0, 1) if total > 0 else 0.0
        width = max(pct, 1.0 if val > 0 else 0.0)
        rows.append(
            f'          <div class="dpe-bar-row">'
            f'<span class="dpe-badge dpe-{k}">{k}</span>'
            f'<div class="bar-track"><div class="bar-fill dpe-{k}" style="width:{width:.1f}%"></div></div>'
            f'<div class="dpe-num">{fmt_int(val)} ({pct:.1f}&nbsp;%)</div>'
            f"</div>"
        )
    return "\n".join(rows)


def render_calendar_section() -> str:
    return """      <div class="calendar-grid">
        <div class="cal-box alert">
          <strong>1er janvier 2025 — EN VIGUEUR</strong>
          <p style="margin:6px 0 0;font-size:0.9rem;color:var(--ink-2);">Interdiction de mise en location (nouveaux baux et renouvellements) des logements classés <strong>G</strong> en France métropolitaine (Loi Climat &amp; Résilience) + gels des loyers F et G actifs depuis août 2022.</p>
        </div>
        <div class="cal-box soon">
          <strong>1er janvier 2028 — ÉCHÉANCE PROCHE</strong>
          <p style="margin:6px 0 0;font-size:0.9rem;color:var(--ink-2);">Extension de l'interdiction de location aux logements classés <strong>F</strong>. L'<strong>audit énergétique réglementaire</strong> est déjà obligatoire pour vendre une maison ou monopropriété classée <strong>E, F ou G</strong>.</p>
        </div>
        <div class="cal-box future">
          <strong>1er janvier 2034 — HORIZON LONG</strong>
          <p style="margin:6px 0 0;font-size:0.9rem;color:var(--ink-2);">Interdiction de location étendue à l'étiquette <strong>E</strong>. Anticiper via un artisan certifié <strong>RGE</strong> (Reconnu Garant de l'Environnement) conditionne l'accès à MaPrimeRénov', aux primes CEE et à l'Éco-PTZ (jusqu'à 50 000 €).</p>
        </div>
      </div>"""


def build_city_page(v: dict, siblings: list[dict]) -> str:
    slug = v["slug"]
    nom = v["nom"]
    nom_h = html.escape(nom)
    insee = v["insee"]
    cp = v["code_postal"]
    dept_code = v["code_departement"]
    dept_name = html.escape(v["departement"])
    region = html.escape(v["region"])
    pop = int(v["population"])
    snap = v["dpe_snapshot"]
    total_dpe = int(snap["total"])
    counts = snap["counts"]
    fg = int(snap["passoires_fg"])
    fg_pct = float(snap["passoires_pct"])
    ab = int(counts.get("A", 0)) + int(counts.get("B", 0))
    ab_pct = round((ab / total_dpe) * 100.0, 1) if total_dpe > 0 else 0.0
    ademe_qs = v["ademe_qs"]

    url = f"{SITE_BASE}/villes/{slug}.html"
    meta_desc = (
        f"Observatoire DPE ADEME à {nom} ({cp}, INSEE {insee}) : {fmt_int(total_dpe)} diagnostics analysés, "
        f"{fg_pct:.1f} % de passoires thermiques F/G ({fmt_int(fg)}), explorateur live par rue et annuaire officiel des artisans RGE."
    )

    faq_items = [
        {
            "@type": "Question",
            "name": f"Combien de passoires thermiques (DPE F et G) sont recensées à {nom} ({cp}) ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Selon la base officielle ADEME des DPE logements existants (instantané {LASTMOD}), {nom} ({dept_code}) compte {fmt_int(total_dpe)} diagnostics enregistrés, dont {fmt_int(fg)} logements classés F ou G, soit {fg_pct:.1f} % du parc diagnostiqué ({fmt_int(counts['F'])} en F et {fmt_int(counts['G'])} en G).",
            },
        },
        {
            "@type": "Question",
            "name": f"Comment vérifier gratuitement les artisans certifiés RGE à {nom} ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"L'explorateur live de cette page interroge directement l'API officielle Annuaire des Entreprises (DINUM/INSEE) filtrée sur est_rge=true pour le code postal {cp}. Vous pouvez aussi saisir un autre code postal de {nom} pour vérifier instantanément le SIREN et la certification RGE de votre prestataire avant signature.",
            },
        },
        {
            "@type": "Question",
            "name": f"Quelles aides de rénovation énergétique sont accessibles à {nom} ({v['region']}) en 2026 ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Les propriétaires occupants et bailleurs de {nom} peuvent mobiliser MaPrimeRénov' (parcours par geste ou rénovation d'ampleur), les Certificats d'Économies d'Énergie (CEE), l'Éco-PTZ jusqu'à 50 000 € à taux zéro et la TVA réduite à 5,5 %, sous réserve de faire appel à une entreprise titulaire du label RGE.",
            },
        },
    ]

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Observatoire DPE & RGE France", "item": f"{SITE_BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": "100 Villes de France", "item": f"{SITE_BASE}/villes/"},
                    {"@type": "ListItem", "position": 3, "name": f"{nom} ({cp})", "item": url},
                ],
            },
            {
                "@type": "Dataset",
                "name": f"Données DPE ADEME & Artisans RGE — {nom} ({cp}, INSEE {insee})",
                "description": meta_desc,
                "url": url,
                "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
                "spatialCoverage": f"{nom}, {v['departement']}, {v['region']}, France",
                "dateModified": LASTMOD,
                "creator": {"@type": "Organization", "name": "ADEME & DINUM/INSEE (Open Data)"},
            },
            {
                "@type": "FAQPage",
                "mainEntity": faq_items,
            },
        ],
    }

    sib_cards = []
    for s in siblings:
        ss = s["dpe_snapshot"]
        sib_cards.append(
            f'          <a class="city-card" href="./{s["slug"]}.html">'
            f'<strong>{html.escape(s["nom"])} ({s["code_postal"]})</strong>'
            f'<span class="meta">{html.escape(s["departement"])} · INSEE {s["insee"]}</span>'
            f'<div class="stats"><span>{fmt_int(ss["total"])} DPE</span><span style="color:#b91c1c;">{ss["passoires_pct"]:.1f} % F/G</span></div>'
            f"</a>"
        )

    faq_html = "\n".join(
        f'          <details><summary>{html.escape(q["name"])}</summary><p>{html.escape(q["acceptedAnswer"]["text"])}</p></details>'
        for q in faq_items
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DPE ADEME &amp; Artisans RGE à {nom_h} ({cp}) — Passoires Thermiques {LASTMOD[:4]}</title>
  <meta name="description" content="{html.escape(meta_desc)}">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="DPE ADEME &amp; Artisans RGE à {nom_h} ({cp})">
  <meta property="og:description" content="{html.escape(meta_desc)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <link rel="stylesheet" href="../assets/styles.css">
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body>
{render_header("../")}

  <main>
    <section class="hero">
      <div class="container">
        <div class="breadcrumb">
          <a href="../index.html">Observatoire DPE &amp; RGE</a> ›
          <a href="./index.html">100 Villes de France</a> ›
          {nom_h} ({cp})
        </div>
        <div class="eyebrow">INSEE {insee} · Code postal {cp} · {dept_name} ({dept_code}) · {region}</div>
        <h1>DPE ADEME, passoires thermiques F/G &amp; artisans RGE à {nom_h} ({cp})</h1>
        <p class="hero-lead">
          Analyse open-data officielle du parc de logements diagnostiqués à <strong>{nom_h}</strong> ({fmt_int(pop)} habitants) à partir de la base <strong>ADEME (<code>dpe03existant</code>)</strong> et de l'annuaire public <strong>DINUM/INSEE des entreprises certifiées RGE</strong>.
        </p>

        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-val">{fmt_int(total_dpe)}</span>
            <span class="kpi-label">DPE logements existants recensés (ADEME {LASTMOD})</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val warn">{fg_pct:.1f}&nbsp;% ({fmt_int(fg)})</span>
            <span class="kpi-label">Passoires thermiques F ({fmt_int(counts["F"])}) &amp; G ({fmt_int(counts["G"])})</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val ok">{ab_pct:.1f}&nbsp;% ({fmt_int(ab)})</span>
            <span class="kpi-label">Logements performants A ({fmt_int(counts["A"])}) &amp; B ({fmt_int(counts["B"])})</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val">{fmt_int(pop)}</span>
            <span class="kpi-label">Population municipale INSEE · {v["codes_postaux_count"]} code(s) postal(aux)</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="panel">
          <h2>Répartition officielle des étiquettes DPE (A à G) à {nom_h}</h2>
          <p class="section-sub">Instantané officiel calculé sur les diagnostics ADEME <code>dpe03existant</code> au {LASTMOD} (requête source : <code>{html.escape(ademe_qs)}</code>).</p>
          <div class="dpe-bars">
{render_dpe_bars_html(counts, total_dpe)}
          </div>
        </div>
      </div>
    </section>

    <section id="explorateur-live" class="section section-alt">
      <div class="container">
        <div id="dpe-rge-explorer" class="panel" data-cp="{cp}" data-ademe-qs="{html.escape(ademe_qs)}" data-mode="city">
          <h2>Explorateur LIVE ADEME DPE &amp; Artisans RGE à {nom_h}</h2>
          <p class="section-sub">Interrogation directe depuis votre navigateur (0 € backend) des derniers diagnostics ADEME à {nom_h} et des entreprises certifiées RGE locales (API officielle DINUM/INSEE).</p>

          <form id="exp-form" class="live-controls">
            <div class="field">
              <label for="exp-cp">Code postal (modifiez pour un arrondissement / quartier)</label>
              <input id="exp-cp" type="text" inputmode="numeric" maxlength="5" value="{cp}" placeholder="{cp}">
            </div>
            <div class="field">
              <label for="exp-dpe-filter">Filtre étiquette DPE</label>
              <select id="exp-dpe-filter">
                <option value="all">Toutes les étiquettes (A–G)</option>
                <option value="FG">Passoires thermiques uniquement (F &amp; G)</option>
                <option value="G">Classe G (interdite location depuis 2025)</option>
                <option value="F">Classe F (échéance 2028)</option>
                <option value="E">Classe E (échéance 2034)</option>
                <option value="D">Classe D</option>
                <option value="C">Classe C</option>
                <option value="B">Classe B</option>
                <option value="A">Classe A</option>
              </select>
            </div>
            <div class="field">
              <label for="exp-street">Filtrer par nom de rue (optionnel)</label>
              <input id="exp-street" type="search" placeholder="Ex : Victor Hugo, République...">
            </div>
            <button type="submit" class="btn-primary">Actualiser en direct</button>
          </form>

          <p id="live-explorer-status" class="live-status">Chargement des données live ADEME &amp; SIRENE RGE...</p>

          <div class="live-grid-2">
            <div>
              <h3 style="margin:0 0 10px;font-size:1.05rem;">Derniers DPE ADEME publiés à {nom_h}</h3>
              <div class="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>DPE</th>
                      <th>Adresse</th>
                      <th>Type &amp; Surface</th>
                      <th>Conso EP</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody id="dpe-live-tbody">
                    <tr><td colspan="5">Chargement des diagnostics ADEME en direct...</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div>
              <h3 style="margin:0 0 10px;font-size:1.05rem;">Artisans &amp; entreprises certifiés RGE ({cp})</h3>
              <p id="rge-total-summary" class="live-status" style="margin-top:0;">Interrogation de l'Annuaire Officiel des Entreprises...</p>
              <div id="rge-live-cards" class="rge-list"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Calendrier légal des passoires thermiques &amp; aides à {nom_h}</h2>
{render_calendar_section()}

        <h2 style="margin-top:30px;">Ressources officielles, aides &amp; partenaires rénovation</h2>
        <div id="partner-cards-mount" class="partner-grid"></div>
{render_ecosystem_cta()}
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <h2>Questions fréquentes — DPE &amp; RGE à {nom_h}</h2>
        <div class="faq-list">
{faq_html}
        </div>

        <h2 style="margin-top:28px;">Autres villes observées en {region} &amp; en France</h2>
        <div class="city-grid">
{chr(10).join(sib_cards)}
        </div>
      </div>
    </section>
  </main>

{render_footer("../")}
  <script src="../partner-slots.js"></script>
  <script src="../assets/dpe-rge-live.js"></script>
</body>
</html>
"""


def build_directory_page(villes: list[dict]) -> str:
    url = f"{SITE_BASE}/villes/"
    regions = sorted({v["region"] for v in villes})
    pills = [f'<button type="button" class="dir-pill" data-region="all" aria-pressed="true">Toutes ({len(villes)})</button>']
    for reg in regions:
        cnt = sum(1 for v in villes if v["region"] == reg)
        pills.append(
            f'<button type="button" class="dir-pill" data-region="{html.escape(reg)}" aria-pressed="false">{html.escape(reg)} ({cnt})</button>'
        )

    cards = []
    for v in villes:
        s = v["dpe_snapshot"]
        hay = f"{v['nom']} {v['code_postal']} {v['insee']} {v['departement']} {v['code_departement']} {v['region']}".lower()
        cards.append(
            f'          <a class="city-card" href="./{v["slug"]}.html" '
            f'data-region="{html.escape(v["region"])}" data-search="{html.escape(hay)}">'
            f'<strong>{html.escape(v["nom"])} ({v["code_postal"]})</strong>'
            f'<span class="meta">{html.escape(v["departement"])} ({v["code_departement"]}) · {html.escape(v["region"])} · INSEE {v["insee"]}</span>'
            f'<div class="stats"><span>{fmt_int(s["total"])} DPE</span><span style="color:#b91c1c;">{s["passoires_pct"]:.1f} % F/G</span></div>'
            f"</a>"
        )

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "Annuaire DPE ADEME & Artisans RGE — 100 Villes de France",
                "url": url,
                "dateModified": LASTMOD,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Observatoire DPE & RGE France", "item": f"{SITE_BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": "100 Villes de France", "item": url},
                ],
            },
            {
                "@type": "Dataset",
                "name": "Observatoire Open Data DPE ADEME — Top 100 Villes de France",
                "description": "Agrégats officiels DPE (étiquettes A à G, part de passoires thermiques F/G) pour les 100 plus grandes communes métropolitaines françaises.",
                "url": url,
                "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
                "dateModified": LASTMOD,
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Quelles villes sont couvertes par l'Observatoire DPE & RGE ?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "L'annuaire couvre les 100 communes métropolitaines les plus peuplées (Paris, Marseille, Lyon, Toulouse, Nice, Nantes, Montpellier, Strasbourg, Bordeaux, Lille, Rennes, Reims, Toulon, Saint-Étienne, Le Havre, Grenoble, Dijon, Angers, Nîmes, Pau, etc.) avec statistiques ADEME et annuaire RGE live.",
                        },
                    }
                ],
            },
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Annuaire DPE ADEME &amp; Artisans RGE — 100 Villes de France | Observatoire Open Data</title>
  <meta name="description" content="Explorez les statistiques DPE ADEME (étiquettes A–G, passoires thermiques F/G) et les artisans certifiés RGE dans les 100 plus grandes villes de France.">
  <link rel="canonical" href="{url}">
  <link rel="stylesheet" href="../assets/styles.css">
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body>
{render_header("../")}

  <main>
    <section class="hero">
      <div class="container">
        <div class="breadcrumb"><a href="../index.html">Observatoire DPE &amp; RGE</a> › 100 Villes de France</div>
        <div class="eyebrow">100 Communes Métropolitaines · Données Officielles ADEME &amp; SIRENE RGE</div>
        <h1>Annuaire DPE &amp; Artisans RGE par ville (100 fiches locales)</h1>
        <p class="hero-lead">
          Filtrez par région, département, nom de commune ou code postal pour consulter le taux officiel de passoires thermiques F/G et la liste en direct des artisans certifiés RGE.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="live-controls">
          <div class="field">
            <label for="city-search">Rechercher une ville, un département ou un code postal</label>
            <input id="city-search" type="search" placeholder="Ex : Lyon, 31000, Bretagne, Pau, 75001...">
          </div>
        </div>
        <div class="dir-pills">
          {" ".join(pills)}
        </div>
        <p id="dir-count" class="live-status">{len(villes)} / {len(villes)} villes affichées</p>

        <div id="city-list" class="city-grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>
  </main>

{render_footer("../")}
  <script>
  (function () {{
    var search = document.getElementById("city-search");
    var pills = document.querySelectorAll(".dir-pill");
    var cards = document.querySelectorAll("#city-list .city-card");
    var count = document.getElementById("dir-count");
    var activeRegion = "all";

    function update() {{
      var q = (search && search.value ? search.value : "").trim().toLowerCase();
      var visible = 0;
      for (var i = 0; i < cards.length; i++) {{
        var c = cards[i];
        var reg = c.getAttribute("data-region");
        var hay = c.getAttribute("data-search") || "";
        var ok = (activeRegion === "all" || reg === activeRegion) && (!q || hay.indexOf(q) !== -1);
        c.hidden = !ok;
        if (ok) visible++;
      }}
      if (count) count.textContent = visible + " / " + cards.length + " villes affichées";
    }}

    if (search) search.addEventListener("input", update);
    for (var j = 0; j < pills.length; j++) {{
      pills[j].addEventListener("click", function (ev) {{
        var btn = ev.currentTarget;
        activeRegion = btn.getAttribute("data-region") || "all";
        for (var k = 0; k < pills.length; k++) {{
          pills[k].setAttribute("aria-pressed", pills[k] === btn ? "true" : "false");
        }}
        update();
      }});
    }}
  }})();
  </script>
</body>
</html>
"""


def build_home_page(villes: list[dict]) -> str:
    url = f"{SITE_BASE}/"
    total_dpe_all = sum(int(v["dpe_snapshot"]["total"]) for v in villes)
    total_fg_all = sum(int(v["dpe_snapshot"]["passoires_fg"]) for v in villes)
    total_pop_all = sum(int(v["population"]) for v in villes)
    agg_counts = {k: sum(int(v["dpe_snapshot"]["counts"][k]) for v in villes) for k in "ABCDEFG"}
    avg_fg_pct = round((total_fg_all / total_dpe_all) * 100.0, 1) if total_dpe_all else 0.0

    top_passoires = sorted(villes, key=lambda v: v["dpe_snapshot"]["passoires_pct"], reverse=True)[:10]
    top_volume = villes[:12]

    passoire_rows = "\n".join(
        f'              <tr><td><a href="./villes/{v["slug"]}.html"><strong>{html.escape(v["nom"])}</strong> ({v["code_postal"]})</a></td>'
        f'<td>{html.escape(v["departement"])} ({v["code_departement"]})</td>'
        f'<td>{fmt_int(v["dpe_snapshot"]["total"])}</td>'
        f'<td style="color:#b91c1c;font-weight:700;">{v["dpe_snapshot"]["passoires_pct"]:.1f}&nbsp;% ({fmt_int(v["dpe_snapshot"]["passoires_fg"])})</td></tr>'
        for v in top_passoires
    )

    featured_cards = "\n".join(
        f'          <a class="city-card" href="./villes/{v["slug"]}.html">'
        f'<strong>{html.escape(v["nom"])} ({v["code_postal"]})</strong>'
        f'<span class="meta">{html.escape(v["region"])} · INSEE {v["insee"]}</span>'
        f'<div class="stats"><span>{fmt_int(v["dpe_snapshot"]["total"])} DPE</span><span style="color:#b91c1c;">{v["dpe_snapshot"]["passoires_pct"]:.1f} % F/G</span></div>'
        f"</a>"
        for v in top_volume
    )

    faq_items = [
        {
            "@type": "Question",
            "name": "D'où proviennent les données DPE et RGE affichées sur l'Observatoire ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Toutes les données proviennent en direct des APIs publiques officielles françaises (Licence Ouverte 2.0) : base ADEME dpe03existant (data.ademe.fr) pour les diagnostics énergétiques, Annuaire des Entreprises DINUM/INSEE (recherche-entreprises.api.gouv.fr?est_rge=true) pour les artisans RGE, et geo.api.gouv.fr pour les codes INSEE et postaux.",
            },
        },
        {
            "@type": "Question",
            "name": "Puis-je interroger n'importe quel code postal français hors des 100 villes ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Oui ! L'explorateur live sur cette page accepte n'importe quel code postal de 5 chiffres en France métropolitaine et charge instantanément la distribution A–G ADEME, les derniers DPE publiés et les artisans certifiés RGE locaux.",
            },
        },
        {
            "@type": "Question",
            "name": "Quand les logements classés F et G sont-ils interdits à la location ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Les logements classés G sont interdits à la location depuis le 1er janvier 2025, les logements classés F seront concernés au 1er janvier 2028, puis la classe E au 1er janvier 2034 (Loi Climat et Résilience).",
            },
        },
    ]

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": "Observatoire ADEME DPE & Artisans RGE — 100 Villes de France",
                "url": url,
                "inLanguage": "fr-FR",
            },
            {
                "@type": "Dataset",
                "name": "Observatoire National DPE ADEME & Artisans RGE — 100 Grandes Villes",
                "description": f"Synthèse de {fmt_int(total_dpe_all)} diagnostics DPE ADEME et explorateur temps réel des entreprises certifiées RGE dans 100 villes de France.",
                "url": url,
                "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
                "dateModified": LASTMOD,
            },
            {
                "@type": "FAQPage",
                "mainEntity": faq_items,
            },
        ],
    }

    faq_html = "\n".join(
        f'          <details><summary>{html.escape(q["name"])}</summary><p>{html.escape(q["acceptedAnswer"]["text"])}</p></details>'
        for q in faq_items
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Observatoire ADEME DPE &amp; Artisans RGE — 100 Villes de France (Open Data Live)</title>
  <meta name="description" content="Consultez gratuitement les étiquettes DPE ADEME (A à G), le taux de passoires thermiques F/G et les artisans certifiés RGE dans les 100 plus grandes villes de France ou par code postal.">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="Observatoire ADEME DPE &amp; Artisans RGE — 100 Villes de France">
  <meta property="og:description" content="Explorateur live ADEME DPE &amp; SIRENE RGE (100 % gratuit, données officielles ouvertes) sur 100 villes de France.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <link rel="stylesheet" href="./assets/styles.css">
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body>
{render_header("./")}

  <main>
    <section class="hero">
      <div class="container">
        <div class="eyebrow">100 % Gratuit · APIs Officielles ADEME &amp; DINUM/INSEE Live · Zéro inscription</div>
        <h1>Observatoire DPE ADEME, passoires thermiques F/G &amp; artisans certifiés RGE en France</h1>
        <p class="hero-lead">
          Explorez en temps réel les <strong>Diagnostics de Performance Énergétique (DPE)</strong> officiels et trouvez les <strong>entreprises certifiées RGE</strong> pour n'importe quel code postal français ou parmi nos <strong>100 fiches villes détaillées</strong>.
        </p>

        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-val">{fmt_int(total_dpe_all)}</span>
            <span class="kpi-label">DPE ADEME analysés sur les 100 grandes villes ({LASTMOD})</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val warn">{avg_fg_pct:.1f}&nbsp;% ({fmt_int(total_fg_all)})</span>
            <span class="kpi-label">Passoires thermiques F &amp; G identifiées</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val ok">100 Villes</span>
            <span class="kpi-label">Fiches locales dédiées ({fmt_int(total_pop_all)} habitants couverts)</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-val">Live API</span>
            <span class="kpi-label">ADEME <code>dpe03existant</code> + SIRENE <code>est_rge=true</code></span>
          </div>
        </div>
      </div>
    </section>

    <section id="explorateur-live" class="section section-alt">
      <div class="container">
        <div id="dpe-rge-explorer" class="panel" data-cp="75001" data-ademe-qs="code_postal_ban:75001" data-mode="home">
          <h2>Explorateur LIVE par Code Postal (toute la France)</h2>
          <p class="section-sub">Saisissez n'importe quel code postal français (5 chiffres) pour obtenir en direct la répartition ADEME A–G, les derniers diagnostics publiés et les artisans certifiés RGE locaux.</p>

          <form id="exp-form" class="live-controls">
            <div class="field">
              <label for="exp-cp">Code postal (5 chiffres)</label>
              <input id="exp-cp" type="text" inputmode="numeric" maxlength="5" value="75001" placeholder="Ex : 69001, 31000, 33000...">
            </div>
            <div class="field">
              <label for="exp-dpe-filter">Étiquette DPE</label>
              <select id="exp-dpe-filter">
                <option value="all">Toutes (A–G)</option>
                <option value="FG">Passoires thermiques (F &amp; G)</option>
                <option value="G">Classe G uniquement</option>
                <option value="F">Classe F uniquement</option>
                <option value="E">Classe E uniquement</option>
                <option value="D">Classe D</option>
                <option value="C">Classe C</option>
                <option value="B">Classe B</option>
                <option value="A">Classe A</option>
              </select>
            </div>
            <div class="field">
              <label for="exp-street">Nom de rue (optionnel)</label>
              <input id="exp-street" type="search" placeholder="Ex : Rivoli, Jean Jaurès...">
            </div>
            <button type="submit" class="btn-primary">Analyser ce code postal</button>
          </form>

          <p id="live-explorer-status" class="live-status">Interrogation live ADEME &amp; SIRENE RGE...</p>
          <p id="dpe-dynamic-summary" style="font-weight:700;margin:0 0 10px;"></p>
          <div id="dpe-dynamic-bars" class="dpe-bars" style="margin-bottom:20px;"></div>

          <div class="live-grid-2">
            <div>
              <h3 style="margin:0 0 10px;font-size:1.05rem;">Derniers DPE ADEME sur ce code postal</h3>
              <div class="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>DPE</th>
                      <th>Adresse</th>
                      <th>Type &amp; Surface</th>
                      <th>Conso EP</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody id="dpe-live-tbody">
                    <tr><td colspan="5">Chargement en direct...</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div>
              <h3 style="margin:0 0 10px;font-size:1.05rem;">Entreprises certifiées RGE locales</h3>
              <p id="rge-total-summary" class="live-status" style="margin-top:0;">Interrogation SIRENE RGE...</p>
              <div id="rge-live-cards" class="rge-list"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="live-grid-2">
          <div class="panel">
            <h2>Distribution agrégée DPE — Top 100 Villes</h2>
            <p class="section-sub">Cumul officiel de {fmt_int(total_dpe_all)} diagnostics ADEME sur les 100 plus grandes communes métropolitaines.</p>
            <div class="dpe-bars">
{render_dpe_bars_html(agg_counts, total_dpe_all)}
            </div>
          </div>
          <div class="panel">
            <h2>Top 10 taux de passoires thermiques (F &amp; G)</h2>
            <p class="section-sub">Villes présentant la part la plus élevée de logements F/G parmi les 100 grandes villes étudiées.</p>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr><th>Ville</th><th>Département</th><th>Total DPE</th><th>Part F/G</th></tr>
                </thead>
                <tbody>
{passoire_rows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;">
          <div>
            <h2>Accès rapide aux grandes métropoles</h2>
            <p class="section-sub" style="margin-bottom:0;">Sélection des 12 premières villes par population — ou parcourez l'annuaire complet des 100 communes.</p>
          </div>
          <a class="btn-primary" href="./villes/index.html">Voir les 100 villes →</a>
        </div>
        <div class="city-grid">
{featured_cards}
        </div>
      </div>
    </section>

    <section id="calendrier-passoires" class="section">
      <div class="container">
        <h2>Calendrier réglementaire Loi Climat &amp; Résilience (2025–2034)</h2>
{render_calendar_section()}

        <h2 style="margin-top:30px;">Aides publiques, rénovation &amp; ressources BTP</h2>
        <div id="partner-cards-mount" class="partner-grid"></div>
{render_ecosystem_cta()}
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <h2>Questions fréquentes sur l'Observatoire DPE &amp; RGE</h2>
        <div class="faq-list">
{faq_html}
        </div>
      </div>
    </section>
  </main>

{render_footer("./")}
  <script src="./partner-slots.js"></script>
  <script src="./assets/dpe-rge-live.js"></script>
</body>
</html>
"""


def write_sitemap_and_robots(repo_root: Path, villes: list[dict]) -> int:
    urls = [
        (f"{SITE_BASE}/", LASTMOD, "weekly", "1.0"),
        (f"{SITE_BASE}/villes/", LASTMOD, "weekly", "0.9"),
    ]
    for v in villes:
        urls.append((f"{SITE_BASE}/villes/{v['slug']}.html", LASTMOD, "monthly", "0.75"))

    entries = [
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        for loc, mod, freq, prio in urls
    ]
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (repo_root / "sitemap.xml").write_text(xml, encoding="utf-8")

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_BASE}/sitemap.xml\n"
    )
    (repo_root / "robots.txt").write_text(robots, encoding="utf-8")
    return len(urls)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    villes = json.loads((repo_root / "data" / "villes_top100.json").read_text(encoding="utf-8"))
    assert len(villes) == 100, f"Expected 100 cities, got {len(villes)}"
    assert len({v["slug"] for v in villes}) == 100, "Duplicate city slugs detected"

    out_dir = repo_root / "villes"
    out_dir.mkdir(parents=True, exist_ok=True)

    (repo_root / "index.html").write_text(build_home_page(villes), encoding="utf-8")
    (out_dir / "index.html").write_text(build_directory_page(villes), encoding="utf-8")

    for idx, v in enumerate(villes):
        same_reg = [x for x in villes if x["region"] == v["region"] and x["slug"] != v["slug"]]
        others = [x for x in villes if x["slug"] != v["slug"] and x not in same_reg]
        siblings = (same_reg + others[idx % max(1, len(others)):] + others)[:4]
        (out_dir / f"{v['slug']}.html").write_text(build_city_page(v, siblings), encoding="utf-8")

    total_urls = write_sitemap_and_robots(repo_root, villes)
    print(f"Generated index.html + villes/index.html + {len(villes)} city pages; sitemap.xml updated ({total_urls} URLs) + robots.txt.")


if __name__ == "__main__":
    main()
