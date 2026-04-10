#!/usr/bin/env python3
"""
EtymoLink Dataset Cleaning Pipeline

Reads the raw dataset files, applies corrections in a defined order,
validates the result, and writes clean output files.

Steps:
  1. Expand language code lookup tables
  2. Fix malformed node identifiers
  3. Resolve _href artifacts
  4. Deduplicate edges
  5. Deduplicate word entries in etymologies.json
  6. Fix graph cycles
  7. Clean annotated_formatted.csv
  8. Reconcile across files
  9. Validate
"""

import csv
import json
import re
import sys
import os
from collections import Counter, defaultdict
from copy import deepcopy

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EDGES_FILE = os.path.join(BASE_DIR, "edges.csv")
ETYM_FILE = os.path.join(BASE_DIR, "etymologies.json")
ANNOT_FILE = os.path.join(BASE_DIR, "annotated_formatted.csv")
LANG_CODES_FILE = os.path.join(BASE_DIR, "language_codes.csv")
LANG_FAMILIES_FILE = os.path.join(BASE_DIR, "language_families.csv")

# Output files
OUT_EDGES = os.path.join(BASE_DIR, "edges_clean.csv")
OUT_ETYM = os.path.join(BASE_DIR, "etymologies_clean.json")
OUT_ANNOT = os.path.join(BASE_DIR, "annotated_formatted_clean.csv")
OUT_LANG_CODES = os.path.join(BASE_DIR, "language_codes_clean.csv")
OUT_LANG_FAMILIES = os.path.join(BASE_DIR, "language_families_clean.csv")
OUT_LOG = os.path.join(BASE_DIR, "cleaning_log.json")
OUT_FLAGGED = os.path.join(BASE_DIR, "flagged_for_review.csv")

# Import language code mapping
sys.path.insert(0, BASE_DIR)
from lang_code_mapping import CODE_MAPPING, NEW_CODES, MERGE_CODES, ARTIFACT_CODES

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
cleaning_log = []

def log(step, action, detail, old_val=None, new_val=None):
    entry = {"step": step, "action": action, "detail": detail}
    if old_val is not None:
        entry["old"] = str(old_val)
    if new_val is not None:
        entry["new"] = str(new_val)
    cleaning_log.append(entry)

flagged_rows = []

def flag(reason, word=None, data=None):
    row = {"reason": reason}
    if word:
        row["word"] = word
    if data:
        row["data"] = str(data)
    flagged_rows.append(row)

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def extract_lang_code(node):
    """Extract language code from 'word_LANG' format."""
    if not node or not isinstance(node, str):
        return None, None
    node = node.strip()
    idx = node.rfind("_")
    if idx == -1:
        return node, None
    word_part = node[:idx]
    code = node[idx + 1:].rstrip(",").strip()
    return word_part, code if code else None


def rebuild_node(word_part, code):
    """Rebuild a node identifier from word part and language code."""
    if code:
        return f"{word_part}_{code}"
    return word_part


# Language chronology for cycle resolution (higher = older)
LANG_EPOCH = {
    "PIE": 100, "IndoIr": 95,
    "PI": 90, "PGer": 90,
    "San": 85, "Avest": 85,
    "OL": 80, "preL": 80,
    "G": 75, "EG": 75, "LateG": 73, "MediG": 71, "ByG": 71,
    "L": 70, "VL": 68, "LateL": 67, "ChuL": 66, "MediL": 65, "AL": 64,
    "OE": 60, "OHGer": 60, "ONor": 60, "OFri": 60, "WGer": 60,
    "Fran": 58,
    "OF": 55, "ONF": 55, "OPro": 55,
    "MF": 45,
    "ModL": 40, "ModG": 40,
    "F": 30, "AF": 30,
    "Ger": 25, "Dut": 25, "Span": 25, "I": 25, "Por": 25,
    "E": 10,
}


def get_epoch(code):
    """Get chronological epoch for a language code. Higher = older."""
    if code in LANG_EPOCH:
        return LANG_EPOCH[code]
    # Guess from prefixes
    if code and code.startswith("O"):
        return 60  # Old-anything
    if code and code.startswith("P") and code not in ("Per", "Pol", "Por"):
        return 90  # Proto-anything
    if code and code.startswith("Medi"):
        return 65
    if code and code.startswith("Late"):
        return 67
    if code and code.startswith("Mod"):
        return 40
    return 50  # Unknown — middle of the road


# ---------------------------------------------------------------------------
# STEP 1: Expand language code lookup tables
# ---------------------------------------------------------------------------
def step1_expand_lang_codes():
    print("Step 1: Expanding language code lookup tables...")

    # Load existing
    existing_codes = {}
    with open(LANG_CODES_FILE, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            existing_codes[row["Code"]] = row["Language"]

    existing_families = {}
    with open(LANG_FAMILIES_FILE) as f:
        for row in csv.DictReader(f):
            existing_families[row["Code"]] = {
                "Language": row["Language"],
                "Family": row["Family"],
            }

    added = 0
    for code, info in NEW_CODES.items():
        if code not in existing_codes:
            existing_codes[code] = info["full_name"]
            existing_families[code] = {
                "Language": info["full_name"],
                "Family": info["family"],
            }
            log(1, "add_lang_code", f"Added {code} = {info['full_name']} ({info['family']})")
            added += 1

    # Write clean lookup tables
    with open(OUT_LANG_CODES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Code", "Language"])
        for code in sorted(existing_codes):
            w.writerow([code, existing_codes[code]])

    with open(OUT_LANG_FAMILIES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Code", "Language", "Family"])
        for code in sorted(existing_families):
            info = existing_families[code]
            w.writerow([code, info["Language"], info["Family"]])

    print(f"  Added {added} new language codes. Total: {len(existing_codes)}")
    return existing_codes, existing_families


# ---------------------------------------------------------------------------
# Load edges
# ---------------------------------------------------------------------------
def load_edges():
    """Load edges.csv into a list of dicts."""
    edges = []
    with open(EDGES_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append({
                "source": row["source"].strip(),
                "target": row["target"].strip(),
                "word_family": row["word_family"].strip(),
            })
    return edges


# ---------------------------------------------------------------------------
# STEP 2: Fix malformed node identifiers
# ---------------------------------------------------------------------------
def step2_fix_identifiers(edges):
    print("Step 2: Fixing malformed node identifiers...")

    rename_map = {}  # old_node -> new_node
    fixes = Counter()

    # Collect all nodes
    all_nodes = set()
    for e in edges:
        all_nodes.add(e["source"])
        all_nodes.add(e["target"])

    # Build neighbor context for inference
    node_neighbors = defaultdict(set)
    for e in edges:
        node_neighbors[e["source"]].add(e["target"])
        node_neighbors[e["target"]].add(e["source"])

    for node in sorted(all_nodes):
        word_part, code = extract_lang_code(node)
        new_node = None

        # 2a: Trailing commas (ad_L, -> ad_L)
        if node.endswith(","):
            new_node = node.rstrip(",")
            fixes["trailing_comma"] += 1
            log(2, "fix_trailing_comma", f"Stripped trailing comma", node, new_node)

        # 2b: Infinite-loop nodes
        elif "Austro-_Austro-_Aurora" in node:
            new_node = "Austro-"  # Will need a lang code — handled below
            fixes["infinite_loop"] += 1
            log(2, "fix_infinite_loop", "Fixed infinite-loop parse artifact", node, new_node)

        # 2c: Nodes with E/... or similar infinite-loop patterns
        elif code and ("/" in code or code in ARTIFACT_CODES):
            # These are artifact codes — we'll handle in step 3
            continue

        # 2d: Merge variant language codes
        elif code and code in MERGE_CODES:
            canonical = MERGE_CODES[code]
            new_node = rebuild_node(word_part, canonical)
            fixes["merge_code"] += 1
            log(2, "merge_lang_code", f"Merged {code} -> {canonical}", node, new_node)

        # 2e: Fix case typos in codes
        elif code and code.lower() != code and code not in NEW_CODES and code not in existing_codes_global:
            # Check if lowercase/proper case version exists
            for known in list(existing_codes_global.keys()) + list(NEW_CODES.keys()):
                if code.lower() == known.lower() and code != known:
                    new_node = rebuild_node(word_part, known)
                    fixes["case_typo"] += 1
                    log(2, "fix_case_typo", f"Fixed case: {code} -> {known}", node, new_node)
                    break

        # 2f: Trailing underscores (empty code)
        elif node.endswith("_") and not code:
            # Infer code from context
            inferred = infer_lang_code(node.rstrip("_"), node_neighbors.get(node, set()))
            new_node = f"{node.rstrip('_')}_{inferred}"
            fixes["empty_code_inferred"] += 1
            log(2, "infer_empty_code", f"Inferred code {inferred} for trailing underscore", node, new_node)

        # 2g: Reconstructed forms tagged _E
        elif code == "E" and word_part and word_part.startswith("*"):
            inferred = infer_lang_code(word_part, node_neighbors.get(node, set()))
            if inferred != "E":
                new_node = rebuild_node(word_part, inferred)
                fixes["reconstructed_E"] += 1
                log(2, "fix_reconstructed_E", f"Reconstructed form: {code} -> {inferred}", node, new_node)

        # 2h: Truncated POS markers
        elif "(" in node and not node_has_balanced_parens(node):
            fixed = fix_truncated_pos(node)
            if fixed and fixed != node:
                new_node = fixed
                fixes["truncated_pos"] += 1
                log(2, "fix_truncated_pos", "Fixed truncated POS marker", node, new_node)

        if new_node and new_node != node:
            rename_map[node] = new_node

    # Apply renames
    renamed_count = apply_renames(edges, rename_map)

    print(f"  Fixes: {dict(fixes)}")
    print(f"  Total renames applied: {renamed_count}")
    return rename_map


def node_has_balanced_parens(node):
    """Check if parentheses are balanced in a node."""
    depth = 0
    for ch in node:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


def fix_truncated_pos(node):
    """Fix truncated POS markers like 'better (adj.' -> 'better (adj.)_E'"""
    # Common POS patterns
    pos_patterns = [
        r"\(n\.\d*$", r"\(v\.\d*$", r"\(adj\.\d*$", r"\(adv\.\d*$",
        r"\(prep\.$", r"\(conj\.$", r"\(interj\.$",
    ]
    for pat in pos_patterns:
        if re.search(pat, node):
            # Close the paren and add _E
            return node + ")_E"
    # Generic: unclosed paren at end
    if node.count("(") > node.count(")"):
        # Try to close it
        return node + ")_E"
    return None


def infer_lang_code(word_part, neighbors):
    """Infer language code from word form and graph neighbors."""
    # If starts with *, it's reconstructed
    if word_part.startswith("*"):
        # Check neighbors for clues
        neighbor_codes = []
        for n in neighbors:
            _, nc = extract_lang_code(n)
            if nc:
                neighbor_codes.append(nc)

        if neighbor_codes:
            code_counts = Counter(neighbor_codes)
            # If all neighbors are one code, use that
            if len(code_counts) == 1:
                return code_counts.most_common(1)[0][0]
            # If PIE is among neighbors, this is probably PIE too
            if "PIE" in code_counts:
                return "PIE"
            # Use the "oldest" neighbor language
            oldest_code = max(neighbor_codes, key=lambda c: get_epoch(c))
            return oldest_code

        # Default for reconstructed forms
        return "PIE"

    # Non-reconstructed: check neighbors
    neighbor_codes = []
    for n in neighbors:
        _, nc = extract_lang_code(n)
        if nc:
            neighbor_codes.append(nc)

    if neighbor_codes:
        code_counts = Counter(neighbor_codes)
        # Return most common neighbor code
        return code_counts.most_common(1)[0][0]

    return "E"  # Default to English


def apply_renames(edges, rename_map):
    """Apply node renames to all edges."""
    count = 0
    for e in edges:
        for field in ["source", "target"]:
            old = e[field]
            if old in rename_map:
                e[field] = rename_map[old]
                count += 1
        # Also rename word_family if it matches
        if e["word_family"] in rename_map:
            e["word_family"] = rename_map[e["word_family"]]
    return count


# ---------------------------------------------------------------------------
# STEP 3: Resolve _href artifacts
# ---------------------------------------------------------------------------
def step3_resolve_href(edges):
    print("Step 3: Resolving _href and artifact nodes...")

    # Collect all valid nodes (non-artifact)
    valid_nodes = set()
    artifact_edges = []
    clean_edges = []

    for e in edges:
        _, sc = extract_lang_code(e["source"])
        _, tc = extract_lang_code(e["target"])
        if sc in ARTIFACT_CODES or tc in ARTIFACT_CODES:
            artifact_edges.append(e)
        else:
            valid_nodes.add(e["source"])
            valid_nodes.add(e["target"])
            clean_edges.append(e)

    # Build lookup: word_root -> set of valid nodes
    root_to_nodes = defaultdict(set)
    for node in valid_nodes:
        wp, _ = extract_lang_code(node)
        if wp:
            root_to_nodes[wp].add(node)

    # Try to resolve artifact edges
    resolved = 0
    unresolved = 0
    removed = 0

    for e in artifact_edges:
        src_wp, src_code = extract_lang_code(e["source"])
        tgt_wp, tgt_code = extract_lang_code(e["target"])

        new_src = e["source"]
        new_tgt = e["target"]
        resolvable = True

        # Resolve source if artifact
        if src_code in ARTIFACT_CODES:
            if src_wp and f"{src_wp}_E" in valid_nodes:
                new_src = f"{src_wp}_E"
            elif src_wp and root_to_nodes.get(src_wp):
                new_src = sorted(root_to_nodes[src_wp])[0]
            else:
                resolvable = False

        # Resolve target if artifact
        if tgt_code in ARTIFACT_CODES:
            if tgt_wp and f"{tgt_wp}_E" in valid_nodes:
                new_tgt = f"{tgt_wp}_E"
            elif tgt_wp and root_to_nodes.get(tgt_wp):
                new_tgt = sorted(root_to_nodes[tgt_wp])[0]
            else:
                resolvable = False

        if resolvable and new_src != new_tgt:
            e["source"] = new_src
            e["target"] = new_tgt
            clean_edges.append(e)
            resolved += 1
            log(3, "resolve_href", f"Resolved artifact edge",
                f"{e['source']}->{e['target']}", f"{new_src}->{new_tgt}")
        else:
            removed += 1
            log(3, "remove_artifact_edge", f"Removed unresolvable artifact edge",
                f"{e['source']}->{e['target']}")

    print(f"  Artifact edges found: {len(artifact_edges)}")
    print(f"  Resolved: {resolved}, Removed: {removed}")

    return clean_edges


# ---------------------------------------------------------------------------
# STEP 4: Deduplicate edges
# ---------------------------------------------------------------------------
def step4_dedup_edges(edges):
    print("Step 4: Deduplicating edges...")
    before = len(edges)
    seen = set()
    unique = []
    dupes = 0
    for e in edges:
        key = (e["source"], e["target"], e["word_family"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
        else:
            dupes += 1

    log(4, "dedup_edges", f"Removed {dupes} duplicate edges")
    print(f"  Before: {before}, After: {len(unique)}, Removed: {dupes}")
    return unique


# ---------------------------------------------------------------------------
# STEP 5: Deduplicate word entries in etymologies.json
# ---------------------------------------------------------------------------
def step5_dedup_words(edges, rename_map):
    print("Step 5: Deduplicating word entries in etymologies.json...")

    with open(ETYM_FILE) as f:
        data = json.load(f)

    words = data["words"]
    print(f"  Total entries: {len(words)}")

    # Apply renames to etymology chains
    for entry in words:
        # Rename the word field itself
        if entry["word"] in rename_map:
            entry["word"] = rename_map[entry["word"]]

        # Rename nodes in chains
        for link in entry["etymology_chain"]:
            for field in ["source", "target"]:
                if link[field] in rename_map:
                    link[field] = rename_map[link[field]]

    # Group by word
    word_groups = defaultdict(list)
    for entry in words:
        word_groups[entry["word"]].append(entry)

    # Deduplicate
    deduped = []
    pure_dupes = 0
    conflicts = 0
    merged = 0

    for word, entries in word_groups.items():
        if len(entries) == 1:
            deduped.append(entries[0])
            continue

        # Check if all chains are identical
        chains = [
            frozenset((l["source"], l["target"]) for l in e["etymology_chain"])
            for e in entries
        ]
        unique_chains = list(set(chains))

        if len(unique_chains) == 1:
            # Pure duplicates
            deduped.append(entries[0])
            pure_dupes += len(entries) - 1
            log(5, "dedup_pure", f"Removed {len(entries)-1} pure duplicate(s) of {word}")
            continue

        # Conflicting chains — try resolution strategies
        resolved = resolve_chain_conflict(word, entries)
        if resolved:
            deduped.append(resolved)
            merged += 1
        else:
            # Keep first, flag for review
            deduped.append(entries[0])
            conflicts += 1
            flag(
                "conflicting_etymology_chains",
                word=word,
                data={
                    "num_variants": len(entries),
                    "chains": [e["etymology_chain"] for e in entries],
                },
            )

    print(f"  Pure duplicates removed: {pure_dupes}")
    print(f"  Conflicts merged: {merged}")
    print(f"  Conflicts flagged for review: {conflicts}")

    return {"words": deduped}


def resolve_chain_conflict(word, entries):
    """Try to resolve conflicting chains. Returns merged entry or None."""
    chains = [
        set((l["source"], l["target"]) for l in e["etymology_chain"])
        for e in entries
    ]

    # Strategy 1: subset/superset — keep the longest
    sorted_by_len = sorted(zip(chains, entries), key=lambda x: len(x[0]), reverse=True)
    longest_chain, longest_entry = sorted_by_len[0]

    is_superset = all(c.issubset(longest_chain) for c, _ in sorted_by_len[1:])
    if is_superset:
        log(5, "resolve_superset", f"Kept longest chain for {word} ({len(longest_chain)} edges)")
        return longest_entry

    # Strategy 2: merge overlapping chains
    all_edges = set()
    for c in chains:
        all_edges |= c

    # Check if the union forms a reasonable DAG (no cycles)
    if not has_cycle_in_edges(all_edges):
        merged_entry = deepcopy(entries[0])
        merged_entry["etymology_chain"] = [
            {"source": s, "target": t} for s, t in sorted(all_edges)
        ]
        log(5, "resolve_merge", f"Merged {len(chains)} chains for {word} ({len(all_edges)} edges)")
        return merged_entry

    # Can't auto-resolve
    return None


def has_cycle_in_edges(edge_set):
    """Check if a set of (source, target) pairs contains a cycle."""
    adj = defaultdict(set)
    nodes = set()
    for s, t in edge_set:
        adj[s].add(t)
        nodes.add(s)
        nodes.add(t)

    visited = set()
    in_stack = set()

    def dfs(node):
        visited.add(node)
        in_stack.add(node)
        for nb in adj.get(node, []):
            if nb in in_stack:
                return True
            if nb not in visited:
                if dfs(nb):
                    return True
        in_stack.discard(node)
        return False

    for node in nodes:
        if node not in visited:
            if dfs(node):
                return True
    return False


# ---------------------------------------------------------------------------
# STEP 6: Fix graph cycles
# ---------------------------------------------------------------------------
def step6_fix_cycles(edges):
    print("Step 6: Fixing graph cycles...")

    # 6a: Remove self-loops
    before = len(edges)
    non_loops = []
    loop_count = 0
    for e in edges:
        if e["source"] == e["target"]:
            loop_count += 1
            log(6, "remove_self_loop", f"Removed self-loop", e["source"])
        else:
            non_loops.append(e)
    edges = non_loops
    print(f"  Self-loops removed: {loop_count}")

    # 6b: Find and fix bidirectional edges
    edge_pairs = defaultdict(list)
    for i, e in enumerate(edges):
        pair = tuple(sorted([e["source"], e["target"]]))
        edge_pairs[pair].append((i, e["source"], e["target"]))

    bidir_fixes = 0
    remove_indices = set()
    for pair, occurrences in edge_pairs.items():
        directions = set()
        for idx, src, tgt in occurrences:
            directions.add((src, tgt))
        if len(directions) <= 1:
            continue

        # Bidirectional! Fix using chronology
        node_a, node_b = pair
        _, code_a = extract_lang_code(node_a)
        _, code_b = extract_lang_code(node_b)
        epoch_a = get_epoch(code_a) if code_a else 50
        epoch_b = get_epoch(code_b) if code_b else 50

        # Correct direction: younger derives from older (younger_source -> older_target)
        if epoch_a != epoch_b:
            # Keep: younger -> older
            if epoch_a < epoch_b:
                correct = (node_a, node_b)  # A is younger, derives from B (older)
            else:
                correct = (node_b, node_a)  # B is younger, derives from A (older)
        else:
            # Same epoch — flag for review, keep first occurrence
            flag("bidirectional_same_epoch", word=f"{node_a} <-> {node_b}")
            correct = (occurrences[0][1], occurrences[0][2])

        for idx, src, tgt in occurrences:
            if (src, tgt) != correct:
                remove_indices.add(idx)
                bidir_fixes += 1
                log(6, "fix_bidirectional", f"Removed wrong-direction edge",
                    f"{src}->{tgt}", f"Kept {correct[0]}->{correct[1]}")

    edges = [e for i, e in enumerate(edges) if i not in remove_indices]
    print(f"  Bidirectional edges fixed: {bidir_fixes}")

    # 6c: Iteratively find and break remaining cycles
    iteration = 0
    max_iterations = 10
    while iteration < max_iterations:
        remaining_cycles = find_cycles(edges, max_cycles=20)
        if not remaining_cycles:
            print(f"  No remaining cycles after {iteration} iteration(s).")
            break
        print(f"  Iteration {iteration + 1}: {len(remaining_cycles)} cycles found")
        for cycle in remaining_cycles:
            worst_edge = find_worst_chronology_edge(cycle)
            if worst_edge:
                edges = [e for e in edges
                         if not (e["source"] == worst_edge[0]
                                 and e["target"] == worst_edge[1])]
                log(6, "break_cycle", f"Removed edge to break cycle",
                    f"{worst_edge[0]}->{worst_edge[1]}", str(cycle))
            else:
                # Last resort: remove the first edge in the cycle
                src, tgt = cycle[0], cycle[1]
                edges = [e for e in edges
                         if not (e["source"] == src and e["target"] == tgt)]
                log(6, "break_cycle_forced",
                    f"Force-removed first edge to break cycle",
                    f"{src}->{tgt}", str(cycle))
        iteration += 1
    else:
        # Hit max iterations
        remaining = find_cycles(edges, max_cycles=5)
        if remaining:
            for cycle in remaining:
                flag("unresolvable_cycle", data=cycle)

    print(f"  Edges after cycle fixes: {len(edges)}")
    return edges


def find_cycles(edges, max_cycles=50):
    """Find cycles in the edge graph using DFS."""
    adj = defaultdict(set)
    for e in edges:
        adj[e["source"]].add(e["target"])

    visited = set()
    in_stack = set()
    cycles = []

    def dfs(node, path):
        if len(cycles) >= max_cycles:
            return
        visited.add(node)
        in_stack.add(node)
        path.append(node)
        for nb in adj.get(node, set()):
            if nb in in_stack:
                # Found cycle
                cycle_start = path.index(nb)
                cycle = path[cycle_start:] + [nb]
                cycles.append(cycle)
            elif nb not in visited:
                dfs(nb, path)
        path.pop()
        in_stack.discard(node)

    all_nodes = set()
    for e in edges:
        all_nodes.add(e["source"])
        all_nodes.add(e["target"])

    for node in sorted(all_nodes):
        if node not in visited:
            dfs(node, [])
        if len(cycles) >= max_cycles:
            break

    return cycles


def find_worst_chronology_edge(cycle):
    """Find the edge in a cycle that most violates chronological order."""
    # cycle is [node1, node2, ..., node1]
    worst = None
    worst_score = 0
    for i in range(len(cycle) - 1):
        src = cycle[i]
        tgt = cycle[i + 1]
        _, src_code = extract_lang_code(src)
        _, tgt_code = extract_lang_code(tgt)
        src_epoch = get_epoch(src_code) if src_code else 50
        tgt_epoch = get_epoch(tgt_code) if tgt_code else 50
        # In correct edge: src is younger (lower epoch), tgt is older (higher epoch)
        # Violation: src is older than tgt (src_epoch > tgt_epoch means wrong direction)
        violation = src_epoch - tgt_epoch
        if violation > worst_score:
            worst_score = violation
            worst = (src, tgt)
    return worst


# ---------------------------------------------------------------------------
# STEP 7: Clean annotated_formatted.csv
# ---------------------------------------------------------------------------
def step7_clean_annotated(rename_map):
    print("Step 7: Cleaning annotated_formatted.csv...")

    rows = []
    with open(ANNOT_FILE, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            rows.append(row)

    print(f"  Raw rows: {len(rows)}")

    cleaned = []
    fixes = Counter()

    seen_words = set()
    for row in rows:
        if len(row) < 4:
            fixes["short_row"] += 1
            continue

        sorted_col, word, full_text, candidates = row[0], row[1], row[2], row[3]

        # Fix trailing whitespace on word
        word_stripped = word.strip()
        if word_stripped != word:
            fixes["whitespace"] += 1
            word = word_stripped

        # Strip HTML from full_text
        full_text_clean = strip_html(full_text)
        if full_text_clean != full_text:
            fixes["html_stripped"] += 1
            full_text = full_text_clean

        # Clean sorted column: remove trailing empty ()
        sorted_clean = re.sub(r";\(\)$", "", sorted_col)
        sorted_clean = re.sub(r"^\(\);?", "", sorted_clean)
        if sorted_clean != sorted_col:
            fixes["empty_tuples"] += 1
            sorted_col = sorted_clean

        # Apply node renames to sorted column
        sorted_col = apply_renames_to_sorted(sorted_col, rename_map)

        # Dedup by word
        if word in seen_words:
            fixes["duplicate"] += 1
            continue
        seen_words.add(word)

        cleaned.append([sorted_col, word, full_text, candidates])

    # Write clean file
    with open(OUT_ANNOT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in cleaned:
            w.writerow(row)

    print(f"  Fixes: {dict(fixes)}")
    print(f"  Output rows: {len(cleaned)}")
    return cleaned


def strip_html(text):
    """Remove HTML tags from text."""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</?(blockquote|b|i|strong|em)[^>]*>", "", text)
    return text


def apply_renames_to_sorted(sorted_col, rename_map):
    """Apply node renames within the sorted edge-tuple column."""
    if not rename_map:
        return sorted_col
    for old, new in rename_map.items():
        if old in sorted_col:
            sorted_col = sorted_col.replace(old, new)
    return sorted_col


# ---------------------------------------------------------------------------
# STEP 8: Reconcile across files
# ---------------------------------------------------------------------------
def step8_reconcile(edges, etym_data, rename_map):
    print("Step 8: Reconciling across files...")

    # Rebuild etymologies.json from corrected edges
    # Group edges by word_family
    family_edges = defaultdict(list)
    for e in edges:
        family_edges[e["word_family"]].append({
            "source": e["source"],
            "target": e["target"],
        })

    # Update etymology entries
    updated = 0
    for entry in etym_data["words"]:
        word_root = entry.get("word_root", "")
        word = entry.get("word", "")

        # Find matching family
        family_key = word_root
        if family_key in family_edges:
            new_chain = family_edges[family_key]
            old_chain_set = set(
                (l["source"], l["target"]) for l in entry["etymology_chain"]
            )
            new_chain_set = set(
                (l["source"], l["target"]) for l in new_chain
            )
            if old_chain_set != new_chain_set:
                entry["etymology_chain"] = new_chain
                updated += 1

    print(f"  Etymology chains updated from edges: {updated}")
    return etym_data


# ---------------------------------------------------------------------------
# STEP 9: Validate
# ---------------------------------------------------------------------------
def step9_validate(edges, etym_data):
    print("\nStep 9: Validation...")
    issues = []

    # 9a: Duplicate edges
    edge_set = set()
    dupes = 0
    for e in edges:
        key = (e["source"], e["target"], e["word_family"])
        if key in edge_set:
            dupes += 1
        edge_set.add(key)
    check("Zero duplicate edges", dupes == 0, f"{dupes} duplicates remain", issues)

    # 9b: Self-loops
    loops = sum(1 for e in edges if e["source"] == e["target"])
    check("Zero self-loops", loops == 0, f"{loops} self-loops remain", issues)

    # 9c: Cycles
    cycles = find_cycles(edges, max_cycles=5)
    check("Zero cycles (DAG)", len(cycles) == 0, f"{len(cycles)} cycles remain", issues)

    # 9d: No href/artifact codes
    artifact_count = 0
    for e in edges:
        for field in ["source", "target"]:
            _, code = extract_lang_code(e[field])
            if code in ARTIFACT_CODES:
                artifact_count += 1
    check("Zero artifact language codes", artifact_count == 0,
          f"{artifact_count} artifact codes remain", issues)

    # 9e: Duplicate word entries
    word_counts = Counter(e["word"] for e in etym_data["words"])
    dup_words = sum(1 for c in word_counts.values() if c > 1)
    check("Zero duplicate word entries", dup_words == 0,
          f"{dup_words} duplicate words remain", issues)

    # 9f: All language codes in lookup tables
    all_codes_used = set()
    for e in edges:
        for field in ["source", "target"]:
            _, code = extract_lang_code(e[field])
            if code:
                all_codes_used.add(code)

    unknown = all_codes_used - existing_codes_global.keys() - set(NEW_CODES.keys())
    check("All language codes in lookup tables", len(unknown) == 0,
          f"{len(unknown)} unknown codes: {sorted(unknown)[:20]}", issues)

    # Stats
    all_nodes = set()
    for e in edges:
        all_nodes.add(e["source"])
        all_nodes.add(e["target"])

    print(f"\n  Final stats:")
    print(f"    Edges: {len(edges)}")
    print(f"    Unique nodes: {len(all_nodes)}")
    print(f"    Word entries: {len(etym_data['words'])}")
    print(f"    Language codes used: {len(all_codes_used)}")

    if issues:
        print(f"\n  VALIDATION ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"    FAIL: {issue}")
    else:
        print(f"\n  ALL CHECKS PASSED")

    return len(issues) == 0


def check(name, passed, msg, issues):
    if passed:
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name}: {msg}")
        issues.append(f"{name}: {msg}")


# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
def write_outputs(edges, etym_data):
    # edges_clean.csv
    with open(OUT_EDGES, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "target", "word_family"])
        w.writeheader()
        w.writerows(edges)
    print(f"\nWrote {len(edges)} edges to {OUT_EDGES}")

    # etymologies_clean.json
    with open(OUT_ETYM, "w") as f:
        json.dump(etym_data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(etym_data['words'])} words to {OUT_ETYM}")

    # cleaning_log.json
    with open(OUT_LOG, "w") as f:
        json.dump(cleaning_log, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(cleaning_log)} log entries to {OUT_LOG}")

    # flagged_for_review.csv
    with open(OUT_FLAGGED, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["reason", "word", "data"])
        w.writeheader()
        w.writerows(flagged_rows)
    print(f"Wrote {len(flagged_rows)} flagged items to {OUT_FLAGGED}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
existing_codes_global = {}

def main():
    global existing_codes_global

    print("=" * 60)
    print("EtymoLink Dataset Cleaning Pipeline")
    print("=" * 60)

    # Step 1: Expand language codes
    existing_codes_global, _ = step1_expand_lang_codes()

    # Load edges
    edges = load_edges()
    print(f"\nLoaded {len(edges)} edges from {EDGES_FILE}")

    # Step 2: Fix malformed identifiers
    rename_map = step2_fix_identifiers(edges)

    # Step 3: Resolve _href artifacts
    edges = step3_resolve_href(edges)

    # Re-apply renames and catch any remaining merge codes after step 3
    re_applied = apply_renames(edges, rename_map)
    # Also do a direct pass for any MERGE_CODES that weren't in the original rename_map
    extra_renames = 0
    for e in edges:
        for field in ["source", "target"]:
            _, code = extract_lang_code(e[field])
            if code and code in MERGE_CODES:
                word_part = e[field][:e[field].rfind("_")]
                canonical = MERGE_CODES[code]
                new_node = rebuild_node(word_part, canonical)
                if new_node != e[field]:
                    rename_map[e[field]] = new_node
                    e[field] = new_node
                    extra_renames += 1
    if re_applied or extra_renames:
        print(f"  Re-applied {re_applied} renames + {extra_renames} extra merge fixes after step 3")

    # Step 4: Deduplicate edges
    edges = step4_dedup_edges(edges)

    # Step 5: Deduplicate word entries
    etym_data = step5_dedup_words(edges, rename_map)

    # Step 6: Fix graph cycles
    edges = step6_fix_cycles(edges)

    # Step 7: Clean annotated file
    step7_clean_annotated(rename_map)

    # Step 8: Reconcile
    etym_data = step8_reconcile(edges, etym_data, rename_map)

    # Step 9: Validate
    step9_validate(edges, etym_data)

    # Write all outputs
    write_outputs(edges, etym_data)

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
