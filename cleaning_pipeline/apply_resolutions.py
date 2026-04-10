#!/usr/bin/env python3
"""
Apply flagged item resolutions to the clean dataset.

Reads:
  - edges_clean.csv (current clean edges)
  - etymologies_clean.json (current clean word entries)
  - /tmp/etymology_resolutions_1.json, _2.json, _3.json (conflict resolutions from etymonline)
  - /tmp/bidir_resolutions.json (bidirectional pair resolutions)

Writes:
  - edges_clean.csv (updated)
  - etymologies_clean.json (updated)
  - flagged_for_review.csv (cleared/reduced)
"""

import csv
import json
import os
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_conflict_resolutions():
    """Load conflict chain resolutions."""
    path = "/tmp/etymology_resolutions_all.json"
    if os.path.exists(path):
        with open(path) as f:
            resolutions = json.load(f)
            print(f"  Loaded {len(resolutions)} conflict resolutions")
            return resolutions
    print(f"  WARNING: {path} not found")
    return []


def load_bidir_resolutions():
    """Load bidirectional pair resolutions."""
    path = "/tmp/bidir_resolutions.json"
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            print(f"  Loaded {len(data)} bidirectional resolutions")
            return data
    print(f"  WARNING: {path} not found")
    return []


def apply_conflict_resolutions(etym_data, resolutions):
    """Apply conflict chain resolutions to etymologies.json."""
    # Build lookup: word -> chosen chain
    chain_overrides = {}
    for r in resolutions:
        word = r.get("word", "")
        chain = r.get("chosen_chain")
        if word and chain is not None:
            chain_overrides[word] = chain

    updated = 0
    for entry in etym_data["words"]:
        word = entry["word"]
        if word in chain_overrides:
            old_chain = entry["etymology_chain"]
            new_chain = chain_overrides[word]
            # Only update if different
            old_set = set((l["source"], l["target"]) for l in old_chain)
            new_set = set((l["source"], l["target"]) for l in new_chain)
            if old_set != new_set:
                entry["etymology_chain"] = new_chain
                updated += 1

    print(f"  Conflict resolutions applied: {updated}")
    return etym_data


def apply_bidir_resolutions(edges, resolutions):
    """Remove wrong-direction edges for bidirectional pairs."""
    # Build set of edges to remove
    to_remove = set()
    for r in resolutions:
        src = r["remove_source"]
        tgt = r["remove_target"]
        to_remove.add((src, tgt))

    before = len(edges)
    edges = [e for e in edges if (e["source"], e["target"]) not in to_remove]
    removed = before - len(edges)
    print(f"  Bidirectional wrong-direction edges removed: {removed}")
    return edges


def rebuild_etym_from_edges(edges, etym_data):
    """Rebuild etymology chains from the final edge set."""
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

    print(f"  Etymology chains rebuilt from edges: {updated}")
    return etym_data


def main():
    print("=" * 60)
    print("Applying Flagged Item Resolutions")
    print("=" * 60)

    # Load current clean data
    print("\nLoading clean dataset...")
    edges = []
    with open(os.path.join(BASE_DIR, "edges_clean.csv")) as f:
        for row in csv.DictReader(f):
            edges.append(row)
    print(f"  Edges: {len(edges)}")

    with open(os.path.join(BASE_DIR, "etymologies_clean.json")) as f:
        etym_data = json.load(f)
    print(f"  Word entries: {len(etym_data['words'])}")

    # Load resolutions
    print("\nLoading resolutions...")
    conflict_res = load_conflict_resolutions()
    bidir_res = load_bidir_resolutions()

    # Apply conflict resolutions
    print("\nApplying conflict resolutions...")
    etym_data = apply_conflict_resolutions(etym_data, conflict_res)

    # Apply bidirectional resolutions
    print("\nApplying bidirectional resolutions...")
    edges = apply_bidir_resolutions(edges, bidir_res)

    # Rebuild etymology chains from final edges
    print("\nRebuilding etymology chains...")
    etym_data = rebuild_etym_from_edges(edges, etym_data)

    # Write updated files
    print("\nWriting updated files...")
    with open(os.path.join(BASE_DIR, "edges_clean.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "target", "word_family"])
        w.writeheader()
        w.writerows(edges)
    print(f"  Wrote {len(edges)} edges")

    with open(os.path.join(BASE_DIR, "etymologies_clean.json"), "w") as f:
        json.dump(etym_data, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {len(etym_data['words'])} word entries")

    # Clear flagged file (all resolved)
    with open(os.path.join(BASE_DIR, "flagged_for_review.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["reason", "word", "data"])
        w.writeheader()
    print("  Cleared flagged_for_review.csv")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
