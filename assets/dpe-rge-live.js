/**
 * Explorateur LIVE 100 % navigateur — ADEME DPE Existant + Annuaire Officiel Artisans RGE (DINUM/INSEE)
 * Zéro backend payant, zéro clé API, CORS natif (*), échappement DOM strict (textContent).
 */
(function () {
  "use strict";

  var ADEME_LINES = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines";
  var ADEME_AGG = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/values_agg";
  var SIRENE_RGE = "https://recherche-entreprises.api.gouv.fr/search";
  var fmtInt = new Intl.NumberFormat("fr-FR");

  function clearEl(el) {
    while (el && el.firstChild) el.removeChild(el.firstChild);
  }

  function makeBadge(label) {
    var span = document.createElement("span");
    var clean = String(label || "?").toUpperCase().slice(0, 1);
    span.className = "dpe-badge dpe-" + (/[A-G]/.test(clean) ? clean : "D");
    span.textContent = clean;
    return span;
  }

  function renderAggBars(mountEl, counts, total) {
    if (!mountEl) return;
    clearEl(mountEl);
    var letters = ["A", "B", "C", "D", "E", "F", "G"];
    for (var i = 0; i < letters.length; i++) {
      var k = letters[i];
      var val = Number(counts[k] || 0);
      var pct = total > 0 ? Math.round((val / total) * 1000) / 10 : 0;

      var row = document.createElement("div");
      row.className = "dpe-bar-row";
      row.appendChild(makeBadge(k));

      var track = document.createElement("div");
      track.className = "bar-track";
      var fill = document.createElement("div");
      fill.className = "bar-fill dpe-" + k;
      fill.style.width = Math.max(pct, val > 0 ? 1 : 0) + "%";
      track.appendChild(fill);
      row.appendChild(track);

      var num = document.createElement("div");
      num.className = "dpe-num";
      num.textContent = fmtInt.format(val) + " (" + pct.toFixed(1) + " %)";
      row.appendChild(num);

      mountEl.appendChild(row);
    }
  }

  function renderDpeRows(tbody, rows) {
    if (!tbody) return;
    clearEl(tbody);
    if (!rows || rows.length === 0) {
      var tr0 = document.createElement("tr");
      var td0 = document.createElement("td");
      td0.colSpan = 5;
      td0.textContent = "Aucun DPE récent trouvé pour ce filtre. Essayez un autre code postal ou supprimez le filtre d'étiquette.";
      tr0.appendChild(td0);
      tbody.appendChild(tr0);
      return;
    }
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      var tr = document.createElement("tr");

      var tdDpe = document.createElement("td");
      tdDpe.appendChild(makeBadge(r.etiquette_dpe));
      tr.appendChild(tdDpe);

      var tdAddr = document.createElement("td");
      tdAddr.textContent = r.adresse_ban || ((r.code_postal_ban || "") + " " + (r.nom_commune_ban || ""));
      tr.appendChild(tdAddr);

      var tdType = document.createElement("td");
      var surf = r.surface_habitable_logement ? Math.round(Number(r.surface_habitable_logement)) + " m²" : "—";
      tdType.textContent = (r.type_batiment || "logement") + " · " + surf;
      tr.appendChild(tdType);

      var tdConso = document.createElement("td");
      tdConso.textContent = r.conso_5_usages_par_m2_ep ? Math.round(Number(r.conso_5_usages_par_m2_ep)) + " kWh/m²/an" : "—";
      tr.appendChild(tdConso);

      var tdDate = document.createElement("td");
      tdDate.textContent = (r.date_etablissement_dpe || "").slice(0, 10) || "—";
      tr.appendChild(tdDate);

      tbody.appendChild(tr);
    }
  }

  function renderRgeCards(container, results, totalCount, cp) {
    if (!container) return;
    clearEl(container);
    if (!results || results.length === 0) {
      var p0 = document.createElement("p");
      p0.className = "live-status";
      p0.textContent = "Aucune entreprise certifiée RGE recensée directement sur le code postal " + cp + " (essayez un code postal voisin ou le chef-lieu).";
      container.appendChild(p0);
      return;
    }
    for (var i = 0; i < results.length; i++) {
      var org = results[i];
      var card = document.createElement("div");
      card.className = "rge-card";

      var pill = document.createElement("span");
      pill.className = "rge-pill";
      pill.textContent = "Certifié RGE Officiel · NAF " + (org.activite_principale || "BTP");
      card.appendChild(pill);

      var name = document.createElement("div");
      name.className = "rge-name";
      name.textContent = org.nom_complet || org.nom_raison_sociale || "Entreprise RGE";
      card.appendChild(name);

      var meta = document.createElement("div");
      meta.className = "rge-meta";
      var addr = (org.siege && org.siege.adresse) ? org.siege.adresse : (cp || "");
      meta.textContent = "SIREN " + (org.siren || "—") + " · " + addr;
      card.appendChild(meta);

      container.appendChild(card);
    }
    var summary = document.getElementById("rge-total-summary");
    if (summary) {
      summary.textContent = fmtInt.format(totalCount || results.length) + " entreprise(s) certifiée(s) RGE trouvée(s) sur le code postal " + cp + " (API officielle DINUM/INSEE).";
    }
  }

  function fetchLiveExplorer(opts) {
    var cp = String(opts.postalCode || "").replace(/[^0-9]/g, "").slice(0, 5);
    var ademeBaseQs = opts.ademeQs || (cp ? ("code_postal_ban:" + cp) : "code_postal_ban:75001");
    var labelFilter = String(opts.dpeFilter || "all");
    var streetQuery = String(opts.streetQuery || "").trim().replace(/["\\]/g, "");

    var statusEl = document.getElementById("live-explorer-status");
    var tbody = document.getElementById("dpe-live-tbody");
    var rgeMount = document.getElementById("rge-live-cards");
    var dynBarsMount = document.getElementById("dpe-dynamic-bars");
    var dynSummary = document.getElementById("dpe-dynamic-summary");

    if (statusEl) {
      statusEl.textContent = "Interrogation en direct des APIs officielles ADEME (dpe03existant) et DINUM SIRENE (est_rge=true)...";
    }

    var clauses = ["(" + ademeBaseQs + ")"];
    if (labelFilter === "FG") {
      clauses.push("(etiquette_dpe:F OR etiquette_dpe:G)");
    } else if (/^[A-G]$/.test(labelFilter)) {
      clauses.push("etiquette_dpe:" + labelFilter);
    }
    if (streetQuery.length >= 2) {
      clauses.push('adresse_ban:"' + streetQuery + '"');
    }
    var fullQs = clauses.join(" AND ");

    var dpeUrl = ADEME_LINES + "?size=12&sort=-date_etablissement_dpe&select=etiquette_dpe,etiquette_ges,adresse_ban,code_postal_ban,nom_commune_ban,surface_habitable_logement,conso_5_usages_par_m2_ep,type_batiment,date_etablissement_dpe&qs=" + encodeURIComponent(fullQs);
    var rgeUrl = SIRENE_RGE + "?est_rge=true&code_postal=" + encodeURIComponent(cp || "75001") + "&per_page=9";

    var tasks = [
      fetch(dpeUrl).then(function (r) { if (!r.ok) throw new Error("ADEME HTTP " + r.status); return r.json(); }),
      fetch(rgeUrl).then(function (r) { if (!r.ok) throw new Error("SIRENE HTTP " + r.status); return r.json(); })
    ];

    if (opts.refreshAgg && dynBarsMount) {
      var aggUrl = ADEME_AGG + "?field=etiquette_dpe&qs=" + encodeURIComponent(ademeBaseQs);
      tasks.push(fetch(aggUrl).then(function (r) { if (!r.ok) throw new Error("ADEME AGG HTTP " + r.status); return r.json(); }));
    }

    Promise.allSettled(tasks).then(function (settled) {
      var okMsgs = [];
      if (settled[0].status === "fulfilled") {
        var dpeData = settled[0].value;
        renderDpeRows(tbody, dpeData.results || []);
        okMsgs.push("ADEME DPE LIVE : " + fmtInt.format(dpeData.total || 0) + " diagnostics correspondants");
      } else {
        renderDpeRows(tbody, []);
        okMsgs.push("ADEME momentanément indisponible (repli sur l'instantané officiel affiché ci-dessus)");
      }

      if (settled[1].status === "fulfilled") {
        var rgeData = settled[1].value;
        renderRgeCards(rgeMount, rgeData.results || [], rgeData.total_results || 0, cp || "75001");
        okMsgs.push("SIRENE RGE LIVE : " + fmtInt.format(rgeData.total_results || 0) + " entreprises certifiées sur " + (cp || "75001"));
      } else {
        renderRgeCards(rgeMount, [], 0, cp || "75001");
        okMsgs.push("Annuaire SIRENE RGE momentanément indisponible");
      }

      if (settled[2] && settled[2].status === "fulfilled" && dynBarsMount) {
        var agg = settled[2].value;
        var counts = { A: 0, B: 0, C: 0, D: 0, E: 0, F: 0, G: 0 };
        var aggs = agg.aggs || [];
        var total = 0;
        for (var i = 0; i < aggs.length; i++) {
          var k = String(aggs[i].value || "").toUpperCase();
          if (counts.hasOwnProperty(k)) {
            counts[k] = Number(aggs[i].total || 0);
            total += counts[k];
          }
        }
        renderAggBars(dynBarsMount, counts, total);
        if (dynSummary) {
          var fg = counts.F + counts.G;
          var pctFg = total > 0 ? ((fg / total) * 100).toFixed(1) : "0.0";
          dynSummary.textContent = "Code postal " + cp + " : " + fmtInt.format(total) + " DPE ADEME recensés dont " + fmtInt.format(fg) + " passoires thermiques F/G (" + pctFg + " %).";
        }
      }

      if (statusEl) {
        statusEl.textContent = okMsgs.join(" · ");
      }
    });
  }

  function initExplorer() {
    var root = document.getElementById("dpe-rge-explorer");
    if (!root) return;

    var cpInput = document.getElementById("exp-cp");
    var filterSelect = document.getElementById("exp-dpe-filter");
    var streetInput = document.getElementById("exp-street");
    var form = document.getElementById("exp-form");

    var defaultCp = root.getAttribute("data-cp") || "75001";
    var defaultAdemeQs = root.getAttribute("data-ademe-qs") || "";
    var isHome = root.getAttribute("data-mode") === "home";

    function run(userTriggered) {
      var cpVal = cpInput ? cpInput.value.replace(/[^0-9]/g, "").slice(0, 5) : defaultCp;
      if (cpVal.length !== 5) cpVal = defaultCp;
      var useAdemeQs = (!userTriggered && defaultAdemeQs) ? defaultAdemeQs : ("code_postal_ban:" + cpVal);
      if (defaultAdemeQs && cpVal === defaultCp && !isHome) {
        useAdemeQs = defaultAdemeQs;
      }
      fetchLiveExplorer({
        postalCode: cpVal,
        ademeQs: useAdemeQs,
        dpeFilter: filterSelect ? filterSelect.value : "all",
        streetQuery: streetInput ? streetInput.value : "",
        refreshAgg: isHome || (cpVal !== defaultCp)
      });
    }

    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        run(true);
      });
    }
    if (filterSelect) {
      filterSelect.addEventListener("change", function () {
        run(true);
      });
    }

    run(false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initExplorer);
  } else {
    initExplorer();
  }
})();
