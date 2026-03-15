"""Export project content to NotebookLM-friendly .txt files.

Groups files to minimize source count while keeping content navigable.
Converts all markdown to plain text. Uses descriptive filenames.
Upsert behavior: overwrites existing exports.
"""

import re
from pathlib import Path


def _strip_markdown(text: str) -> str:
    """Light markdown cleanup — keep structure readable but remove syntax."""
    # Keep content mostly as-is but strip heavy markdown artifacts
    # Remove code block fences but keep content
    text = re.sub(r"```\w*\n?", "", text)
    # Remove image references
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Remove link syntax but keep text
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text


def _read_and_clean(path: Path) -> str:
    """Read a markdown file and return cleaned text."""
    try:
        content = path.read_text(encoding="utf-8")
        return _strip_markdown(content)
    except Exception as e:
        return f"[Error reading {path}: {e}]"


def _concat_files(files: list[Path], separator: str = "\n\n{'='*80}\n\n") -> str:
    """Concatenate multiple files with clear separators."""
    parts = []
    for f in files:
        if f.exists():
            header = f"{'='*80}\nFICHIER: {f.name}\n{'='*80}\n"
            parts.append(header + _read_and_clean(f))
    return "\n\n".join(parts)


def _find_files(root: Path, pattern: str) -> list[Path]:
    """Find files matching glob pattern, sorted by name."""
    return sorted(root.glob(pattern))


def export_notebooklm(target_dir: Path) -> bool:
    """Export project to data/export/notebooklm/ as grouped .txt files."""
    out = target_dir / "data" / "export" / "notebooklm"
    out.mkdir(parents=True, exist_ok=True)

    print(f"Exporting to {out.relative_to(target_dir)}/")

    exported = 0
    skipped = 0

    # -------------------------------------------------------------------------
    # 1. Chapters — one file per chapter (they're long)
    # -------------------------------------------------------------------------
    chapters = _find_files(target_dir, "chapitre_*.md")
    for ch in chapters:
        # chapitre_01.md → "chapitre_01_surface_du_desert.txt" etc.
        name = ch.stem  # chapitre_01
        outfile = out / f"{name}.txt"
        content = _read_and_clean(ch)
        outfile.write_text(content, encoding="utf-8")
        print(f"  ✓ {outfile.name} ({len(content):,} chars)")
        exported += 1

    # -------------------------------------------------------------------------
    # 2. Worldbuilding preparation — grouped
    # -------------------------------------------------------------------------
    wb_files = [
        target_dir / "CONCEPT.md",
        target_dir / "MONDE.md",
        target_dir / "CONTACT.md",
        target_dir / "METIERS.md",
    ]
    wb_existing = [f for f in wb_files if f.exists()]
    if wb_existing:
        content = _concat_files(wb_existing)
        outfile = out / "preparation_worldbuilding.txt"
        outfile.write_text(content, encoding="utf-8")
        print(f"  ✓ {outfile.name} ({len(content):,} chars) [{len(wb_existing)} fichiers]")
        exported += 1

    # -------------------------------------------------------------------------
    # 3. Narrative preparation — grouped
    # -------------------------------------------------------------------------
    narr_files = [
        target_dir / "PERSONNAGES.md",
        target_dir / "STRUCTURE.md",
        target_dir / "SQUELETTE.md",
    ]
    narr_existing = [f for f in narr_files if f.exists()]
    if narr_existing:
        content = _concat_files(narr_existing)
        outfile = out / "preparation_narration.txt"
        outfile.write_text(content, encoding="utf-8")
        print(f"  ✓ {outfile.name} ({len(content):,} chars) [{len(narr_existing)} fichiers]")
        exported += 1

    # -------------------------------------------------------------------------
    # 4. Taxonomy + Mapping — grouped
    # -------------------------------------------------------------------------
    ref_files = [
        target_dir / "docs" / "TAXONOMY.md",
        target_dir / "docs" / "MAPPING.md",
    ]
    ref_existing = [f for f in ref_files if f.exists()]
    if ref_existing:
        content = _concat_files(ref_existing)
        outfile = out / "reference_taxonomie_et_mapping.txt"
        outfile.write_text(content, encoding="utf-8")
        print(f"  ✓ {outfile.name} ({len(content):,} chars) [{len(ref_existing)} fichiers]")
        exported += 1

    # -------------------------------------------------------------------------
    # 5. Doc chains — one file per module (8 docs → 1 txt)
    # -------------------------------------------------------------------------
    docs_dir = target_dir / "docs"
    if docs_dir.exists():
        # Find all module directories (contain OBJECTIVES_*.md or PATTERNS_*.md)
        module_dirs = set()
        for obj_file in docs_dir.rglob("OBJECTIVES_*.md"):
            module_dirs.add(obj_file.parent)
        for pat_file in docs_dir.rglob("PATTERNS_*.md"):
            module_dirs.add(pat_file.parent)

        # Chain order for readable concatenation
        chain_order = [
            "OBJECTIVES", "PATTERNS", "BEHAVIORS", "ALGORITHM",
            "VALIDATION", "IMPLEMENTATION", "HEALTH", "SYNC",
        ]

        for mod_dir in sorted(module_dirs):
            # Build relative module name: docs/worldbuilding/contact → worldbuilding_contact
            rel = mod_dir.relative_to(docs_dir)
            module_name = str(rel).replace("/", "_").replace("\\", "_")

            # Collect files in chain order
            mod_files = []
            for prefix in chain_order:
                matches = sorted(mod_dir.glob(f"{prefix}_*.md"))
                mod_files.extend(matches)
            # Add any remaining .md files not caught by chain order
            all_md = set(mod_dir.glob("*.md"))
            remaining = sorted(all_md - set(mod_files))
            mod_files.extend(remaining)

            if mod_files:
                content = _concat_files(mod_files)
                outfile = out / f"docchain_{module_name}.txt"
                outfile.write_text(content, encoding="utf-8")
                print(f"  ✓ {outfile.name} ({len(content):,} chars) [{len(mod_files)} fichiers]")
                exported += 1

    # -------------------------------------------------------------------------
    # 6. Images — copy as-is (NotebookLM supports images)
    # -------------------------------------------------------------------------
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
    for ext in image_exts:
        for img in target_dir.rglob(f"*{ext}"):
            # Skip .mind/ and data/ directories
            rel = img.relative_to(target_dir)
            parts = rel.parts
            if parts[0] in (".mind", "data", "node_modules", ".git"):
                continue
            import shutil
            outfile = out / f"image_{img.stem}{img.suffix}"
            shutil.copy2(img, outfile)
            print(f"  ✓ {outfile.name} (image)")
            exported += 1

    # -------------------------------------------------------------------------
    # 7. README if exists
    # -------------------------------------------------------------------------
    readme = target_dir / "README.md"
    if readme.exists():
        content = _read_and_clean(readme)
        outfile = out / "readme.txt"
        outfile.write_text(content, encoding="utf-8")
        print(f"  ✓ {outfile.name} ({len(content):,} chars)")
        exported += 1

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    total_chars = sum(f.stat().st_size for f in out.iterdir() if f.is_file())
    print(f"\n✓ Export: {exported} fichiers, {total_chars:,} chars total")
    print(f"  Destination: {out.relative_to(target_dir)}/")
    return True
