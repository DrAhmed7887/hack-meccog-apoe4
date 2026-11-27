/* MecCog APOE4 Evidence Workbench client controller (Step 1 JSON + browser DecompressionStream Mol* loader) */
(function () {
  "use strict";

  const state = {
    data: null,
    hyp: "ALL",
    nodeId: "ALL",
    dir: "ALL",
    directness: "ALL",
    tier: "ALL",
    query: "",
    structureId: "1b68",
    activeResidue: null,
    residueCoords: {},
    viewer: null,
    loadSeq: 0,
  };

  function el(id) {
    return document.getElementById(id);
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function applyUrlParams() {
    const p = new URLSearchParams(window.location.search);
    const hyp = p.get("hyp");
    if (hyp && ["ALL", "H5", "H2"].includes(hyp)) state.hyp = hyp;
    const node = p.get("node");
    if (node) state.nodeId = node;
    const dir = p.get("dir");
    if (dir && ["ALL", "supports", "contradicts"].includes(dir)) state.dir = dir;
    const struct = p.get("struct");
    if (struct && state.data.structures.some((s) => s.id === struct)) state.structureId = struct;
  }

  async function init() {
    const resp = await fetch("./data/explorer_data.json");
    if (!resp.ok) {
      el("molstar-status").textContent = "Failed to load explorer_data.json";
      return;
    }
    state.data = await resp.json();
    applyUrlParams();
    bindStaticHeader();
    document.querySelectorAll("[data-hyp]").forEach((b) => {
      const on = b.getAttribute("data-hyp") === state.hyp;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-selected", on ? "true" : "false");
    });
    document.querySelectorAll("[data-dir]").forEach((b) => {
      b.classList.toggle("is-active", b.getAttribute("data-dir") === state.dir);
    });
    populateStructureSelect();
    bindEvents();
    renderCascade();
    renderGeometryStrip();
    renderFindings();
    await initMolstar();
  }

  function bindStaticHeader() {
    const d = state.data;
    el("c5-notice-text").textContent = d.rule_c5_notice;
    el("count-all").textContent = String(d.totals.n_findings_total);
    el("count-h5").textContent = String(d.hypotheses.H5.n_findings);
    el("count-h2").textContent = String(d.hypotheses.H2.n_findings);
    updateTopMetrics();
  }

  function updateTopMetrics() {
    const d = state.data;
    if (state.hyp === "ALL") {
      el("metric-papers").textContent = `${d.totals.n_papers_total} (${d.totals.n_unique_papers} uniq)`;
      el("metric-findings").textContent = String(d.totals.n_findings_total);
      el("metric-contra").textContent = String(d.totals.n_contradicting_total);
      el("metric-stats").textContent = String(d.totals.n_printed_stats_total);
    } else {
      const h = d.hypotheses[state.hyp];
      el("metric-papers").textContent = String(h.n_papers);
      el("metric-findings").textContent = String(h.n_findings);
      el("metric-contra").textContent = String(h.n_contradicting);
      el("metric-stats").textContent = String(h.n_printed_stats);
    }
  }

  function populateStructureSelect() {
    const sel = el("structure-select");
    sel.innerHTML = "";
    for (const st of state.data.structures) {
      const opt = document.createElement("option");
      opt.value = st.id;
      opt.textContent = `${st.label} [${st.category}]`;
      sel.appendChild(opt);
    }
    sel.value = state.structureId;
    renderResidueBar();
    renderStructureMeta();
  }

  function renderResidueBar() {
    const st = state.data.structures.find((s) => s.id === state.structureId);
    const bar = el("residue-bar");
    bar.innerHTML = "";
    if (!st) return;
    for (const r of st.residues) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "res-btn" + (state.activeResidue === r.auth_seq_id ? " is-active" : "");
      btn.textContent = `${r.label} [auth ${r.auth_asym_id}:${r.auth_seq_id}]`;
      btn.addEventListener("click", () => {
        state.activeResidue = r.auth_seq_id;
        renderResidueBar();
        focusResidue(r.auth_asym_id, r.auth_seq_id);
      });
      bar.appendChild(btn);
    }
  }

  function renderStructureMeta() {
    const st = state.data.structures.find((s) => s.id === state.structureId);
    if (!st) return;
    const parts = [
      `${st.source_id}`,
      st.category,
      st.resolution ? `Resolution: ${st.resolution}` : null,
      st.mean_plddt ? `Mean pLDDT: ${st.mean_plddt}` : null,
      `${st.license}`,
      st.numbering_note,
    ].filter(Boolean);
    el("structure-meta").textContent = parts.join(" | ");
  }

  function renderGeometryStrip() {
    const g = state.data.geometry;
    el("geometry-strip").innerHTML = [
      {
        title: `APOE4 Arg112 to Glu109 (1B68): ${g["1b68_Arg112_Glu109"].distance_A} A`,
        sub: `${g["1b68_Arg112_Glu109"].res1} to ${g["1b68_Arg112_Glu109"].res2} salt bridge`,
      },
      {
        title: `Arg61 displacement: ${g["1b68_Arg61_Glu109"].distance_A} A vs ${g["1nfn_Arg61_Glu109"].distance_A} A`,
        sub: "APOE4 (1B68) moves Arg61 outward relative to APOE3 (1NFN)",
      },
      {
        title: `Full-length Arg61 to Glu255 (2L7B M1): ${g["2l7b_Arg61_Glu255"].distance_A} A`,
        sub: "N-terminal/C-terminal domain separation baseline",
      },
    ]
      .map((c) => `<div class="geom-cell"><strong>${escapeHtml(c.title)}</strong><span>${escapeHtml(c.sub)}</span></div>`)
      .join("");
  }

  function renderCascade() {
    const host = el("cascade-nodes");
    host.innerHTML = "";
    for (const nd of state.data.nodes) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cascade-node" + (state.nodeId === nd.id ? " is-selected" : "");
      btn.setAttribute("role", "listitem");
      const countText =
        nd.counts.total > 0
          ? `${nd.counts.total} findings (${nd.counts.H5} H5 / ${nd.counts.H2} H2)`
          : "Structural switch context (PDB 1B68 vs 1NFN)";
      const contraSpan =
        nd.counts.contradicts > 0
          ? `<span class="contra-inline"> | ${nd.counts.contradicts} contradicts</span>`
          : "";
      btn.innerHTML = `
        <span class="node-step">Stage ${nd.step} (${escapeHtml(nd.hypothesis_focus.join(" + "))})</span>
        <span class="node-title">${escapeHtml(nd.title)}</span>
        <span class="node-sub">${escapeHtml(nd.subtitle)}</span>
        <span class="node-counts">${escapeHtml(countText)}${contraSpan}</span>
      `;
      btn.addEventListener("click", () => {
        state.nodeId = state.nodeId === nd.id ? "ALL" : nd.id;
        renderCascade();
        renderFindings();
        if (nd.default_structure_id && nd.default_structure_id !== state.structureId) {
          state.structureId = nd.default_structure_id;
          state.activeResidue = null;
          el("structure-select").value = state.structureId;
          renderResidueBar();
          renderStructureMeta();
          loadSelectedStructure();
        }
      });
      host.appendChild(btn);
    }
    const active = state.data.nodes.find((n) => n.id === state.nodeId);
    el("active-node-note").textContent = active
      ? active.note
      : "Showing all 5 cascade stages across H5 (lysosomal cholesterol efflux and clearance) and H2 (early endosomal recycling and NHE6).";
  }

  function filteredFindings() {
    const q = state.query.trim().toLowerCase();
    return state.data.findings.filter((f) => {
      if (state.hyp !== "ALL" && f.hyp !== state.hyp) return false;
      if (state.nodeId !== "ALL" && f.node_id !== state.nodeId) return false;
      if (state.dir !== "ALL" && f.direction !== state.dir) return false;
      if (state.directness !== "ALL" && f.directness_class !== state.directness) return false;
      if (state.tier !== "ALL" && String(f.tier) !== state.tier) return false;
      if (q) {
        const hay = `${f.id} ${f.pmid} ${f.doi} ${f.title} ${f.description} ${f.quote} ${f.experimental_system} ${f.location}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function renderFindings() {
    const rows = filteredFindings();
    el("drawer-match-count").textContent = String(rows.length);
    const list = el("findings-list");

    if (rows.length === 0 && state.nodeId === "isoform_switch") {
      list.innerHTML =
        `<div class="finding-row">` +
        `<p class="finding-desc">No Step 1 experimental row is tagged exclusively to protein crystal geometry because Rule C5 excludes structural models from Step 1 workbooks. Click Reset filters or select Stage 2 through Stage 5 to inspect all 120 downstream Step 1 findings.</p>` +
        `</div>`;
      return;
    }

    if (rows.length === 0) {
      list.innerHTML = `<div class="finding-row"><p class="finding-desc">No Step 1 findings match the current filter combination.</p></div>`;
      return;
    }

    list.innerHTML = rows
      .map((f) => {
        const isContra = f.direction === "contradicts";
        const dirClass = isContra ? "dir-contradicts" : "dir-supports";
        const dirLabel = isContra ? "CONTRADICTING" : "SUPPORTS";
        const statParts = [];
        for (const [label, key] of [
          ["Effect", "effect_size"],
          ["P", "p_value"],
          ["N", "sample_size"],
        ]) {
          const val = f[key];
          if (val) {
            const prov = (f.stats && f.stats[key] && f.stats[key].provenance) || "printed_in_text";
            statParts.push(`${label}: ${val} (${prov})`);
          }
        }
        const pmidUrl = f.pmid && f.pmid !== "N/A" ? `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(f.pmid)}/` : "";
        const doiUrl = f.doi && f.doi !== "N/A" ? `https://doi.org/${encodeURI(f.doi)}` : "";
        return `
          <div class="finding-row ${isContra ? "is-contra" : ""}">
            <div class="finding-head">
              <span class="finding-id">${escapeHtml(f.id)} | ${escapeHtml(f.location || "Abstract only")}</span>
              <span class="dir-status ${dirClass}">${dirLabel} (Class ${escapeHtml(f.directness_class)} | d=${escapeHtml(String(f.directness_strength ?? ""))})</span>
            </div>
            <div class="finding-meta">
              ${pmidUrl ? `<a href="${pmidUrl}" target="_blank" rel="noopener">PMID ${escapeHtml(f.pmid)}</a>` : "PMID N/A"}
              ${doiUrl ? ` | <a href="${doiUrl}" target="_blank" rel="noopener">${escapeHtml(f.doi)}</a>` : ""}
              | Tier ${escapeHtml(f.tier)} | ${escapeHtml(String(f.year || ""))} | ${escapeHtml(f.fulltext_source)}
            </div>
            <p class="finding-desc">${escapeHtml(f.description)}</p>
            <blockquote class="finding-quote">"${escapeHtml(f.quote)}"</blockquote>
            <div class="finding-stats">
              <span><strong>Model:</strong> ${escapeHtml(f.experimental_system)}</span>
              ${statParts.length ? `<br /><span><strong>Printed stats:</strong> ${escapeHtml(statParts.join(" ; "))}</span>` : ""}
            </div>
          </div>
        `;
      })
      .join("");
  }

  function bindEvents() {
    document.querySelectorAll("[data-hyp]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.hyp = btn.getAttribute("data-hyp") || "ALL";
        document.querySelectorAll("[data-hyp]").forEach((b) => {
          const on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-selected", on ? "true" : "false");
        });
        updateTopMetrics();
        renderFindings();
      });
    });

    document.querySelectorAll("[data-dir]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.dir = btn.getAttribute("data-dir") || "ALL";
        document.querySelectorAll("[data-dir]").forEach((b) => b.classList.toggle("is-active", b === btn));
        renderFindings();
      });
    });

    el("directness-select").addEventListener("change", (e) => {
      state.directness = e.target.value;
      renderFindings();
    });

    el("tier-select").addEventListener("change", (e) => {
      state.tier = e.target.value;
      renderFindings();
    });

    el("search-input").addEventListener("input", (e) => {
      state.query = e.target.value;
      renderFindings();
    });

    el("btn-all-nodes").addEventListener("click", () => {
      state.nodeId = "ALL";
      renderCascade();
      renderFindings();
    });

    el("btn-clear-filters").addEventListener("click", () => {
      state.hyp = "ALL";
      state.nodeId = "ALL";
      state.dir = "ALL";
      state.directness = "ALL";
      state.tier = "ALL";
      state.query = "";
      el("search-input").value = "";
      el("directness-select").value = "ALL";
      el("tier-select").value = "ALL";
      document.querySelectorAll("[data-hyp]").forEach((b) => {
        const on = b.getAttribute("data-hyp") === "ALL";
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });
      document.querySelectorAll("[data-dir]").forEach((b) => {
        b.classList.toggle("is-active", b.getAttribute("data-dir") === "ALL");
      });
      updateTopMetrics();
      renderCascade();
      renderFindings();
    });

    el("structure-select").addEventListener("change", (e) => {
      state.structureId = e.target.value;
      state.activeResidue = null;
      renderResidueBar();
      renderStructureMeta();
      loadSelectedStructure();
    });

    el("btn-reset-view").addEventListener("click", () => {
      state.activeResidue = null;
      renderResidueBar();
      if (state.viewer && state.viewer.plugin) {
        state.viewer.plugin.managers.camera.reset();
      }
    });
  }

  async function initMolstar() {
    if (!window.molstar || !window.molstar.Viewer) {
      el("molstar-status").textContent = "Mol* CDN unavailable offline; structure metadata active.";
      return;
    }
    try {
      state.viewer = await window.molstar.Viewer.create(el("molstar-container"), {
        layoutIsExpanded: false,
        layoutShowControls: false,
        layoutShowRemoteState: false,
        layoutShowSequence: false,
        layoutShowLog: false,
        layoutShowLeftPanel: false,
        viewportShowExpand: true,
        viewportShowSelectionMode: false,
        viewportShowAnimation: false,
        pdbProvider: "rcsb",
      });
      await loadSelectedStructure();
    } catch (err) {
      el("molstar-status").textContent = `3D viewer initialization error: ${err && err.message ? err.message : err}`;
    }
  }

  async function fetchGunzipText(url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${url}`);
    if (typeof DecompressionStream === "function" && resp.body) {
      const ds = new DecompressionStream("gzip");
      return await new Response(resp.body.pipeThrough(ds)).text();
    }
    throw new Error("DecompressionStream not supported in this browser");
  }

  function parseResidueCoords(cifText) {
    const coords = {};
    const lines = cifText.split(/\r?\n/);
    let i = 0;
    while (i < lines.length) {
      if (lines[i].trim() === "loop_") {
        const cols = [];
        let j = i + 1;
        while (j < lines.length && lines[j].trimStart().startsWith("_")) {
          cols.push(lines[j].trim());
          j++;
        }
        if (cols.length && cols.every((c) => c.startsWith("_atom_site."))) {
          const iAsym = cols.indexOf("_atom_site.auth_asym_id");
          const iSeq = cols.indexOf("_atom_site.auth_seq_id");
          const iAtom = cols.indexOf("_atom_site.auth_atom_id");
          const iX = cols.indexOf("_atom_site.Cartn_x");
          const iY = cols.indexOf("_atom_site.Cartn_y");
          const iZ = cols.indexOf("_atom_site.Cartn_z");
          for (let k = j; k < lines.length; k++) {
            const rs = lines[k].trim();
            if (!rs || rs.startsWith("#") || rs === "loop_" || rs.startsWith("_")) break;
            const tok = rs.split(/\s+/);
            const atom = tok[iAtom];
            const key = `${tok[iAsym]}:${tok[iSeq]}`;
            if (atom === "CA" || !coords[key]) {
              coords[key] = [parseFloat(tok[iX]), parseFloat(tok[iY]), parseFloat(tok[iZ])];
            }
          }
          break;
        }
        i = j;
        continue;
      }
      i++;
    }
    return coords;
  }

  async function loadSelectedStructure() {
    if (!state.viewer) return;
    const st = state.data.structures.find((s) => s.id === state.structureId);
    if (!st) return;
    const seq = ++state.loadSeq;
    el("molstar-status").textContent = `Loading ${st.source_id} (${st.size_kb} KB .cif.gz)...`;
    try {
      const cifText = await fetchGunzipText(`./${st.file}`);
      if (seq !== state.loadSeq) return;
      state.residueCoords = parseResidueCoords(cifText);
      await state.viewer.plugin.clear();
      await state.viewer.loadStructureFromData(cifText, "mmcif", { dataLabel: st.source_id });
      el("molstar-status").textContent = `${st.source_id} loaded (${st.category})`;
      if (st.residues && st.residues.length > 0) {
        const first = st.residues[0];
        focusResidue(first.auth_asym_id, first.auth_seq_id);
      }
    } catch (err) {
      el("molstar-status").textContent = `Load error for ${st.source_id}: ${err && err.message ? err.message : err}`;
    }
  }

  function focusResidue(authAsym, authSeq) {
    if (!state.viewer || !state.viewer.plugin) return;
    const key = `${authAsym}:${authSeq}`;
    const center = state.residueCoords[key];
    try {
      const camera = state.viewer.plugin.managers.camera;
      if (center && camera && typeof camera.focusSphere === "function") {
        camera.focusSphere({ center, radius: 11 }, { durationMs: 320 });
        el("molstar-status").textContent = `Focused ${authAsym}:${authSeq}`;
        return;
      }
    } catch (_err) {}
    el("molstar-status").textContent = `Selected residue ${authAsym}:${authSeq}`;
  }

  init().catch((err) => {
    const status = el("molstar-status");
    if (status) status.textContent = `Startup error: ${err && err.message ? err.message : err}`;
  });
})();
