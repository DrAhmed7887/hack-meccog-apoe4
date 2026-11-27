#!/usr/bin/env python3
"""Deterministically compile docs/data/explorer_data.json from frozen Step 1 outputs
and staged Model-1 structures under docs/structures/.

Preserves the strict Rule C5 boundary: Step 1 findings & quotes come verbatim from
data/extracted.json (H5) and data/H2/extracted.json (H2), while 3D structure presets,
residue coordinate mappings, and computed atomic distances live strictly in structural
context metadata and are never injected into Step 1 findings.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H5_PATH = ROOT / "data" / "extracted.json"
H2_PATH = ROOT / "data" / "H2" / "extracted.json"
STRUCT_DIR = ROOT / "docs" / "structures"
OUT_PATH = ROOT / "docs" / "data" / "explorer_data.json"

NODES = [
    {
        "id": "isoform_switch",
        "step": 1,
        "short_label": "APOE4 Fold",
        "title": "Arg112–Glu109 Salt Bridge & Arg61 Switch",
        "subtitle": "Cys112 (APOE3) vs Arg112 (APOE4) alters N/C-terminal orientation",
        "hypothesis_focus": ["H5", "H2"],
        "default_structure_id": "1b68",
        "note": "Structural context (PDB 1B68 vs 1NFN & 2L7B). Step 1 sheets test downstream endosomal phenotypes rather than crystal geometry.",
    },
    {
        "id": "receptor_uptake_recycling",
        "step": 2,
        "short_label": "Receptor Recycling",
        "title": "LDLR, ApoER2 & LRP1 Endocytic Recycling",
        "subtitle": "Surface receptor trapping vs APOE lipidation / heparan-sulfate dependence",
        "hypothesis_focus": ["H2"],
        "default_structure_id": "1n7d",
        "note": "H2 focus: includes 38217595 (Fig 4A,B ApoER2/LRP1), 39532095 (CONTRADICTING: LDLR recycling parity), and Christchurch Arg136 protection context.",
    },
    {
        "id": "early_endosome_nhe6_rab5",
        "step": 3,
        "short_label": "Early Endosome & NHE6",
        "title": "NHE6 / SLC9A6 & Rab5+ Early Endosome Arrest",
        "subtitle": "Endosomal pH dysregulation and astrocyte vs in-vivo NHE6 divergence",
        "hypothesis_focus": ["H2", "H5"],
        "default_structure_id": "9r8l",
        "note": "Key mechanistic divergence captured in H2: NHE6 ablation rescues Reelin/ApoER2 recycling and reduces amyloid pathology in neurons/in vivo (PMIDs 30375977, 34617884), whereas APOE4 astrocytes lose NHE6 and require NHE6 restoration (PMID 29946028).",
    },
    {
        "id": "cholesterol_efflux_abca1_npc1",
        "step": 4,
        "short_label": "Cholesterol & ABCA1/NPC1",
        "title": "Endolysosomal Cholesterol Sequestration & Efflux",
        "subtitle": "ABCA1 immobilization, NPC1 lysosomal cholesterol trapping, lipid droplets",
        "hypothesis_focus": ["H5"],
        "default_structure_id": "5xjy",
        "note": "H5 flagship bottleneck: cholesterol accumulates inside late endosomes/lysosomes while surface ABCA1 efflux fails.",
    },
    {
        "id": "lysosomal_clearance_lamp1_abeta",
        "step": 5,
        "short_label": "Lysosome & Aβ Clearance",
        "title": "Lysosomal Deacidification & Impaired Cargo Clearance",
        "subtitle": "LAMP1/LAMP2 expansion, v-ATPase / cathepsin deficits, Aβ42 & proteostasis lag",
        "hypothesis_focus": ["H5"],
        "default_structure_id": "AF-P13473",
        "note": "H5 endpoint: lysosomal pH rise, BMP/sphingolipid accumulation, and slowed Abeta42 / lipid droplet clearance (incl. contradicting neutral/rescue lines).",
    },
]

STRUCTURE_CATALOG = [
    {
        "id": "1b68",
        "label": "APOE4 N-Terminal (PDB 1B68)",
        "category": "Experimental X-Ray (2.00 Å)",
        "file": "structures/1b68.cif.gz",
        "source_id": "PDB:1B68",
        "license": "RCSB PDB CC0",
        "numbering_note": "Mature APOE numbering in auth_seq_id (Arg112 present).",
        "node_ids": ["isoform_switch"],
        "residues": [
            {"label": "Arg112 (APOE4 risk)", "auth_seq_id": 112, "auth_asym_id": "A", "role": "risk"},
            {"label": "Glu109 (salt bridge)", "auth_seq_id": 109, "auth_asym_id": "A", "role": "partner"},
            {"label": "Arg61 (domain switch)", "auth_seq_id": 61, "auth_asym_id": "A", "role": "switch"},
            {"label": "Arg136 (Christchurch)", "auth_seq_id": 136, "auth_asym_id": "A", "role": "protective"},
            {"label": "Arg158 (APOE2 site)", "auth_seq_id": 158, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "1nfn",
        "label": "APOE3 N-Terminal (PDB 1NFN)",
        "category": "Experimental X-Ray (1.80 Å)",
        "file": "structures/1nfn.cif.gz",
        "source_id": "PDB:1NFN",
        "license": "RCSB PDB CC0",
        "numbering_note": "Mature APOE numbering in auth_seq_id (Cys112 baseline).",
        "node_ids": ["isoform_switch"],
        "residues": [
            {"label": "Cys112 (APOE3 WT)", "auth_seq_id": 112, "auth_asym_id": "A", "role": "baseline"},
            {"label": "Glu109", "auth_seq_id": 109, "auth_asym_id": "A", "role": "partner"},
            {"label": "Arg61 (packed to Glu109)", "auth_seq_id": 61, "auth_asym_id": "A", "role": "switch"},
            {"label": "Arg136 (Christchurch)", "auth_seq_id": 136, "auth_asym_id": "A", "role": "protective"},
            {"label": "Arg158", "auth_seq_id": 158, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "2l7b",
        "label": "Full-Length APOE3 (PDB 2L7B Model 1)",
        "category": "Solution NMR (Model 1)",
        "file": "structures/2l7b_model1.cif.gz",
        "source_id": "PDB:2L7B",
        "license": "RCSB PDB CC0",
        "numbering_note": "Mature numbering in auth_seq_id (1–299, engineered monomeric APOE3 mutant F257A/W264R/V269A/L279Q/V287E); note label_seq_id = auth_seq_id + 8 in PDB CIF.",
        "node_ids": ["isoform_switch"],
        "residues": [
            {"label": "Cys112", "auth_seq_id": 112, "auth_asym_id": "A", "role": "baseline"},
            {"label": "Glu109", "auth_seq_id": 109, "auth_asym_id": "A", "role": "partner"},
            {"label": "Arg61", "auth_seq_id": 61, "auth_asym_id": "A", "role": "switch"},
            {"label": "Glu255 (C-term domain)", "auth_seq_id": 255, "auth_asym_id": "A", "role": "cterm"},
        ],
    },
    {
        "id": "AF-P02649",
        "label": "APOE Full-Length (AlphaFold v6)",
        "category": "AlphaFold DB v6 (CC-BY 4.0)",
        "file": "structures/AF-P02649-F1-model_v6.cif.gz",
        "source_id": "AF-P02649-F1",
        "license": "CC-BY 4.0 (EMBL-EBI)",
        "numbering_note": "Full pre-pro sequence (residues 1–18 signal peptide): auth_seq_id = mature + 18 (Cys112 -> 130, Glu109 -> 127, Arg61 -> 79, Arg136 -> 154, Glu255 -> 273).",
        "node_ids": ["isoform_switch"],
        "residues": [
            {"label": "Cys130 (mature Cys112)", "auth_seq_id": 130, "auth_asym_id": "A", "role": "baseline"},
            {"label": "Glu127 (mature Glu109)", "auth_seq_id": 127, "auth_asym_id": "A", "role": "partner"},
            {"label": "Arg79 (mature Arg61)", "auth_seq_id": 79, "auth_asym_id": "A", "role": "switch"},
            {"label": "Arg154 (mature Arg136)", "auth_seq_id": 154, "auth_asym_id": "A", "role": "protective"},
            {"label": "Glu273 (mature Glu255)", "auth_seq_id": 273, "auth_asym_id": "A", "role": "cterm"},
        ],
    },
    {
        "id": "1n7d",
        "label": "LDLR Ectodomain (PDB 1N7D)",
        "category": "Experimental X-Ray (3.70 Å)",
        "file": "structures/1n7d.cif.gz",
        "source_id": "PDB:1N7D",
        "license": "RCSB PDB CC0",
        "numbering_note": "Low-pH endosomal closed conformation of LDLR ectodomain (chain A).",
        "node_ids": ["receptor_uptake_recycling"],
        "residues": [
            {"label": "YWTD beta-propeller core (His562)", "auth_seq_id": 562, "auth_asym_id": "A", "role": "context"},
            {"label": "EGF-A domain (Asp299)", "auth_seq_id": 299, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "AF-P01130",
        "label": "LDLR Full-Length (AlphaFold v6)",
        "category": "AlphaFold DB v6 (CC-BY 4.0)",
        "file": "structures/AF-P01130-F1-model_v6.cif.gz",
        "source_id": "AF-P01130-F1",
        "license": "CC-BY 4.0 (EMBL-EBI)",
        "numbering_note": "Full pre-pro human LDLR_HUMAN (860 aa, includes 21-aa signal peptide).",
        "node_ids": ["receptor_uptake_recycling"],
        "residues": [
            {"label": "YWTD core (His583)", "auth_seq_id": 583, "auth_asym_id": "A", "role": "context"},
            {"label": "EGF-A domain (Asp320)", "auth_seq_id": 320, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "9r8l",
        "label": "NHE6 / SLC9A6 Dimer (PDB 9R8L)",
        "category": "Experimental Cryo-EM",
        "file": "structures/9r8l.cif.gz",
        "source_id": "PDB:9R8L",
        "license": "RCSB PDB CC0",
        "numbering_note": "Human NHE6 homodimer (chains A, B; residues 59–578) regulating early endosomal pH.",
        "node_ids": ["early_endosome_nhe6_rab5"],
        "residues": [
            {"label": "Ion-transport core (Asp292)", "auth_seq_id": 292, "auth_asym_id": "A", "role": "partner"},
            {"label": "Transmembrane interface (Tyr380)", "auth_seq_id": 380, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "AF-Q92581",
        "label": "NHE6 Full-Length (AlphaFold v6)",
        "category": "AlphaFold DB v6 (CC-BY 4.0)",
        "file": "structures/AF-Q92581-F1-model_v6.cif.gz",
        "source_id": "AF-Q92581-F1",
        "license": "CC-BY 4.0 (EMBL-EBI)",
        "numbering_note": "Full-length human SLC9A6 (701 aa) including cytoplasmic C-terminal recycling tail.",
        "node_ids": ["early_endosome_nhe6_rab5"],
        "residues": [
            {"label": "Exchanger Asp292", "auth_seq_id": 292, "auth_asym_id": "A", "role": "partner"},
        ],
    },
    {
        "id": "5xjy",
        "label": "ABCA1 Cholesterol Exporter (PDB 5XJY)",
        "category": "Experimental Cryo-EM",
        "file": "structures/5xjy.cif.gz",
        "source_id": "PDB:5XJY",
        "license": "RCSB PDB CC0",
        "numbering_note": "Full human ABCA1 (chain A, residues 3–2234) mediating APOE lipidation & efflux.",
        "node_ids": ["cholesterol_efflux_abca1_npc1"],
        "residues": [
            {"label": "ECD1 tunnel (Trp590)", "auth_seq_id": 590, "auth_asym_id": "A", "role": "partner"},
            {"label": "NBD1 Walker motif (Lys939)", "auth_seq_id": 939, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "AF-O95477",
        "label": "ABCA1 Full-Length (AlphaFold v6)",
        "category": "AlphaFold DB v6 (CC-BY 4.0)",
        "file": "structures/AF-O95477-F1-model_v6.cif.gz",
        "source_id": "AF-O95477-F1",
        "license": "CC-BY 4.0 (EMBL-EBI)",
        "numbering_note": "Full-length human ABCA1_HUMAN cholesterol/phospholipid transporter (2,261 aa).",
        "node_ids": ["cholesterol_efflux_abca1_npc1"],
        "residues": [
            {"label": "ECD1 Trp590", "auth_seq_id": 590, "auth_asym_id": "A", "role": "partner"},
            {"label": "NBD1 Lys939", "auth_seq_id": 939, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "3gkh",
        "label": "NPC1 N-Terminal Pocket (PDB 3GKH)",
        "category": "Experimental X-Ray (1.81 Å)",
        "file": "structures/3gkh.cif.gz",
        "source_id": "PDB:3GKH",
        "license": "RCSB PDB CC0",
        "numbering_note": "Human NPC1 N-terminal cholesterol-binding domain (residues 23–247).",
        "node_ids": ["cholesterol_efflux_abca1_npc1"],
        "residues": [
            {"label": "Sterol pocket Gln79", "auth_seq_id": 79, "auth_asym_id": "A", "role": "partner"},
            {"label": "Sterol pocket Asn41", "auth_seq_id": 41, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "AF-O15118",
        "label": "NPC1 Full-Length (AlphaFold v6)",
        "category": "AlphaFold DB v6 (CC-BY 4.0)",
        "file": "structures/AF-O15118-F1-model_v6.cif.gz",
        "source_id": "AF-O15118-F1",
        "license": "CC-BY 4.0 (EMBL-EBI)",
        "numbering_note": "Full-length human NPC1 lysosomal cholesterol transporter (1,278 aa).",
        "node_ids": ["cholesterol_efflux_abca1_npc1"],
        "residues": [
            {"label": "Sterol NTD Gln79", "auth_seq_id": 79, "auth_asym_id": "A", "role": "partner"},
            {"label": "SSD transmembrane Pro691", "auth_seq_id": 691, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "AF-P13473",
        "label": "LAMP2 Lysosomal Membrane (AlphaFold v6)",
        "category": "AlphaFold DB v6 (CC-BY 4.0)",
        "file": "structures/AF-P13473-F1-model_v6.cif.gz",
        "source_id": "AF-P13473-F1",
        "license": "CC-BY 4.0 (EMBL-EBI)",
        "numbering_note": "Full-length human LAMP2_HUMAN (410 aa; canonical lysosomal membrane glycoprotein context).",
        "node_ids": ["lysosomal_clearance_lamp1_abeta"],
        "residues": [
            {"label": "TM domain Phe390", "auth_seq_id": 390, "auth_asym_id": "A", "role": "context"},
        ],
    },
    {
        "id": "2mof",
        "label": "LAMP-2A TM Helix (PDB 2MOF Model 1)",
        "category": "Solution NMR (Model 1)",
        "file": "structures/2mof_model1.cif.gz",
        "source_id": "PDB:2MOF",
        "license": "RCSB PDB CC0",
        "numbering_note": "Transmembrane coiled-coil segment (residues 369–410) of human LAMP-2A.",
        "node_ids": ["lysosomal_clearance_lamp1_abeta"],
        "residues": [
            {"label": "Gly384 coiled-coil", "auth_seq_id": 384, "auth_asym_id": "A", "role": "context"},
        ],
    },
]


def parse_cif_atoms(cif_gz: Path) -> tuple[list[dict], list[float], str | None]:
    """Read _atom_site rows and resolution from a .cif.gz file."""
    txt = gzip.decompress(cif_gz.read_bytes()).decode("utf-8")
    lines = txt.splitlines()
    atoms: list[dict] = []
    ca_bfactors: list[float] = []
    res: str | None = None
    m_res = re.search(
        r"(?:_refine\.ls_d_res_high|_em_3d_reconstruction\.resolution)\s+([0-9]+\.[0-9]+|[0-9]+)",
        txt,
    )
    if m_res:
        res = f"{m_res.group(1)} Å"

    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == "loop_":
            cols: list[str] = []
            j = i + 1
            while j < n and lines[j].lstrip().startswith("_"):
                cols.append(lines[j].strip())
                j += 1
            if cols and all(c.startswith("_atom_site.") for c in cols):
                idx = {c: pos for pos, c in enumerate(cols)}
                k = j
                while k < n:
                    rs = lines[k].strip()
                    if not rs or rs.startswith("#") or rs == "loop_" or rs.startswith("_"):
                        break
                    tok = shlex.split(rs) if ("'" in rs or '"' in rs) else rs.split()
                    atom_name = tok[idx["_atom_site.auth_atom_id"]]
                    asym = tok[idx["_atom_site.auth_asym_id"]]
                    seq = int(tok[idx["_atom_site.auth_seq_id"]])
                    comp = tok[idx["_atom_site.auth_comp_id"]]
                    elem = tok[idx["_atom_site.type_symbol"]]
                    x = float(tok[idx["_atom_site.Cartn_x"]])
                    y = float(tok[idx["_atom_site.Cartn_y"]])
                    z = float(tok[idx["_atom_site.Cartn_z"]])
                    b = float(tok[idx["_atom_site.B_iso_or_equiv"]])
                    atoms.append(
                        {
                            "asym": asym,
                            "seq": seq,
                            "comp": comp,
                            "atom": atom_name,
                            "elem": elem,
                            "xyz": (x, y, z),
                            "b": b,
                        }
                    )
                    if atom_name == "CA":
                        ca_bfactors.append(b)
                    k += 1
                break
            i = j
            continue
        i += 1
    return atoms, ca_bfactors, res


def min_heavy_distance(atoms: list[dict], seq1: int, seq2: int, asym: str = "A") -> dict:
    """Compute minimum heavy-atom Euclidean distance (in Angstroms) between two residues."""
    a1 = [a for a in atoms if a["asym"] == asym and a["seq"] == seq1 and a["elem"] != "H"]
    a2 = [a for a in atoms if a["asym"] == asym and a["seq"] == seq2 and a["elem"] != "H"]
    best = (9999.0, "", "", "", "")
    for p in a1:
        px, py, pz = p["xyz"]
        for q in a2:
            d = math.dist((px, py, pz), q["xyz"])
            if d < best[0]:
                best = (d, p["comp"], p["atom"], q["comp"], q["atom"])
    return {
        "distance_A": round(best[0], 2),
        "res1": f"{best[1]}{seq1}.{best[2]}",
        "res2": f"{best[3]}{seq2}.{best[4]}",
    }


def classify_node(hyp: str, f: dict) -> str:
    """Map one Step 1 finding into one of the five causal cascade nodes."""
    text = " ".join(
        str(f.get(k) or "") for k in ("description", "quote", "summary", "experimental_system", "location")
    ).lower()
    if any(k in text for k in ("nhe6", "slc9a6", "rab5", "rab7", "rab11", "endosomal ph", "early endosome")):
        return "early_endosome_nhe6_rab5"
    if any(k in text for k in ("abca1", "npc1", "filipin", "cholesterol", "lipid droplet", "cholesteryl", "lipid efflux", "lipidation", "plaque")):
        return "cholesterol_efflux_abca1_npc1"
    if any(k in text for k in ("apoer2", "lrp1", "lrp-1", "ldlr", "reelin", "receptor", "recycling", "endocytosis", "internaliz", "transferrin")):
        return "receptor_uptake_recycling"
    if any(k in text for k in ("lysosom", "lamp1", "lamp2", "cathepsin", "v-atpase", "aβ", "abeta", "amyloid", "autophag", "degrad", "bafilomycin")):
        return "lysosomal_clearance_lamp1_abeta"
    if any(k in text for k in ("domain interaction", "arg61", "r61t", "salt bridge", "glu109", "arg112", "christchurch", "r136s")):
        return "isoform_switch"
    return "receptor_uptake_recycling" if hyp == "H2" else "lysosomal_clearance_lamp1_abeta"


def build_explorer_data() -> dict:
    """Compile normalized explorer JSON from H5/H2 extracted outputs and staged CIFs."""
    h5 = json.loads(H5_PATH.read_text(encoding="utf-8"))
    h2 = json.loads(H2_PATH.read_text(encoding="utf-8"))

    atom_cache: dict[str, list[dict]] = {}
    structures = []
    for entry in STRUCTURE_CATALOG:
        cif_path = ROOT / "docs" / entry["file"]
        atoms, ca_b, res = parse_cif_atoms(cif_path)
        atom_cache[entry["id"]] = atoms
        present_seqs = {(a["asym"], a["seq"]) for a in atoms}
        for r in entry["residues"]:
            if (r["auth_asym_id"], r["auth_seq_id"]) not in present_seqs:
                raise ValueError(f"Residue {r} missing from {entry['file']}")
        item = dict(entry)
        item["size_kb"] = round(cif_path.stat().st_size / 1024, 1)
        if res:
            item["resolution"] = res
        if entry["id"].startswith("AF-") and ca_b:
            item["mean_plddt"] = round(sum(ca_b) / len(ca_b), 1)
        structures.append(item)

    geometry_metrics = {
        "1b68_Arg112_Glu109": min_heavy_distance(atom_cache["1b68"], 112, 109),
        "1b68_Arg61_Glu109": min_heavy_distance(atom_cache["1b68"], 61, 109),
        "1b68_Arg61_Arg112": min_heavy_distance(atom_cache["1b68"], 61, 112),
        "1nfn_Cys112_Glu109": min_heavy_distance(atom_cache["1nfn"], 112, 109),
        "1nfn_Arg61_Glu109": min_heavy_distance(atom_cache["1nfn"], 61, 109),
        "1nfn_Arg61_Cys112": min_heavy_distance(atom_cache["1nfn"], 61, 112),
        "2l7b_Arg61_Glu255": min_heavy_distance(atom_cache["2l7b"], 61, 255),
        "AF_P02649_Arg79_Glu127": min_heavy_distance(atom_cache["AF-P02649"], 79, 127),
        "AF_P02649_Arg79_Glu273": min_heavy_distance(atom_cache["AF-P02649"], 79, 273),
    }

    findings = []
    papers_summary = []
    stats_by_hyp: dict[str, dict] = {}
    pmids_by_hyp: dict[str, set[str]] = {}

    for hyp_key, data in (("H5", h5), ("H2", h2)):
        n_findings = 0
        n_contra = 0
        n_printed_stats = 0
        ft_count = 0
        t1_count = 0
        pmids_by_hyp[hyp_key] = set()
        for p_idx, p in enumerate(data["papers"], 1):
            pmids_by_hyp[hyp_key].add(str(p.get("pmid") or ""))
            ft_blk = p.get("fulltext") or {}
            is_ft = str(ft_blk.get("status", "")).lower() == "full_text"
            ft_route = str(ft_blk.get("route") or "") if is_ft else "abstract_only"
            if is_ft:
                ft_count += 1
            if str(p.get("tier", "")) == "1":
                t1_count += 1
            papers_summary.append(
                {
                    "hyp": hyp_key,
                    "paper_num": p_idx,
                    "pmid": str(p.get("pmid") or ""),
                    "doi": str(p.get("doi") or ""),
                    "title": str(p.get("title") or ""),
                    "year": p.get("year"),
                    "source_type": str(p.get("source_type") or "PubMed published"),
                    "tier": str(p.get("tier") or "2"),
                    "fulltext_source": ft_route or "abstract_only",
                    "fulltext_status": str(ft_blk.get("status") or "unavailable"),
                    "n_findings": len(p.get("findings", [])),
                }
            )
            for f_idx, f in enumerate(p.get("findings", []), 1):
                n_findings += 1
                direction = str(f.get("direction") or "supports").lower()
                if direction == "contradicts":
                    n_contra += 1
                parsed_stats = {}
                for kind in ("effect_size", "p_value", "sample_size"):
                    blk = f.get(kind) or {}
                    val = blk.get("value") if isinstance(blk, dict) else blk
                    prov = (blk.get("provenance") if isinstance(blk, dict) else None) or ""
                    squote = (blk.get("quote") if isinstance(blk, dict) else None) or ""
                    vs = str(val or "").strip()
                    if val not in (None, "", "N/A"):
                        if prov == "printed_in_text":
                            n_printed_stats += 1
                        parsed_stats[kind] = {
                            "value": vs,
                            "provenance": prov,
                            "quote": str(squote),
                        }
                    else:
                        parsed_stats[kind] = {"value": "", "provenance": "", "quote": ""}
                node_id = classify_node(hyp_key, f)
                findings.append(
                    {
                        "id": f"{hyp_key}-P{p_idx}.F{f_idx}",
                        "hyp": hyp_key,
                        "paper_num": p_idx,
                        "finding_num": f_idx,
                        "node_id": node_id,
                        "pmid": str(p.get("pmid") or ""),
                        "doi": str(p.get("doi") or ""),
                        "title": str(p.get("title") or ""),
                        "year": p.get("year"),
                        "tier": str(p.get("tier") or "2"),
                        "source_type": str(p.get("source_type") or "PubMed published"),
                        "fulltext_source": ft_route or "abstract_only",
                        "direction": direction,
                        "directness_class": str(f.get("directness_class") or "1"),
                        "directness_strength": f.get("directness_strength"),
                        "location": str(f.get("location") or ""),
                        "quote": str(f.get("quote") or ""),
                        "description": str(f.get("description") or ""),
                        "summary": str(f.get("summary") or ""),
                        "experimental_system": str(f.get("experimental_system") or ""),
                        "relevance": str(f.get("relevance") or ""),
                        "effect_size": parsed_stats["effect_size"]["value"],
                        "p_value": parsed_stats["p_value"]["value"],
                        "sample_size": parsed_stats["sample_size"]["value"],
                        "stats": parsed_stats,
                    }
                )
        stats_by_hyp[hyp_key] = {
            "hypothesis_statement": str(data.get("hypothesis_statement") or ""),
            "n_papers": len(data["papers"]),
            "n_findings": n_findings,
            "n_contradicting": n_contra,
            "n_supporting": n_findings - n_contra,
            "n_printed_stats": n_printed_stats,
            "n_fulltext_oa": ft_count,
            "n_tier1": t1_count,
        }

    node_counts = {}
    for nd in NODES:
        nid = nd["id"]
        sub = [x for x in findings if x["node_id"] == nid]
        node_counts[nid] = {
            "total": len(sub),
            "H5": sum(1 for x in sub if x["hyp"] == "H5"),
            "H2": sum(1 for x in sub if x["hyp"] == "H2"),
            "contradicts": sum(1 for x in sub if x["direction"] == "contradicts"),
        }

    shared_pmids = sorted(pmids_by_hyp["H5"] & pmids_by_hyp["H2"])
    unique_pmids = pmids_by_hyp["H5"] | pmids_by_hyp["H2"]

    return {
        "rule_c5_notice": (
            "Companion Visual & Structural Workbench: Step 1 workbooks (H5 v3 & H2 v1) contain strictly "
            "primary experimental quotes, panel locations, and printed_in_text statistics under Rule C5. "
            "PDB and AlphaFold v6 (CC-BY 4.0) 3D structures provide structural context only."
        ),
        "totals": {
            "n_papers_total": sum(v["n_papers"] for v in stats_by_hyp.values()),
            "n_unique_papers": len(unique_pmids),
            "shared_pmids": shared_pmids,
            "n_findings_total": sum(v["n_findings"] for v in stats_by_hyp.values()),
            "n_contradicting_total": sum(v["n_contradicting"] for v in stats_by_hyp.values()),
            "n_printed_stats_total": sum(v["n_printed_stats"] for v in stats_by_hyp.values()),
            "n_structures": len(structures),
        },
        "hypotheses": stats_by_hyp,
        "nodes": [{**nd, "counts": node_counts[nd["id"]]} for nd in NODES],
        "geometry": geometry_metrics,
        "structures": structures,
        "papers": papers_summary,
        "findings": findings,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Compile docs/data/explorer_data.json deterministically")
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    args = ap.parse_args()
    payload = build_explorer_data()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    t = payload["totals"]
    print(
        f"wrote {args.out}: {t['n_papers_total']} papers, {t['n_findings_total']} findings "
        f"({t['n_contradicting_total']} contradicting), {t['n_printed_stats_total']} printed stats, "
        f"{t['n_structures']} structures"
    )


if __name__ == "__main__":
    main()
