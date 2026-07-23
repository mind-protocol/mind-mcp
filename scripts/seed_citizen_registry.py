"""Seed the L4 citizen registry — one-shot migration off citizens/*/profile.json.

After this runs, the registry graph is the source of truth and nothing reads the
profile files again. It is deliberately a separate script and not a fallback
inside the registry: a silent file-then-graph fallback is how two sources of
truth survive for months.

Identity is the Telegram handle, so every citizen needs one. A legacy folder
name is not a Telegram handle and is never assumed to be one — pass the mapping
explicitly:

    python scripts/seed_citizen_registry.py --dry-run
    python scripts/seed_citizen_registry.py --map mechanical_visionary=mechvis
    python scripts/seed_citizen_registry.py --set aurore:tg_user_id=123456789

Citizens without a mapping are reported and skipped, never guessed.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runtime.l4 import citizen_registry as registry  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_PROFILES = PROJECT_ROOT / "citizens"


def read_legacy_profiles(base: Path) -> list[dict]:
    """Read citizens/<handle>/profile.json one last time."""
    if not base.is_dir():
        return []
    citizens = []
    for directory in sorted(base.iterdir()):
        profile_path = directory / "profile.json"
        if not directory.is_dir() or directory.name.startswith(".") or not profile_path.exists():
            continue
        try:
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  !! {directory.name}: unreadable profile ({e}) — skipped")
            continue
        identity = profile.get("identity", {})
        capabilities = profile.get("capabilities", {})
        relationships = profile.get("relationships", {})
        citizens.append({
            "legacy_handle": directory.name,
            "name": identity.get("name") or directory.name,
            "type": identity.get("type", "citizen"),
            "bio": identity.get("bio", ""),
            "social_class": identity.get("class_") or identity.get("social_class"),
            "autonomy_level": capabilities.get("autonomy_level"),
            "supervision_tier": capabilities.get("supervision_tier"),
            "human_partner": next(iter(relationships), None),
            "tg_username": profile.get("tg_username") or identity.get("tg_username"),
            "tg_chat_id": profile.get("telegram_chat_id") or profile.get("tg_chat_id"),
            "tg_user_id": profile.get("telegram_user_id") or profile.get("tg_user_id"),
        })
    return citizens


def parse_overrides(pairs: list[str]) -> dict[str, dict]:
    """Parse --set handle:field=value into {handle: {field: value}}."""
    overrides: dict[str, dict] = {}
    for pair in pairs:
        if ":" not in pair or "=" not in pair:
            raise SystemExit(f"--set expects handle:field=value, got {pair!r}")
        target, assignment = pair.split(":", 1)
        field, value = assignment.split("=", 1)
        overrides.setdefault(target.strip().lstrip("@").lower(), {})[field.strip()] = value.strip()
    return overrides


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--profiles-dir", default=str(LEGACY_PROFILES),
                        help="legacy citizens/ directory to read once (default: ./citizens)")
    parser.add_argument("--map", action="append", default=[], metavar="LEGACY=TG_HANDLE",
                        help="map a legacy folder name to its Telegram handle")
    parser.add_argument("--set", action="append", default=[], metavar="HANDLE:FIELD=VALUE",
                        help="override or add a field on a citizen record")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would be written, write nothing")
    args = parser.parse_args()

    mapping = {}
    for entry in args.map:
        if "=" not in entry:
            raise SystemExit(f"--map expects LEGACY=TG_HANDLE, got {entry!r}")
        legacy, tg_handle = entry.split("=", 1)
        mapping[legacy.strip().lower()] = tg_handle.strip().lstrip("@").lower()
    overrides = parse_overrides(args.set)

    print(f"Registry graph : {registry.REGISTRY_GRAPH} @ {registry.L4_HOST}:{registry.L4_PORT}")
    print(f"Design graph   : {registry.DESIGN_GRAPH} (untouched)")

    profiles = read_legacy_profiles(Path(args.profiles_dir))
    print(f"Legacy profiles: {len(profiles)} found in {args.profiles_dir}\n")

    written, skipped = 0, []
    seen = set()

    for entry in profiles:
        legacy = entry.pop("legacy_handle")
        tg_handle = mapping.get(legacy) or entry.get("tg_username") or legacy
        handle = registry.normalize_handle(tg_handle)
        if not handle:
            skipped.append((legacy, "no usable Telegram handle"))
            continue
        if legacy not in mapping and not entry.get("tg_username"):
            # Le nom de dossier n'est pas une preuve d'identité Telegram. On
            # l'écrit quand même (c'est le seul nom qu'on ait) mais on le dit,
            # pour que la correspondance soit confirmée et pas héritée par défaut.
            print(f"  ?? @{handle}: folder name used as Telegram handle — confirm with --map")

        fields = {k: v for k, v in entry.items() if v not in (None, "")}
        fields.update(overrides.get(handle, {}))
        fields.setdefault("tg_username", handle)
        seen.add(handle)

        print(f"  -> @{handle}  l1={registry.l1_graph_name(handle)}  "
              f"{fields.get('type', 'citizen')}  autonomy={fields.get('autonomy_level')}")
        if not args.dry_run:
            registry.upsert_citizen(handle, **fields)
        written += 1

    # --set on a handle with no legacy profile creates the record outright.
    for handle, fields in overrides.items():
        normalized = registry.normalize_handle(handle)
        if not normalized or normalized in seen:
            continue
        print(f"  -> @{normalized}  l1={registry.l1_graph_name(normalized)}  (from --set)")
        if not args.dry_run:
            registry.upsert_citizen(normalized, **fields)
        written += 1

    for legacy, reason in skipped:
        print(f"  !! {legacy}: {reason} — skipped")

    verb = "would write" if args.dry_run else "wrote"
    print(f"\n{verb} {written} citizen(s), skipped {len(skipped)}.")

    if not args.dry_run:
        registry.invalidate()
        print("\nRegistry now holds:")
        for citizen in registry.list_citizens(citizen_type=None):
            print(f"  @{citizen['handle']:<24} {citizen['l1_graph']:<28} "
                  f"tier={citizen['supervision_tier']} level={citizen['autonomy_level']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
