#!/usr/bin/env python3
"""Stage compact Model-1 .cif.gz structures and licensing notice into docs/structures/.

Reads pre-fetched RCSB PDB and AlphaFold v6 mmCIF files from the artifact directory,
strips multi-model NMR ensembles (2L7B, 2MOF) to Model 1 only so Mol* loads cleanly and
files stay strictly under pr_review_bundle.py's 2 MB tracked-structure ceiling, and
writes deterministic (mtime=0) gzipped mmCIF files to docs/structures/.
"""
from __future__ import annotations

import argparse
import gzip
import os
import shlex
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT / "out" / "raw_structures"
NOTICE_SRC = ROOT / "out" / "structures" / "ALPHAFOLD_TERMS_NOTICE.txt"
DOCS_STRUCT = ROOT / "docs" / "structures"
MAX_BYTES = 2 * 1024 * 1024

PDB_SPECS = [
    ("pdb/pdb_00001b68.cif", "1b68.cif.gz", False),
    ("pdb/pdb_00001nfn.cif", "1nfn.cif.gz", False),
    ("pdb/pdb_00002l7b.cif", "2l7b_model1.cif.gz", True),
    ("pdb/pdb_00001n7d.cif", "1n7d.cif.gz", False),
    ("pdb/pdb_00003gkh.cif", "3gkh.cif.gz", False),
    ("pdb/pdb_00005xjy.cif", "5xjy.cif.gz", False),
    ("pdb/pdb_00009r8l.cif", "9r8l.cif.gz", False),
    ("pdb/pdb_00002mof.cif", "2mof_model1.cif.gz", True),
]

AF_SPECS = [
    ("af/P02649/AF-P02649-F1-model_v6.cif", "AF-P02649-F1-model_v6.cif.gz"),
    ("af/O15118/AF-O15118-F1-model_v6.cif", "AF-O15118-F1-model_v6.cif.gz"),
    ("af/O95477/AF-O95477-F1-model_v6.cif", "AF-O95477-F1-model_v6.cif.gz"),
    ("af/P01130/AF-P01130-F1-model_v6.cif", "AF-P01130-F1-model_v6.cif.gz"),
    ("af/P13473/AF-P13473-F1-model_v6.cif", "AF-P13473-F1-model_v6.cif.gz"),
    ("af/Q92581/AF-Q92581-F1-model_v6.cif", "AF-Q92581-F1-model_v6.cif.gz"),
]


def strip_to_model1(cif_text: str) -> str:
    """Return mmCIF text keeping only Model 1 rows in _atom_site and _pdbx_nmr_ensemble."""
    lines = cif_text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped == "loop_":
            cols: list[str] = []
            j = i + 1
            while j < n and lines[j].lstrip().startswith("_"):
                cols.append(lines[j].strip())
                j += 1
            if cols and all(c.startswith("_atom_site.") for c in cols):
                try:
                    model_idx = cols.index("_atom_site.pdbx_PDB_model_num")
                except ValueError:
                    model_idx = -1
                out.extend(lines[i:j])
                k = j
                while k < n:
                    row = lines[k]
                    rs = row.strip()
                    if rs.startswith("#") or rs == "loop_" or rs.startswith("_") or rs.startswith("data_"):
                        break
                    if not rs:
                        out.append(row)
                        k += 1
                        continue
                    if model_idx >= 0:
                        tokens = shlex.split(rs) if ("'" in rs or '"' in rs) else rs.split()
                        if len(tokens) > model_idx and tokens[model_idx] == "1":
                            out.append(row)
                    else:
                        out.append(row)
                    k += 1
                i = k
                continue
        out.append(line)
        i += 1
    return "".join(out)


def write_deterministic_gz(text: str, dst: Path) -> int:
    """Write UTF-8 text into a deterministic (mtime=0) gzip file and return byte size."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "wb") as raw_fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_fh, compresslevel=9, mtime=0) as gz:
            gz.write(text.encode("utf-8"))
    size = dst.stat().st_size
    if size >= MAX_BYTES:
        raise ValueError(f"{dst} is {size} bytes (>= {MAX_BYTES})")
    return size


def stage_all(src_root: Path = DEFAULT_SRC, dst_dir: Path = DOCS_STRUCT) -> list[tuple[str, int]]:
    """Stage all PDB and AlphaFold models plus notice text into dst_dir."""
    if not src_root.exists():
        raise FileNotFoundError(f"Structure source dir missing: {src_root}")
    dst_dir.mkdir(parents=True, exist_ok=True)
    staged: list[tuple[str, int]] = []

    for rel, out_name, strip_m1 in PDB_SPECS:
        src = src_root / rel
        if not src.exists():
            raise FileNotFoundError(f"Missing source PDB CIF: {src}")
        txt = src.read_text(encoding="utf-8")
        if strip_m1:
            txt = strip_to_model1(txt)
        sz = write_deterministic_gz(txt, dst_dir / out_name)
        staged.append((out_name, sz))

    for rel, out_name in AF_SPECS:
        src = src_root / rel
        if not src.exists():
            raise FileNotFoundError(f"Missing source AF CIF: {src}")
        txt = src.read_text(encoding="utf-8")
        sz = write_deterministic_gz(txt, dst_dir / out_name)
        staged.append((out_name, sz))

    if NOTICE_SRC.exists():
        shutil.copy2(NOTICE_SRC, dst_dir / "ALPHAFOLD_TERMS_NOTICE.txt")
        staged.append(("ALPHAFOLD_TERMS_NOTICE.txt", (dst_dir / "ALPHAFOLD_TERMS_NOTICE.txt").stat().st_size))

    return staged


def main() -> None:
    ap = argparse.ArgumentParser(description="Stage compact Model-1 .cif.gz structures into docs/structures/")
    ap.add_argument("--src", type=Path, default=Path(os.environ.get("MECCOG_STRUCT_SRC", str(DEFAULT_SRC))))
    ap.add_argument("--dst", type=Path, default=DOCS_STRUCT)
    args = ap.parse_args()
    staged = stage_all(args.src, args.dst)
    for name, sz in staged:
        print(f"staged {name:34s} {sz / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
