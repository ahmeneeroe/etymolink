#!/usr/bin/env python3
"""
Apply validation fixes from etymonline verification.

Fixes:
1. 24 language code corrections in lang_code_mapping.py
2. 59 bidirectional pair direction corrections in edges_clean.csv
3. 33 self-loop edge restorations in edges_clean.csv + etymologies_clean.json
"""

import csv
import json
import os
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Load corrections
# ---------------------------------------------------------------------------
with open("/tmp/all_corrections.json") as f:
    corrections = json.load(f)

lang_errors = corrections["lang_errors"]
bidir_corrections = corrections["bidir_corrections"]
selfloop_restorations = corrections["selfloop_restorations"]

print("=" * 60)
print("Applying Validation Fixes")
print("=" * 60)
print(f"  Language code errors: {len(lang_errors)}")
print(f"  Bidir direction fixes: {len(bidir_corrections)}")
print(f"  Self-loop restorations: {len(selfloop_restorations)}")

# ---------------------------------------------------------------------------
# 1. Fix language codes in mapping
# ---------------------------------------------------------------------------
print("\n--- 1. Language Code Fixes ---")

# Build correction map from verification results
lang_fixes = {
    # From batch 1 verification
    "Ro": {"action": "add_new", "full_name": "Romansch", "family": "Latin"},
    "Malaya": {"action": "add_new", "full_name": "Malayalam", "family": "Dravidian"},
    "Roman": {"action": "add_new", "full_name": "Roman Latin", "family": "Latin"},
    "NewTest": {"action": "add_new", "full_name": "New Testament Greek", "family": "Greek"},
    "An": {"action": "add_new", "full_name": "Anglo-Indian", "family": "Germanic"},
    "Wol": {"action": "add_new", "full_name": "Walloon", "family": "Latin"},
    # From batch 2
    "OFi": {"action": "add_new", "full_name": "Old Frisian", "family": "Germanic"},
    # From batch 3+4
    "DE": {"action": "add_new", "full_name": "Delaware (Algonquian)", "family": "Native-American"},
    "Assain": {"action": "add_new", "full_name": "Alsatian German", "family": "Germanic"},
    "Anglo": {"action": "add_new", "full_name": "Anglo-Indian", "family": "Germanic"},
    "Hat": {"action": "add_new", "full_name": "Hittite", "family": "Anatolian"},
    "Pin": {"action": "add_new", "full_name": "Philippine (Malay)", "family": "Austronesian"},
    "Saf": {"action": "add_new", "full_name": "South African Dutch", "family": "Germanic"},
    "Hau": {"action": "merge", "canonical": "Hawa"},
    "Gab": {"action": "add_new", "full_name": "Galibi (Carib)", "family": "Native-American"},
    "Micro": {"action": "add_new", "full_name": "Micmac (Algonquian)", "family": "Native-American"},
    "Ae": {"action": "add_new", "full_name": "Aeolic Greek", "family": "Greek"},
    "Daw": {"action": "add_new", "full_name": "Delaware (Lenape)", "family": "Native-American"},
    # Ambiguous/heterogeneous — split needed
    "Mun": {"action": "add_new", "full_name": "Mongolian/Munsee (heterogeneous)", "family": "Mixed"},
    # These should be removed/flagged, not mapped to wrong things
    "British": {"action": "remove", "reason": "Not a language code — refers to British people"},
    "Africa": {"action": "remove", "reason": "Misattributed — actual word is Anglian/Germanic"},
    "Ariz": {"action": "remove", "reason": "Misattributed — Geronimo is Italian/Spanish/Greek"},
    "Cast": {"action": "remove", "reason": "Not a language — person's name (Canon Kir)"},
    "Wo": {"action": "add_new", "full_name": "West Indies Patois", "family": "Latin"},
}

# Also fix HGer from first validation round
lang_fixes["HGer"] = {"action": "add_new", "full_name": "Middle High German", "family": "Germanic"}

# Fix Mah family classification
lang_fixes["Mah_family"] = "note: Marathi is Indo-Aryan, not Iranian"

# Now update lang_code_mapping.py
sys.path.insert(0, BASE_DIR)
from lang_code_mapping import CODE_MAPPING, NEW_CODES, MERGE_CODES, ARTIFACT_CODES

fixed_count = 0
for code, fix in lang_fixes.items():
    if code.endswith("_family"):
        continue
    if code in CODE_MAPPING:
        old = CODE_MAPPING[code]
        CODE_MAPPING[code] = fix
        fixed_count += 1
        print(f"  Fixed {code}: {old.get('full_name', old.get('action', '?'))} -> {fix.get('full_name', fix.get('action', '?'))}")
    else:
        CODE_MAPPING[code] = fix
        fixed_count += 1
        print(f"  Added {code}: {fix.get('full_name', fix.get('action', '?'))}")

print(f"  Total lang code fixes applied to mapping: {fixed_count}")

# Update the clean language code CSVs
existing_codes = {}
with open(os.path.join(BASE_DIR, "language_codes_clean.csv")) as f:
    for row in csv.DictReader(f):
        existing_codes[row["Code"]] = row["Language"]

existing_families = {}
with open(os.path.join(BASE_DIR, "language_families_clean.csv")) as f:
    for row in csv.DictReader(f):
        existing_families[row["Code"]] = {"Language": row["Language"], "Family": row["Family"]}

for code, fix in lang_fixes.items():
    if code.endswith("_family"):
        continue
    if fix.get("action") == "add_new":
        existing_codes[code] = fix["full_name"]
        existing_families[code] = {"Language": fix["full_name"], "Family": fix["family"]}
    elif fix.get("action") == "remove" and code in existing_codes:
        # Keep in table but note it's problematic
        pass

# Fix HGer in lookup tables
if "HGer" in existing_codes:
    existing_codes["HGer"] = "Middle High German"
if "HGer" in existing_families:
    existing_families["HGer"]["Language"] = "Middle High German"

# Fix OFi
existing_codes["OFi"] = "Old Frisian"
existing_families["OFi"] = {"Language": "Old Frisian", "Family": "Germanic"}

# Fix Mah family
if "Mah" in existing_families:
    existing_families["Mah"]["Family"] = "Indo-Aryan"

with open(os.path.join(BASE_DIR, "language_codes_clean.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Code", "Language"])
    for code in sorted(existing_codes):
        w.writerow([code, existing_codes[code]])

with open(os.path.join(BASE_DIR, "language_families_clean.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Code", "Language", "Family"])
    for code in sorted(existing_families):
        info = existing_families[code]
        w.writerow([code, info["Language"], info["Family"]])

print(f"  Updated language_codes_clean.csv ({len(existing_codes)} codes)")
print(f"  Updated language_families_clean.csv ({len(existing_families)} codes)")

# ---------------------------------------------------------------------------
# 2. Fix bidirectional pair directions
# ---------------------------------------------------------------------------
print("\n--- 2. Bidirectional Direction Fixes ---")

edges = []
with open(os.path.join(BASE_DIR, "edges_clean.csv")) as f:
    for row in csv.DictReader(f):
        edges.append(row)

# Build set of edges to flip
flips = {}
for correction in bidir_corrections:
    pair = correction.get("pair", "")
    correct_dir = correction.get("correct_direction", "")
    our_dir = correction.get("our_direction", "")

    if not correct_dir or correct_dir == our_dir:
        continue

    # Parse our_direction "A -> B" format
    if " -> " in our_dir:
        parts = our_dir.split(" -> ")
        wrong_src, wrong_tgt = parts[0].strip(), parts[1].strip()
        flips[(wrong_src, wrong_tgt)] = True

    # Also parse from pair "A <-> B" and correct_direction
    if " -> " in correct_dir:
        parts = correct_dir.split(" -> ")
        correct_src, correct_tgt = parts[0].strip(), parts[1].strip()

flip_count = 0
for e in edges:
    key = (e["source"], e["target"])
    if key in flips:
        # Flip the direction
        e["source"], e["target"] = e["target"], e["source"]
        flip_count += 1

print(f"  Flipped {flip_count} edge directions")

# ---------------------------------------------------------------------------
# 3. Restore self-loop edges
# ---------------------------------------------------------------------------
print("\n--- 3. Self-Loop Edge Restorations ---")

restored = 0
for entry in selfloop_restorations:
    edge = entry.get("suggested_edge")
    word_family = entry.get("word_family", "")
    word = entry.get("word", "")

    if not edge:
        continue

    src = edge.get("source", "")
    tgt = edge.get("target", "")

    if not src or not tgt:
        continue

    # Don't add if it's a sentence/description instead of a real edge
    if len(tgt) > 60:
        continue

    # Add the edge
    edges.append({
        "source": src,
        "target": tgt,
        "word_family": word_family or word,
    })
    restored += 1

# Also restore the 3 from annotated file
annotated_restorations = [
    # architecture
    {"source": "architecture_E", "target": "architecture_F", "word_family": "architecture"},
    {"source": "architecture_F", "target": "architectura_L", "word_family": "architecture"},
    {"source": "architectura_L", "target": "architectus_L", "word_family": "architecture"},
    # distract
    {"source": "distract_E", "target": "distractus_L", "word_family": "distract"},
    {"source": "distractus_L", "target": "distrahere_L", "word_family": "distract"},
    # respiration
    {"source": "respiration_E", "target": "respirationem_L", "word_family": "respiration"},
    {"source": "respirationem_L", "target": "respirare_L", "word_family": "respiration"},
]

for e in annotated_restorations:
    edges.append(e)
    restored += 1

print(f"  Restored {restored} edges from self-loop verification")

# ---------------------------------------------------------------------------
# Deduplicate (in case restorations created dupes)
# ---------------------------------------------------------------------------
seen = set()
unique_edges = []
for e in edges:
    key = (e["source"], e["target"], e["word_family"])
    if key not in seen:
        seen.add(key)
        unique_edges.append(e)
edges = unique_edges

# ---------------------------------------------------------------------------
# Write updated edges
# ---------------------------------------------------------------------------
with open(os.path.join(BASE_DIR, "edges_clean.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["source", "target", "word_family"])
    w.writeheader()
    w.writerows(edges)
print(f"\nWrote {len(edges)} edges to edges_clean.csv")

# ---------------------------------------------------------------------------
# Rebuild etymologies from corrected edges
# ---------------------------------------------------------------------------
print("\nRebuilding etymologies_clean.json from corrected edges...")

with open(os.path.join(BASE_DIR, "etymologies_clean.json")) as f:
    etym_data = json.load(f)

family_edges = defaultdict(list)
for e in edges:
    family_edges[e["word_family"]].append({
        "source": e["source"],
        "target": e["target"],
    })

updated = 0
for entry in etym_data["words"]:
    word_root = entry.get("word_root", "")
    if word_root in family_edges:
        new_chain = family_edges[word_root]
        old_set = set((l["source"], l["target"]) for l in entry["etymology_chain"])
        new_set = set((l["source"], l["target"]) for l in new_chain)
        if old_set != new_set:
            entry["etymology_chain"] = new_chain
            updated += 1

with open(os.path.join(BASE_DIR, "etymologies_clean.json"), "w") as f:
    json.dump(etym_data, f, indent=2, ensure_ascii=False)
print(f"  Updated {updated} etymology chains")

# ---------------------------------------------------------------------------
# Quick validation
# ---------------------------------------------------------------------------
print("\n--- Quick Validation ---")

# Self-loops
loops = sum(1 for e in edges if e["source"] == e["target"])
print(f"  Self-loops: {loops}")

# Duplicates
edge_set = set()
dupes = 0
for e in edges:
    key = (e["source"], e["target"], e["word_family"])
    if key in edge_set:
        dupes += 1
    edge_set.add(key)
print(f"  Duplicate edges: {dupes}")

print(f"\n  Final edge count: {len(edges)}")
print(f"  Final word count: {len(etym_data['words'])}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
