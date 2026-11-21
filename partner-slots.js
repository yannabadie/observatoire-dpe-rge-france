/**
 * Table unique centralisée des emplacements partenaires & CTAs — Observatoire DPE & RGE France
 * Fichier public sans secret ni PII.
 *
 * MODE D'EMPLOI (1 seule édition -> met à jour les 102 pages : accueil, annuaire & 100 villes) :
 * Laisser "" tant qu'un programme partenaire (Affilae, Awin, courtier Éco-PTZ, travaux RGE)
 * n'est pas validé. Les liens officiels publics (France Rénov', ADEME, Service-Public) restent
 * actifs par défaut sans tracking. Dès qu'une URL validée est renseignée, rel="noopener noreferrer sponsored"
 * est appliqué automatiquement.
 */
(function (global) {
  "use strict";

  var PARTNER_SLOTS = {
    "affilae-renovation-devis": "",
    "affilae-audit-energetique": "",
    "affilae-courtier-ecoptz": "",
    "affilae-fournisseur-energie": "",
    "affilae-assurance-pno": "",
    "affilae-indy-lmnp": ""
  };

  var PARTNER_CARDS = [
    {
      slot: "affilae-renovation-devis",
      tag: "Aides & Devis RGE",
      title: "Préparer un dossier MaPrimeRénov' & CEE",
      summary: "Vérifiez votre éligibilité aux aides publiques 2026 (rénovation d'ampleur, pompe à chaleur, isolation) avant de signer un devis d'artisan RGE.",
      cta: "Consulter le portail officiel France Rénov' →",
      fallbackUrl: "https://france-renov.gouv.fr/",
      isOfficialFallback: true
    },
    {
      slot: "affilae-audit-energetique",
      tag: "Passoires F & G",
      title: "Audit énergétique & sortie de passoire",
      summary: "Obligatoire pour la vente de maisons/monopropriétés classées E, F ou G et requis pour le parcours accompagné MaPrimeRénov'.",
      cta: "Règles officielles Audit Énergétique →",
      fallbackUrl: "https://www.ecologie.gouv.fr/politiques-publiques/audit-energetique-reglementaire",
      isOfficialFallback: true
    },
    {
      slot: "affilae-indy-lmnp",
      tag: "Propriétaires Bailleurs / LMNP",
      title: "Comptabilité LMNP & gestion travaux déductibles",
      summary: "Suivez vos déficits fonciers doublés pour rénovation énergétique, amortissements LMNP et factures d'artisans RGE conformes Factur-X.",
      cta: "Comparer les outils & PA conformes →",
      fallbackUrl: "https://yannabadie.github.io/facturkit-2027/comparateur-pa-2026.html",
      isOfficialFallback: true
    },
    {
      slot: "none-facturkit-btp",
      tag: "Artisans RGE & BTP",
      title: "Artisans RGE : obligations Factur-X 2026–2027",
      summary: "Réception électronique obligatoire depuis le 01/09/2026 et émission Factur-X 1.09.2 au 01/09/2027 (TVA 5,5 % rénovation énergétique, autoliquidation BTP).",
      cta: "Voir nos 50 guides métiers & NAF BTP →",
      fallbackUrl: "https://yannabadie.github.io/facturkit-2027/metiers/",
      isOfficialFallback: true
    }
  ];

  var ECOSYSTEM_LINKS = {
    workerApiInfo: "https://github.com/yannabadie/observatoire-dpe-rge-france#écosystème--apis-développeurs-associés",
    facturkitHome: "https://yannabadie.github.io/facturkit-2027/",
    facturkitMetiers: "https://yannabadie.github.io/facturkit-2027/metiers/",
    facturkitPlombier: "https://yannabadie.github.io/facturkit-2027/metiers/plombier-chauffagiste.html",
    facturkitArtisan: "https://yannabadie.github.io/facturkit-2027/metiers/artisan-batiment-macon.html",
    apifyPartnerUrl: "https://apify.com/?fpr=zuvzfw"
  };

  function applyPartnerSlots(root) {
    var scope = root || global.document;
    if (!scope || !scope.querySelectorAll) return;
    var links = scope.querySelectorAll("a[data-partner-slot]");
    for (var i = 0; i < links.length; i++) {
      var slot = links[i].getAttribute("data-partner-slot");
      if (slot && PARTNER_SLOTS[slot]) {
        links[i].setAttribute("href", PARTNER_SLOTS[slot]);
        links[i].setAttribute("rel", "noopener noreferrer sponsored");
      }
    }
  }

  function renderPartnerCards(containerId) {
    if (!global.document) return;
    var box = global.document.getElementById(containerId);
    if (!box) return;
    box.textContent = "";
    for (var i = 0; i < PARTNER_CARDS.length; i++) {
      var item = PARTNER_CARDS[i];
      var card = global.document.createElement("article");
      card.className = "partner-card";

      var top = global.document.createElement("div");
      var badge = global.document.createElement("span");
      badge.className = "badge-soft";
      badge.textContent = item.tag;
      top.appendChild(badge);

      var h3 = global.document.createElement("h3");
      h3.textContent = item.title;
      top.appendChild(h3);

      var p = global.document.createElement("p");
      p.textContent = item.summary;
      top.appendChild(p);
      card.appendChild(top);

      var link = global.document.createElement("a");
      link.className = "btn-card";
      link.setAttribute("data-partner-slot", item.slot);
      var activeUrl = PARTNER_SLOTS[item.slot] || item.fallbackUrl;
      link.setAttribute("href", activeUrl);
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", PARTNER_SLOTS[item.slot] ? "noopener noreferrer sponsored" : "noopener noreferrer");
      link.textContent = item.cta;
      card.appendChild(link);

      box.appendChild(card);
    }
  }

  global.PARTNER_SLOTS = PARTNER_SLOTS;
  global.PARTNER_CARDS = PARTNER_CARDS;
  global.ECOSYSTEM_LINKS = ECOSYSTEM_LINKS;
  global.applyPartnerSlots = applyPartnerSlots;
  global.renderPartnerCards = renderPartnerCards;

  if (global.document) {
    var init = function () {
      renderPartnerCards("partner-cards-mount");
      applyPartnerSlots(global.document);
    };
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})(typeof window !== "undefined" ? window : globalThis);
