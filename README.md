# Observatoire ADEME DPE & Artisans RGE — 100 Villes de France (Open Data)

Portail open-data **100 % statique & côté navigateur (`0,00 €/mois`)** explorant les **Diagnostics de Performance Énergétique (DPE)** et les **artisans certifiés RGE** sur les **100 plus grandes villes de France métropolitaine**, adossé aux APIs officielles françaises zéro-clé.

- **Site LIVE (GitHub Pages)** : https://yannabadie.github.io/observatoire-dpe-rge-france/
- **Annuaire 100 Villes** : https://yannabadie.github.io/observatoire-dpe-rge-france/villes/
- **Sources officielles publiques (zéro clé API, licence Ouverte v2.0)** :
  - **ADEME Open Data** (`dpe03existant`) : `https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines` & `values_agg`
  - **DINUM / INSEE Annuaire des Entreprises (filtre RGE)** : `https://recherche-entreprises.api.gouv.fr/search?est_rge=true&code_postal=...`
  - **IGN / Etalab API Découpage Administratif (`geo.api.gouv.fr`)** : codes INSEE, codes postaux, départements, régions & populations officiels

## Architecture & Régénération Déterministe

```bash
python3 scripts/build_villes.py
```

Le script génère de manière 100 % déterministe (Python 3 stdlib, zéro dépendance) :
- `index.html` — Observatoire national + explorateur live par code postal (`ADEME DPE` + `SIRENE RGE`)
- `villes/index.html` — Annuaire filtrable par région et recherche instantanée des **100 villes**
- `villes/<slug>.html` — **100 pages locales** (statistiques ADEME A–G, passoires thermiques F/G, calendrier Loi Climat & Résilience 2025/2028/2034, explorateur live DPE + artisans RGE, JSON-LD `FAQPage` + `BreadcrumbList` + `Dataset`)
- `sitemap.xml` (`102` URLs) et `robots.txt`
- `partner-slots.js` — Table unique centralisant les futurs liens partenaires rénovation/énergie/financement (`0` code inventé par défaut, ajout automatique de `rel="noopener noreferrer sponsored"`).

## Écosystème & APIs Développeurs Associés

- **API JSON Unifiée ADEME DPE (Cloudflare Worker / Zyla / RapidAPI)** : `https://eu-public-intelligence-worker.eu-us-opendata-worker.workers.dev` (endpoint `/v1/ademe-dpe`, flag `isThermalSieve` + BODACC + OSV/CRA + openFDA + RTE Éco2mix)
- **Artisans RGE & Entreprises BTP — Facturation Électronique 2026–2027** : [FacturKit 2027 — Guides BTP & Comparateur PA](https://yannabadie.github.io/facturkit-2027/metiers/)
- **Automatisation & Extraction Open-Data à Grande Échelle** : [Apify Open-Data & MCP Actors](https://apify.com/?fpr=zuvzfw) *(lien partenaire)*

## Licence

MIT — Données publiques sous Licence Ouverte 2.0 (ADEME, DINUM/INSEE, IGN/Etalab).
