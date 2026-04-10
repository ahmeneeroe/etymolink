"""
Complete mapping of all unknown language codes found in the EtymoLink edges.csv dataset.

This module classifies every unknown code into one of four categories:
  - add_new: A real language/dialect not yet in our lookup tables.
  - merge: A variant code that should be merged into an existing canonical code.
  - remove: An artifact of HTML scraping, annotations, or parse errors.
  - fix_typo: A typo or case variant of an existing code.

Exports:
  CODE_MAPPING  - Master dict: unknown_code -> {action, ...details}
  NEW_CODES     - Dict of new codes to add: code -> {full_name, family}
  MERGE_CODES   - Dict mapping variant codes to their canonical code
  ARTIFACT_CODES - Set of codes that are artifacts to be removed/handled specially
"""

# =============================================================================
# MASTER MAPPING: Every unknown code -> action + details
# =============================================================================

CODE_MAPPING = {

    # =========================================================================
    # ARTIFACTS (action="remove")
    # HTML scraping artifacts, annotations, parse errors, non-languages
    # =========================================================================

    # --- HTML / scraping artifacts ---
    "href": {"action": "remove", "reason": "HTML scraping artifact from etymonline.com"},
    "href,": {"action": "remove", "reason": "HTML scraping artifact with trailing comma"},

    # --- Trailing-comma parse errors (code + stray comma) ---
    "L,": {"action": "fix_typo", "canonical": "L", "reason": "Trailing comma parse error"},
    "PIE,": {"action": "fix_typo", "canonical": "PIE", "reason": "Trailing comma parse error"},
    "ONor,": {"action": "fix_typo", "canonical": "ONor", "reason": "Trailing comma parse error"},
    "San,": {"action": "fix_typo", "canonical": "San", "reason": "Trailing comma parse error"},

    # --- Annotations / non-language labels ---
    "NewTest": {"action": "remove", "reason": "Annotation: 'New Testament' context, not a language"},
    "Schol": {"action": "remove", "reason": "Annotation: 'Scholastic' context, not a language"},
    "Bible": {"action": "remove", "reason": "Annotation: 'Bible' reference, not a language"},
    "Subterranean": {"action": "remove", "reason": "Not a language — word 'parterre' context"},
    "Acid": {"action": "remove", "reason": "Not a language — chemical context ('acide pectique')"},
    "Women": {"action": "remove", "reason": "Not a language — annotation"},
    "Culp": {"action": "remove", "reason": "Not a language — legal/annotation context"},
    "Soviet": {"action": "remove", "reason": "Not a language — geopolitical annotation"},
    "Austro-": {"action": "remove", "reason": "Infinite-loop parse artifact node"},
    "Gnostic": {"action": "remove", "reason": "Not a language — religious movement annotation"},
    "Bapt": {"action": "remove", "reason": "Not a language — 'Baptist' annotation (Lazarus context)"},

    # --- Infinite-loop / malformed codes ---
    "Indo-": {"action": "remove", "reason": "Truncated/malformed code — likely 'Indo-European' parse error"},
    "Indo-E": {"action": "remove", "reason": "Truncated 'Indo-European' — should be PIE or IndoIr"},

    # --- Ambiguous artifact codes ---
    "Hyp": {"action": "remove", "reason": "Artifact — 'hyphen' word used as its own code"},
    "Alaric": {"action": "remove", "reason": "Infinite-loop artifact — Alaric proper name, not a language"},
    "Scall": {"action": "remove", "reason": "Place name artifact (Scalloway), not a language"},
    "Fugger": {"action": "remove", "reason": "Proper name (Fugger family), not a language"},
    "Oscar": {"action": "remove", "reason": "Proper name, not a language"},
    "Chattahoochee": {"action": "remove", "reason": "River name used as language code — should be Muskogean"},

    # --- Empty code ---
    "": {"action": "remove", "reason": "Empty/missing language code"},

    # --- Slash-containing parse artifacts (malformed slash-separated alternatives) ---
    "G/": {"action": "remove", "reason": "Truncated slash-separated alternative (Greek)"},
    "G/kyriakon": {"action": "remove", "reason": "Malformed slash parse: 'kyriake (oikia)_G/kyriakon'"},
    "G/deikelikta": {"action": "remove", "reason": "Malformed slash parse artifact"},
    "OF/brod": {"action": "remove", "reason": "Malformed slash parse: 'breu_OF/brod'"},
    "OF/torse": {"action": "remove", "reason": "Malformed slash parse: 'trousse_OF/torse'"},
    "OF/trichier": {"action": "remove", "reason": "Malformed slash parse: 'trechier_OF/trichier'"},
    "Ger/dot": {"action": "remove", "reason": "Malformed slash parse: 'gelt_Ger/dot'"},
    "Ir/Muirgel": {"action": "remove", "reason": "Malformed slash parse: repeated Muirgheal entries"},
    "Cel/*wen-eto": {"action": "remove", "reason": "Malformed slash parse artifact"},
    "L/-oria": {"action": "remove", "reason": "Malformed slash parse: '-orius_L/-oria'"},
    "L/adserere": {"action": "remove", "reason": "Malformed slash parse: 'asserere_L/adserere'"},
    "L/*certan": {"action": "remove", "reason": "Malformed slash parse artifact"},
    "L/definire": {"action": "remove", "reason": "Malformed slash parse: 'diffinire_L/definire'"},
    "L/": {"action": "remove", "reason": "Truncated slash-separated alternative (Latin)"},
    "L/exsecrari": {"action": "remove", "reason": "Malformed slash parse: 'execrari_L/exsecrari'"},
    "L/exsultare": {"action": "remove", "reason": "Malformed slash parse: 'exultare_L/exsultare'"},
    "ONor/": {"action": "remove", "reason": "Truncated slash-separated alternative (Old Norse)"},
    "PIE/*bhe": {"action": "remove", "reason": "Malformed slash parse: PIE root artifact"},
    "PIE/*oyy": {"action": "remove", "reason": "Malformed slash parse: PIE root artifact"},
    "PIE/*yyo": {"action": "remove", "reason": "Malformed slash parse: PIE root artifact"},
    "PGer/*smul-": {"action": "remove", "reason": "Malformed slash parse: Proto-Germanic artifact"},
    "PGer/*geswi": {"action": "remove", "reason": "Malformed slash parse: Proto-Germanic artifact"},

    # --- Infinite-loop parse errors (E/... patterns) ---
    "E/crawl (v.": {"action": "remove", "reason": "Infinite-loop parse error from sprawlen entry"},
    "E/knurl": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/adj.": {"action": "remove", "reason": "Infinite-loop parse error from quit/quite entry"},
    "E/parvovirus": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/chisel": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/necromancy": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/nebbish": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/amnesty": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/imminence": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/armadillo": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/sonata": {"action": "remove", "reason": "Infinite-loop parse error"},
    "E/clavichord": {"action": "remove", "reason": "Infinite-loop parse error"},

    # =========================================================================
    # MERGES (action="merge")
    # Variant codes that map to existing canonical codes
    # =========================================================================

    # --- Arabic ---
    "Arab": {"action": "merge", "canonical": "A", "reason": "Full spelling of Arabic; canonical is 'A'"},

    # --- Polish ---
    "Po": {"action": "merge", "canonical": "Pol", "reason": "Abbreviation for Polish; canonical is 'Pol'"},

    # --- Portuguese ---
    "Port": {"action": "merge", "canonical": "Por", "reason": "Abbreviation for Portuguese; canonical is 'Por'"},

    # --- Aramaic ---
    "Arama": {"action": "merge", "canonical": "Aram", "reason": "Longer spelling of Aramaic; canonical is 'Aram'"},
    "Aramaic": {"action": "merge", "canonical": "Aram", "reason": "Full name of Aramaic; canonical is 'Aram'"},

    # --- Dakota ---
    "Dakota": {"action": "merge", "canonical": "Dako", "reason": "Full spelling of Dakota; canonical is 'Dako'"},

    # --- Hungarian ---
    "Hung": {"action": "merge", "canonical": "Hun", "reason": "Longer abbreviation for Hungarian; canonical is 'Hun'"},

    # --- Flemish ---
    "Fl": {"action": "merge", "canonical": "Flem", "reason": "Short abbreviation for Flemish; canonical is 'Flem'"},

    # --- Semitic ---
    "Semit": {"action": "merge", "canonical": "Sem", "reason": "Longer abbreviation for Semitic; canonical is 'Sem'"},

    # --- Afrikaans Dutch ---
    "ADut": {"action": "merge", "canonical": "Adut", "reason": "Case variant of Afrikaans Dutch; canonical is 'Adut'"},

    # --- Algonquian ---
    "ALG": {"action": "merge", "canonical": "Algo", "reason": "Abbreviation for Algonquian; canonical is 'Algo'"},
    "Algon": {"action": "merge", "canonical": "Algo", "reason": "Truncated 'Algonquian'; canonical is 'Algo'"},

    # --- Phoenician (merge Pho, Phoen, Ph to new canonical 'Pho') ---
    # Pho is the most frequent (25), add as new; Phoen and Ph merge to it.
    "Phoen": {"action": "merge", "canonical": "Pho", "reason": "Longer abbreviation for Phoenician; canonical is 'Pho'"},
    "Ph": {"action": "merge", "canonical": "Pho", "reason": "Short abbreviation for Phoenician; canonical is 'Pho'"},

    # --- Malay ---
    "Malaya": {"action": "merge", "canonical": "Mal", "reason": "Variant name for Malay; canonical is 'Mal'"},
    "Malayal": {"action": "merge", "canonical": "Mal", "reason": "Truncated 'Malayalam' — close to Malay; but actually Malayalam is distinct. Treat as new."},
    # NOTE: Overridden below — Malayal is actually Malayalam (Dravidian), distinct from Malay.

    # --- Nahuatl / Mexican ---
    "Mex": {"action": "merge", "canonical": "Nah", "reason": "Mexican/Nahuatl — 'chile_Mex' etc. are Nahuatl words"},

    # --- Syriac ---
    "Syri": {"action": "merge", "canonical": "Sy", "reason": "Longer form of Syriac; canonical is 'Sy'"},
    "Syrian": {"action": "merge", "canonical": "Sy", "reason": "Syrian variant — linguistic context is Syriac; canonical is 'Sy'"},

    # --- Norwegian ---
    "Norwe": {"action": "merge", "canonical": "Norw", "reason": "Truncated Norwegian; canonical is 'Norw'"},

    # --- Lithuanian ---
    "Lithu": {"action": "merge", "canonical": "Lith", "reason": "Truncated Lithuanian; canonical is 'Lith'"},

    # --- Ojibwa ---
    "OJib": {"action": "merge", "canonical": "Ojib", "reason": "Variant prefix for Ojibwa; canonical is 'Ojib'"},

    # --- Gaelic ---
    "OGae": {"action": "merge", "canonical": "Gae", "reason": "Old Gaelic — merge to Gaelic family code 'Gae' or add as new. Treating as merge since only 2 occurrences."},

    # --- Serbian ---
    "Ser": {"action": "merge", "canonical": "Serb", "reason": "Short abbreviation for Serbian; canonical is 'Serb'"},

    # --- Croatian ---
    # (no merge needed — Cro already exists)

    # --- Bulgarian ---
    "Bul": {"action": "merge", "canonical": "Bulg", "reason": "Short form for Bulgarian — merging to new code 'Bulg'"},
    "Bulgaria": {"action": "merge", "canonical": "Bulg", "reason": "Country name used as language code — merge to 'Bulg'"},

    # --- Proto-Indo-European ---
    "P": {"action": "merge", "canonical": "PIE", "reason": "All 148 uses are PIE-style reconstructed roots (*klei-wo-_P etc.)"},
    "IE": {"action": "merge", "canonical": "PIE", "reason": "'Indo-European' shorthand; likely PIE"},

    # --- Vulgar Latin ---
    "V": {"action": "merge", "canonical": "VL", "reason": "All 5 uses are reconstructed Vulgar Latin forms (*passare_V, *ultraticum_V)"},

    # --- Dutch ---
    "Dut": {"action": "add_new", "full_name": "Dutch", "family": "Germanic"},
    "D": {"action": "merge", "canonical": "Dut", "reason": "Single-letter Dutch abbreviation (blusden_D in 'bludgeon')"},
    "Du": {"action": "merge", "canonical": "Dut", "reason": "Short Dutch abbreviation (tafel_Du)"},
    "ODut": {"action": "add_new", "full_name": "Old Dutch", "family": "Germanic"},

    # --- Akkadian ---
    "Akadian": {"action": "merge", "canonical": "Akkadian", "reason": "Misspelling of Akkadian"},
    "Akkad": {"action": "merge", "canonical": "Akkadian", "reason": "Truncated Akkadian"},
    "Akka": {"action": "merge", "canonical": "Akkadian", "reason": "Truncated Akkadian"},
    # Akkadian itself is new — added below.

    # --- Breton ---
    "Bre": {"action": "merge", "canonical": "Bret", "reason": "Short form of Breton; canonical is 'Bret'"},
    # Bret itself is new — added below.

    # --- Czech ---
    "Ce": {"action": "add_new", "full_name": "Czech", "family": "Slavic"},
    "Czech": {"action": "merge", "canonical": "Ce", "reason": "Full name — merge to 'Ce' (Czech)"},
    "Bohem": {"action": "merge", "canonical": "Ce", "reason": "Bohemian = Czech; merge to 'Ce'"},

    # --- Provençal ---
    "Pro": {"action": "add_new", "full_name": "Provençal", "family": "Latin"},
    "Prov": {"action": "merge", "canonical": "Pro", "reason": "Truncated Provençal; merge to 'Pro'"},

    # --- Catalan ---
    "Cat": {"action": "add_new", "full_name": "Catalan", "family": "Latin"},
    "Cata": {"action": "merge", "canonical": "Cat", "reason": "Truncated Catalan; merge to 'Cat'"},
    "Cast": {"action": "add_new", "full_name": "Castilian", "family": "Latin"},

    # --- Romanian ---
    "Ro": {"action": "add_new", "full_name": "Romanian", "family": "Latin"},
    "Rum": {"action": "merge", "canonical": "Ro", "reason": "Rumanian spelling variant; merge to 'Ro'"},
    "Romansch": {"action": "add_new", "full_name": "Romansh", "family": "Latin"},

    # --- Marathi ---
    "Mah": {"action": "add_new", "full_name": "Marathi", "family": "Iranian"},
    "Mar": {"action": "merge", "canonical": "Mah", "reason": "Another Marathi abbreviation; merge to 'Mah'"},
    "Marathi": {"action": "merge", "canonical": "Mah", "reason": "Full name Marathi; merge to 'Mah'"},
    "Mara": {"action": "merge", "canonical": "Mah", "reason": "Truncated Marathi; merge to 'Mah'"},

    # --- Hawaiian ---
    "Hawa": {"action": "add_new", "full_name": "Hawaiian", "family": "Austronesian"},
    "Hawai": {"action": "merge", "canonical": "Hawa", "reason": "Variant Hawaiian spelling; merge to 'Hawa'"},
    "Haw": {"action": "merge", "canonical": "Hawa", "reason": "Short Hawaiian abbreviation; merge to 'Hawa'"},
    "Han": {"action": "merge", "canonical": "Hawa", "reason": "Truncated Hawaiian (poi_Han); merge to 'Hawa'"},

    # --- Slovenian ---
    "Sloven": {"action": "add_new", "full_name": "Slovenian", "family": "Slavic"},
    "Slov": {"action": "merge", "canonical": "Sloven", "reason": "Short Slovenian; merge to 'Sloven'"},

    # --- Slavic (general) ---
    "Slav": {"action": "merge", "canonical": "Sla", "reason": "Full form 'Slavic/Slavonic'; canonical is 'Sla'"},

    # --- Icelandic ---
    "Icel": {"action": "add_new", "full_name": "Icelandic", "family": "Germanic"},

    # --- Ukrainian ---
    "Ukraine": {"action": "add_new", "full_name": "Ukrainian", "family": "Slavic"},

    # --- Old Polish ---
    "OPo": {"action": "add_new", "full_name": "Old Polish", "family": "Slavic"},

    # --- Old Gascon ---
    "OGas": {"action": "add_new", "full_name": "Old Gascon", "family": "Latin"},

    # --- Swahili ---
    "Swah": {"action": "add_new", "full_name": "Swahili", "family": "African"},
    "Swa": {"action": "merge", "canonical": "Swah", "reason": "Short Swahili; merge to 'Swah'"},
    "Swap": {"action": "merge", "canonical": "Swah", "reason": "Truncated/typo for Swahili; merge to 'Swah'"},

    # --- Haitian ---
    "Hai": {"action": "add_new", "full_name": "Haitian", "family": "Native-American"},
    "Hait": {"action": "merge", "canonical": "Hai", "reason": "Truncated Haitian; merge to 'Hai'"},

    # --- Carib ---
    "Carib": {"action": "add_new", "full_name": "Carib", "family": "Native-American"},

    # --- Canadian French ---
    "Cana": {"action": "merge", "canonical": "FCan", "reason": "Canadian — linguistic context is French-Canadian; merge to 'FCan'"},

    # --- Cuban ---
    "Cub": {"action": "merge", "canonical": "CuSpan", "reason": "Cuban — linguistic context is Cuban Spanish; merge to 'CuSpan'"},
    "Cuban": {"action": "merge", "canonical": "CuSpan", "reason": "Cuban — linguistic context is Cuban Spanish; merge to 'CuSpan'"},

    # --- Old Finnish ---
    "OFi": {"action": "add_new", "full_name": "Old Finnish", "family": "Uralic"},

    # --- Frisian ---
    "Fri": {"action": "merge", "canonical": "OFri", "reason": "Frisian — likely Old Frisian context; merge to 'OFri'"},
    "WF": {"action": "add_new", "full_name": "West Frisian", "family": "Germanic"},
    "West Frisian": {"action": "merge", "canonical": "WF", "reason": "Full name; merge to 'WF'"},

    # --- South African ---
    "SA": {"action": "add_new", "full_name": "South African Dutch", "family": "Germanic"},

    # --- Anglo-Norman / Anglo ---
    "An": {"action": "add_new", "full_name": "Anglo-Norman", "family": "Latin"},
    "Anglo": {"action": "merge", "canonical": "An", "reason": "Longer form Anglo; merge to 'An'"},

    # --- Seneca ---
    "Sen": {"action": "add_new", "full_name": "Seneca", "family": "Native-American"},

    # --- Mohican/Mohegan ---
    "Moh": {"action": "add_new", "full_name": "Mohegan", "family": "Native-American"},

    # --- Aztec ---
    "Az": {"action": "merge", "canonical": "Aztec", "reason": "Short Aztec; canonical is 'Aztec'"},

    # --- Korean ---
    "Kor": {"action": "add_new", "full_name": "Korean", "family": "Koreanic"},
    "Kore": {"action": "merge", "canonical": "Kor", "reason": "Truncated Korean; merge to 'Kor'"},

    # --- Coptic ---
    "Cop": {"action": "add_new", "full_name": "Coptic", "family": "Semitic"},
    "Cops": {"action": "merge", "canonical": "Cop", "reason": "Truncated/variant Coptic; merge to 'Cop'"},

    # --- Vietnamese ---
    "Vi": {"action": "add_new", "full_name": "Vietnamese", "family": "Austroasiatic"},
    "Vie": {"action": "merge", "canonical": "Vi", "reason": "Truncated Vietnamese; merge to 'Vi'"},
    "Viet": {"action": "merge", "canonical": "Vi", "reason": "Truncated Vietnamese; merge to 'Vi'"},

    # --- Mongolian ---
    "Mongo": {"action": "add_new", "full_name": "Mongolian", "family": "Mongolic"},

    # --- New England Algonquian ---
    "NEA": {"action": "merge", "canonical": "NEAl", "reason": "Short form of Southern New England Algonquian; canonical is 'NEAl'"},

    # --- Massachuset ---
    "Massachuset": {"action": "add_new", "full_name": "Massachuset", "family": "Native-American"},

    # --- Wolof ---
    "Wol": {"action": "add_new", "full_name": "Wolof", "family": "African"},
    "Wolf": {"action": "merge", "canonical": "Wol", "reason": "Typo for Wolof; merge to 'Wol'"},
    "Wo": {"action": "merge", "canonical": "Wol", "reason": "Short Wolof abbreviation; merge to 'Wol'"},

    # --- Armenian ---
    "Armenia": {"action": "add_new", "full_name": "Armenian", "family": "Armenian"},
    "Arm": {"action": "merge", "canonical": "Armenia", "reason": "Short Armenian; merge to 'Armenia'"},

    # --- Aymara ---
    "Aymar": {"action": "add_new", "full_name": "Aymara", "family": "Native-American"},

    # --- Basque ---
    "Bas": {"action": "add_new", "full_name": "Basque", "family": "Basque"},
    "Basque": {"action": "merge", "canonical": "Bas", "reason": "Full name Basque; merge to 'Bas'"},

    # --- Tagalog ---
    "Tagalog": {"action": "add_new", "full_name": "Tagalog", "family": "Austronesian"},
    "Taga": {"action": "merge", "canonical": "Tagalog", "reason": "Truncated Tagalog; merge to 'Tagalog'"},

    # --- Urdu ---
    "Ur": {"action": "add_new", "full_name": "Urdu", "family": "Iranian"},
    "Urdu": {"action": "merge", "canonical": "Ur", "reason": "Full name Urdu; merge to 'Ur'"},

    # --- Amharic ---
    "Amharic": {"action": "add_new", "full_name": "Amharic", "family": "Semitic"},

    # --- Assyrian ---
    "Assyrian": {"action": "add_new", "full_name": "Assyrian", "family": "Semitic"},
    "Assain": {"action": "merge", "canonical": "Assyrian", "reason": "Misspelling of Assyrian"},

    # --- Hebrew ---
    "Heb": {"action": "merge", "canonical": "H", "reason": "Abbreviation for Hebrew; canonical is 'H'"},
    "ModH": {"action": "add_new", "full_name": "Modern Hebrew", "family": "Semitic"},
    "Ash": {"action": "add_new", "full_name": "Ashkenazi Hebrew", "family": "Semitic"},

    # --- Sinhalese ---
    "Sinh": {"action": "add_new", "full_name": "Sinhalese", "family": "Iranian"},
    "Sin": {"action": "merge", "canonical": "Sinh", "reason": "Short Sinhalese; merge to 'Sinh'"},

    # --- Punjabi / Pali ---
    "Pa": {"action": "add_new", "full_name": "Pali", "family": "Iranian"},
    "Pah": {"action": "add_new", "full_name": "Pahlavi", "family": "Iranian"},

    # --- Indic ---
    "Indic": {"action": "add_new", "full_name": "Indic", "family": "Iranian"},
    "In": {"action": "merge", "canonical": "Indic", "reason": "Short Indic; merge to 'Indic'"},
    "Indo": {"action": "merge", "canonical": "IndoIr", "reason": "Truncated Indo(-Iranian); merge to 'IndoIr'"},
    "IndoE": {"action": "merge", "canonical": "PIE", "reason": "Indo-European = PIE; merge to 'PIE'"},

    # --- Prakrit ---
    "Pr": {"action": "add_new", "full_name": "Prakrit", "family": "Iranian"},

    # --- Old Greek dialects ---
    "Attic": {"action": "add_new", "full_name": "Attic Greek", "family": "Greek"},
    "At": {"action": "merge", "canonical": "Attic", "reason": "Short Attic Greek; merge to 'Attic'"},
    "DoG": {"action": "add_new", "full_name": "Doric Greek", "family": "Greek"},
    "DoRo": {"action": "merge", "canonical": "DoG", "reason": "Doric/Roman Greek variant; merge to 'DoG' (Doric Greek)"},
    "Doric": {"action": "merge", "canonical": "DoG", "reason": "Full name Doric; merge to 'DoG'"},
    "Ionic": {"action": "add_new", "full_name": "Ionic Greek", "family": "Greek"},
    "Aeolian": {"action": "add_new", "full_name": "Aeolian Greek", "family": "Greek"},
    "Gate": {"action": "add_new", "full_name": "Greek (Attic)", "family": "Greek"},
    # Gate: kleitoris_Gate -> kleiein_G — looks like an Attic Greek variant annotation.
    # Could merge to Attic, but keeping separate for traceability.
    "OG": {"action": "add_new", "full_name": "Old Greek", "family": "Greek"},

    # --- Proto-languages ---
    "PoSla": {"action": "add_new", "full_name": "Proto-Slavic", "family": "Slavic"},
    "ProSla": {"action": "merge", "canonical": "PoSla", "reason": "Variant Proto-Slavic code; merge to 'PoSla'"},
    "OSla": {"action": "merge", "canonical": "PoSla", "reason": "Old Slavic — essentially Proto-Slavic; merge to 'PoSla'"},
    "PWGer": {"action": "add_new", "full_name": "Proto-West-Germanic", "family": "Germanic"},
    "PCE": {"action": "add_new", "full_name": "Proto-Celtic", "family": "Celtic"},

    # --- Pelasgian ---
    "Pela": {"action": "add_new", "full_name": "Pelasgian", "family": "Pre-Greek"},

    # --- Punic ---
    "Pu": {"action": "add_new", "full_name": "Punic", "family": "Semitic"},

    # --- Phrygian ---
    "Phry": {"action": "add_new", "full_name": "Phrygian", "family": "Anatolian"},

    # --- Pythagorean / Pythian ---
    "Pyt": {"action": "remove", "reason": "Annotation — 'Pythagorean' or 'Pythian' context, not a language"},
    "Pytho": {"action": "remove", "reason": "Annotation — 'Pythian' context, not a language; also shows infinite-loop pattern"},

    # --- Judeo / Jewish ---
    "Ju": {"action": "add_new", "full_name": "Judeo-Arabic", "family": "Semitic"},
    # Hymie_Ju context suggests Jewish/Yiddish, but Yiddish already exists as 'Yid'.
    # 'Ju' likely means Judeo-Arabic or general Jewish linguistic context.

    # --- Roman ---
    "Roman": {"action": "add_new", "full_name": "Romansh", "family": "Latin"},
    "Romany": {"action": "add_new", "full_name": "Romani", "family": "Iranian"},
    "R": {"action": "add_new", "full_name": "Roman (Latin)", "family": "Latin"},
    # R: iuventas_R — Roman Latin, essentially synonymous with L, but may represent
    # a Roman dialect/register distinction. Keeping separate.

    # --- Ugaritic ---
    "Ugar": {"action": "add_new", "full_name": "Ugaritic", "family": "Semitic"},

    # --- Sicilian ---
    "Sici": {"action": "add_new", "full_name": "Sicilian", "family": "Latin"},

    # --- Neapolitan ---
    "Nea": {"action": "add_new", "full_name": "Neapolitan", "family": "Latin"},

    # --- Florentine ---
    "Flor": {"action": "add_new", "full_name": "Florentine", "family": "Latin"},

    # --- Venetian ---
    "Ven": {"action": "add_new", "full_name": "Venetian", "family": "Latin"},

    # --- Corsican ---
    "Corsican": {"action": "add_new", "full_name": "Corsican", "family": "Latin"},

    # --- Savoyard ---
    "Savoy": {"action": "add_new", "full_name": "Savoyard", "family": "Latin"},

    # --- Occitan ---
    "Occitan": {"action": "add_new", "full_name": "Occitan", "family": "Latin"},

    # --- Argentine Spanish ---
    "Argentine": {"action": "add_new", "full_name": "Argentine Spanish", "family": "Latin"},

    # --- Gallo-Latin ---
    "GaL": {"action": "add_new", "full_name": "Gallo-Latin", "family": "Latin"},

    # --- Gallo-Turkic? No — GaT = Gujarati (banyan context) ---
    "GaT": {"action": "add_new", "full_name": "Gujarati (Trade)", "family": "Iranian"},
    # GaT: vaniyo_GaT in 'banyan' — Gujarati trade language context.

    # --- Gujarati ---
    "Gujarati": {"action": "add_new", "full_name": "Gujarati", "family": "Iranian"},
    "Guar": {"action": "merge", "canonical": "Gujarati", "reason": "Truncated Gujarati variant; but actually 'para_Guar' = Guarani"},
    # Correction: Guar = Guarani (para_Guar in 'Guarani' context). Override:

    # --- Frankish ---
    "Frank": {"action": "merge", "canonical": "Fran", "reason": "Full name 'Frankish'; canonical is 'Fran'"},

    # --- Bavarian ---
    "Bav": {"action": "add_new", "full_name": "Bavarian", "family": "Germanic"},

    # --- Alemannic / Swiss German ---
    "Al": {"action": "add_new", "full_name": "Alemannic", "family": "Germanic"},
    "Swis": {"action": "add_new", "full_name": "Swiss German", "family": "Germanic"},
    "Switzerland": {"action": "merge", "canonical": "Swis", "reason": "Country name used as code; merge to 'Swis'"},
    "Switz": {"action": "merge", "canonical": "Swis", "reason": "Truncated Switzerland; merge to 'Swis'"},

    # --- Faeroese ---
    "Faer": {"action": "add_new", "full_name": "Faroese", "family": "Germanic"},

    # --- Gothic ---
    "Goth": {"action": "add_new", "full_name": "Gothic", "family": "Germanic"},
    "Go": {"action": "merge", "canonical": "Goth", "reason": "Short Gothic abbreviation; merge to 'Goth'"},

    # --- Old High German (OH) ---
    "OH": {"action": "merge", "canonical": "OHGer", "reason": "Short Old High German; canonical is 'OHGer'"},

    # --- Old Saxon ---
    "OSach": {"action": "add_new", "full_name": "Old Saxon", "family": "Germanic"},
    "Ae": {"action": "add_new", "full_name": "Anglo-Saxon (dialectal)", "family": "Germanic"},
    # Ae: ponen_Ae — likely Anglian/Anglo-Saxon dialectal form.

    # --- Old Scandinavian ---
    "OScan": {"action": "add_new", "full_name": "Old Scandinavian", "family": "Germanic"},
    "ONS": {"action": "add_new", "full_name": "Old North Scandinavian", "family": "Germanic"},

    # --- Old Estonian ---
    "OEst": {"action": "add_new", "full_name": "Old Estonian", "family": "Baltic"},

    # --- Mercian ---
    "Mer": {"action": "add_new", "full_name": "Mercian", "family": "Germanic"},
    "Me": {"action": "merge", "canonical": "Mer", "reason": "Short Mercian; merge to 'Mer'"},
    "Mec": {"action": "merge", "canonical": "Mer", "reason": "Mercian variant code; merge to 'Mer'"},
    "Mid": {"action": "merge", "canonical": "Mer", "reason": "Midlands dialect = Mercian; merge to 'Mer'"},

    # --- Northumbrian ---
    "Northumber": {"action": "add_new", "full_name": "Northumbrian", "family": "Germanic"},

    # --- Kentish ---
    "Kent": {"action": "add_new", "full_name": "Kentish", "family": "Germanic"},

    # --- Old English dialects / broader ---
    "Austra": {"action": "add_new", "full_name": "Austrasian", "family": "Germanic"},
    # Austra: -scip_Austra — in '-ship' word family, from OE -sciepe.
    # Austrasian = Frankish/Merovingian dialect context. Or possibly a truncation.

    # --- Jamaican ---
    "Jam": {"action": "add_new", "full_name": "Jamaican Creole", "family": "Creole"},

    # --- West Indian Pidgin ---
    "WiP": {"action": "add_new", "full_name": "West Indian Pidgin", "family": "Creole"},

    # --- Afro-Cuban ---
    "AfroCuban": {"action": "add_new", "full_name": "Afro-Cuban", "family": "African"},

    # --- Old Church Slavonic ---
    "OCh": {"action": "add_new", "full_name": "Old Church Slavonic", "family": "Slavic"},

    # --- Delaware / Unami ---
    "Unami": {"action": "add_new", "full_name": "Unami (Delaware)", "family": "Native-American"},

    # --- Chinook ---
    "Chinook": {"action": "add_new", "full_name": "Chinook", "family": "Native-American"},

    # --- Cree ---
    "Cree": {"action": "add_new", "full_name": "Cree", "family": "Native-American"},

    # --- Mohawk ---
    "Mohawk": {"action": "add_new", "full_name": "Mohawk", "family": "Native-American"},

    # --- Choctaw ---
    "Choc": {"action": "add_new", "full_name": "Choctaw", "family": "Native-American"},
    "Cho": {"action": "merge", "canonical": "Choc", "reason": "Short Choctaw; merge to 'Choc'"},

    # --- Muskogean ---
    "Musko": {"action": "add_new", "full_name": "Muskogean", "family": "Native-American"},
    "Musco": {"action": "merge", "canonical": "Musko", "reason": "Variant Muskogean spelling; merge to 'Musko'"},

    # --- Caddoan ---
    "Cad": {"action": "add_new", "full_name": "Caddoan", "family": "Native-American"},

    # --- Taino ---
    "Taino": {"action": "add_new", "full_name": "Taino", "family": "Native-American"},

    # --- Maya ---
    "Maya": {"action": "add_new", "full_name": "Mayan", "family": "Native-American"},

    # --- Cherokee (Chue = Cherokee) ---
    "Chue": {"action": "add_new", "full_name": "Cherokee", "family": "Native-American"},

    # --- Kansa ---
    "Kansa": {"action": "add_new", "full_name": "Kansa", "family": "Native-American"},

    # --- Kiowa ---
    "Kiowa": {"action": "add_new", "full_name": "Kiowa", "family": "Native-American"},

    # --- Navajo ---
    "Navajo": {"action": "add_new", "full_name": "Navajo", "family": "Native-American"},

    # --- Athapaskan ---
    "Ahapaskan": {"action": "add_new", "full_name": "Athapaskan", "family": "Native-American"},

    # --- Pima / O'odham ---
    "Piman": {"action": "add_new", "full_name": "Piman (O'odham)", "family": "Native-American"},
    "O'odham (Piman)": {"action": "merge", "canonical": "Piman", "reason": "Full name; merge to 'Piman'"},

    # --- Pueblo ---
    "Pue": {"action": "add_new", "full_name": "Pueblo", "family": "Native-American"},

    # --- Tewa ---
    "Tewa": {"action": "add_new", "full_name": "Tewa", "family": "Native-American"},

    # --- Virginia Algonquian ---
    "Virgini": {"action": "add_new", "full_name": "Virginia Algonquian", "family": "Native-American"},

    # --- Salinan / Salish ---
    "Sal": {"action": "add_new", "full_name": "Salish", "family": "Native-American"},

    # --- Sasquatch / Halkomelem ---
    "Sas": {"action": "add_new", "full_name": "Halkomelem", "family": "Native-American"},
    # Sas: /inuk/_Sas — could be Salishan. The context (Inuk = Sasquatch) suggests Halkomelem.

    # --- Inupiaq ---
    "Inupiaq": {"action": "add_new", "full_name": "Inupiaq", "family": "Eskimo-Aleut"},
    "Inuk": {"action": "merge", "canonical": "Inupiaq", "reason": "Inuk variant; merge to 'Inupiaq'"},

    # --- Alutiq ---
    "Alutiq": {"action": "add_new", "full_name": "Alutiq", "family": "Eskimo-Aleut"},

    # --- Aleut / Alaska ---
    "Ala": {"action": "add_new", "full_name": "Aleut", "family": "Eskimo-Aleut"},

    # --- Micmac ---
    "Mic": {"action": "add_new", "full_name": "Mi'kmaq", "family": "Native-American"},

    # --- Nootka ---
    "Noot": {"action": "add_new", "full_name": "Nootka", "family": "Native-American"},

    # --- Chibchan ---
    "Chib": {"action": "add_new", "full_name": "Chibchan", "family": "Native-American"},

    # --- Guarani ---
    "Guar": {"action": "add_new", "full_name": "Guarani", "family": "Native-American"},
    # Override the earlier entry. Guar: para_Guar = Guarani context.

    # --- Chamorro ---
    "Chaman": {"action": "add_new", "full_name": "Chamorro", "family": "Austronesian"},

    # --- Washoe ---
    "Wash": {"action": "add_new", "full_name": "Washoe", "family": "Native-American"},

    # --- Dawson / Tamashek ---
    "Daw": {"action": "add_new", "full_name": "Dawson (Tamashek)", "family": "African"},
    # Daw: Tamanen_Daw — Tamashek/Tuareg context.

    # --- Australian Aboriginal ---
    "Au": {"action": "add_new", "full_name": "Australian Aboriginal", "family": "Australian"},
    "Australia": {"action": "merge", "canonical": "Au", "reason": "Country name used as code; merge to 'Au'"},
    "Aborigine": {"action": "merge", "canonical": "Au", "reason": "Aborigine label; merge to 'Au'"},
    "Dharruk": {"action": "add_new", "full_name": "Dharruk", "family": "Australian"},

    # --- Pintupi ---
    "Pin": {"action": "add_new", "full_name": "Pintupi", "family": "Australian"},

    # --- Maori (already exists) ---
    # No action needed.

    # --- Tongan ---
    "Tongan": {"action": "add_new", "full_name": "Tongan", "family": "Austronesian"},

    # --- Tahitian ---
    "Tah": {"action": "add_new", "full_name": "Tahitian", "family": "Austronesian"},

    # --- Ambon/Moluccan ---
    "Amboyna": {"action": "add_new", "full_name": "Ambonese", "family": "Austronesian"},

    # --- Cambodian ---
    "Cambo": {"action": "add_new", "full_name": "Cambodian (Khmer)", "family": "Austroasiatic"},

    # --- Micronesian ---
    "Micro": {"action": "add_new", "full_name": "Micronesian", "family": "Austronesian"},

    # --- Thai ---
    "Thai": {"action": "add_new", "full_name": "Thai", "family": "Tai-Kadai"},

    # --- Tibetan ---
    "Tib": {"action": "add_new", "full_name": "Tibetan", "family": "Sino-Tibetan"},

    # --- Mundari / Munda ---
    "Mun": {"action": "add_new", "full_name": "Mundari", "family": "Austroasiatic"},
    # Mun: dalai_Mun (Dalai Lama) — Mongolian context? No — Shawnee is also Mun.
    # Actually "dalai" is Mongolian. But Shawnee_Mun = Munsee Delaware.
    # Keeping as Mundari since that matches the abbrev best, but it's heterogeneous.

    # --- Khoisan ---
    "Kho": {"action": "add_new", "full_name": "Khoisan", "family": "African"},
    "Saf": {"action": "add_new", "full_name": "South African Khoisan", "family": "African"},

    # --- Zulu ---
    "Zul": {"action": "add_new", "full_name": "Zulu", "family": "African"},

    # --- Twi ---
    "Tw": {"action": "add_new", "full_name": "Twi", "family": "African"},

    # --- Kongo ---
    "Kong": {"action": "add_new", "full_name": "Kongo", "family": "African"},

    # --- Gullah ---
    "Gul": {"action": "add_new", "full_name": "Gullah", "family": "Creole"},

    # --- Lokele ---
    "Lokele": {"action": "add_new", "full_name": "Lokele", "family": "African"},

    # --- Tuareg ---
    "Tuare": {"action": "add_new", "full_name": "Tuareg", "family": "African"},

    # --- Bantu ---
    "Ban": {"action": "add_new", "full_name": "Bantu", "family": "African"},

    # --- Nub(ian) ---
    "Nub": {"action": "add_new", "full_name": "Nubian", "family": "African"},

    # --- Hausa ---
    "Hau": {"action": "add_new", "full_name": "Hausa", "family": "African"},

    # --- Burmese ---
    "Bur": {"action": "add_new", "full_name": "Burmese", "family": "Sino-Tibetan"},

    # --- Tungusic ---
    "Tungus": {"action": "add_new", "full_name": "Tungusic", "family": "Tungusic"},

    # --- Vogul ---
    "Vogul": {"action": "add_new", "full_name": "Vogul (Mansi)", "family": "Uralic"},

    # --- Kazakh ---
    "Kaz": {"action": "add_new", "full_name": "Kazakh", "family": "Turkic"},

    # --- Tajik ---
    "Taj": {"action": "add_new", "full_name": "Tajik", "family": "Iranian"},

    # --- Telugu ---
    "TeL": {"action": "add_new", "full_name": "Telugu", "family": "Dravidian"},

    # --- Tamil ---
    "Tam": {"action": "add_new", "full_name": "Tamil", "family": "Dravidian"},

    # --- Malayalam (distinct from Malay!) ---
    "Malayal": {"action": "add_new", "full_name": "Malayalam", "family": "Dravidian"},
    "Malayalam": {"action": "merge", "canonical": "Malayal", "reason": "Full name Malayalam; merge to 'Malayal'"},

    # --- Balti / Tibetan ---
    "Bal": {"action": "add_new", "full_name": "Balti", "family": "Sino-Tibetan"},

    # --- Shoshone ---
    "Sho": {"action": "add_new", "full_name": "Shoshone", "family": "Native-American"},

    # --- Wampanoag / Wampum ---
    "Woo": {"action": "add_new", "full_name": "Woodland Cree", "family": "Native-American"},
    # Woo: Athapaskaw_Woo — Woodland Cree or general Woodland context.

    # --- Iberian ---
    "Ib": {"action": "add_new", "full_name": "Iberian", "family": "Pre-Roman"},

    # --- Adriatic ---
    "Adriatic": {"action": "add_new", "full_name": "Adriatic (dialectal)", "family": "Latin"},

    # --- Brythonic / British ---
    "Britan": {"action": "add_new", "full_name": "Brythonic", "family": "Celtic"},
    "British": {"action": "merge", "canonical": "Britan", "reason": "British = Brythonic context; merge to 'Britan'"},

    # --- Cockney ---
    "Cockney": {"action": "add_new", "full_name": "Cockney", "family": "Germanic"},

    # --- UK English ---
    "UK": {"action": "merge", "canonical": "E", "reason": "UK English; merge to 'E' (English)"},

    # --- Delaware English / DE ---
    "DE": {"action": "add_new", "full_name": "Delaware English (dialectal)", "family": "Germanic"},
    # DE: ponk_DE in 'punk' — could be Delaware dialect. Or Deutsch.
    # Given ponk_DE -> punk context, likely dialectal English. Keeping as-is.

    # --- Ameliorated French ---
    "Amél": {"action": "merge", "canonical": "F", "reason": "Dialectal French variant; merge to 'F'"},

    # --- Dufnal / Dufenald ---
    "Duf": {"action": "add_new", "full_name": "Duffus (Gaelic dialectal)", "family": "Celtic"},
    # Duf: Dufenald_Duf — Gaelic name variant from Donald etymology.

    # --- Hattian ---
    "Hat": {"action": "add_new", "full_name": "Hattian", "family": "Anatolian"},

    # --- Ariz(ona) / Apache ---
    "Ariz": {"action": "add_new", "full_name": "Arizona Apache", "family": "Native-American"},
    "Apaca": {"action": "add_new", "full_name": "Apache", "family": "Native-American"},

    # --- Sumerian ---
    "Sume": {"action": "add_new", "full_name": "Sumerian", "family": "Sumerian"},

    # --- Umbrian ---
    "Umbi": {"action": "add_new", "full_name": "Umbrian", "family": "Latin"},

    # --- Late Babylonian ---
    "LateBaby": {"action": "add_new", "full_name": "Late Babylonian", "family": "Semitic"},

    # --- Pe = Celtic/Pelasgian (ambiguous) ---
    "Pe": {"action": "merge", "canonical": "Pela", "reason": "Short Pelasgian (*kau-_Pe for Caucasus); merge to 'Pela'"},

    # --- Ara = Araucanian ---
    "Ara": {"action": "add_new", "full_name": "Araucanian", "family": "Native-American"},

    # --- Cer = unclear (Mounted_Cer) ---
    "Cer": {"action": "remove", "reason": "Annotation artifact — 'Mounted (police)' context, not a language"},

    # --- Nie = Niederdeutsch (Low German) ---
    "Nie": {"action": "merge", "canonical": "LGer", "reason": "Niederdeutsch = Low German; canonical is 'LGer'"},

    # --- Afri = Anglian Frisian? ---
    "Afri": {"action": "merge", "canonical": "OFri", "reason": "Likely Anglian-Frisian; merge to 'OFri'"},
    # Afri: wall_Afri -> vallum_L in 'wall' family. Between OE weall and L vallum.
    # Context suggests Anglian-Frisian or general continental form.

    # --- Afra = Anglian-Frisian variant ---
    "Afra": {"action": "merge", "canonical": "OFri", "reason": "Anglian-Frisian variant (height context); merge to 'OFri'"},

    # --- Late(vian) ---
    "Late": {"action": "add_new", "full_name": "Latvian", "family": "Baltic"},

    # --- Iri = Irish ---
    "Iri": {"action": "merge", "canonical": "Ir", "reason": "Truncated Irish; merge to 'Ir'"},

    # --- ModIr = Modern Irish ---
    "ModIr": {"action": "add_new", "full_name": "Modern Irish", "family": "Celtic"},

    # --- West ---
    "West": {"action": "remove", "reason": "Annotation — directional qualifier, not a language"},

    # --- Man = Manchu / Mandarin ---
    "Man": {"action": "add_new", "full_name": "Mandarin", "family": "Sino-Tibetan"},

    # --- Africa ---
    "Africa": {"action": "merge", "canonical": "Afr", "reason": "Full name 'African'; canonical is 'Afr'"},
    "Afriat": {"action": "merge", "canonical": "Afr", "reason": "Truncated African variant; merge to 'Afr'"},

    # --- AC = Algonquian-Canadian ---
    "AC": {"action": "merge", "canonical": "Algo", "reason": "Algonquian-Canadian (*mockasin_AC); merge to 'Algo'"},

    # --- WoS = West Saxon ---
    "WoS": {"action": "add_new", "full_name": "West Saxon", "family": "Germanic"},

    # --- Osse = Ossetian ---
    "Osse": {"action": "add_new", "full_name": "Ossetian", "family": "Iranian"},

    # --- Oscan ---
    "Os": {"action": "add_new", "full_name": "Oscan", "family": "Latin"},
    "Oscon": {"action": "merge", "canonical": "Os", "reason": "Variant Oscan spelling; merge to 'Os'"},

    # --- MediLateL ---
    "MediLateL": {"action": "merge", "canonical": "MediL", "reason": "Medieval/Late Latin — merge to 'MediL'"},

    # --- Ael = Aeolian or Aleut ---
    "Ael": {"action": "add_new", "full_name": "Aleut (Aeolian)", "family": "Eskimo-Aleut"},
    # Ael: parka_Ael — parka is from Aleut/Nenets. So Ael = Aleut.

    # =========================================================================
    # NEW LANGUAGE CODES (action="add_new")
    # These are covered in the entries above with full_name and family.
    # The ones listed here with action="add_new" directly:
    # =========================================================================

    "HGer": {"action": "add_new", "full_name": "High German", "family": "Germanic"},
    "OIr": {"action": "add_new", "full_name": "Old Irish", "family": "Celtic"},
    "OI": {"action": "add_new", "full_name": "Old Italian", "family": "Latin"},
    "Span": {"action": "add_new", "full_name": "Spanish", "family": "Latin"},
    "MexSpan": {"action": "add_new", "full_name": "Mexican Spanish", "family": "Latin"},
    "Gau": {"action": "add_new", "full_name": "Gaulish", "family": "Celtic"},
    "ChuSla": {"action": "add_new", "full_name": "Church Slavonic", "family": "Slavic"},
    "OPer": {"action": "add_new", "full_name": "Old Persian", "family": "Iranian"},
    "OCel": {"action": "add_new", "full_name": "Old Celtic", "family": "Celtic"},
    "ODan": {"action": "add_new", "full_name": "Old Danish", "family": "Germanic"},
    "Pho": {"action": "add_new", "full_name": "Phoenician", "family": "Semitic"},
    "Akkadian": {"action": "add_new", "full_name": "Akkadian", "family": "Semitic"},
    "OSpan": {"action": "add_new", "full_name": "Old Spanish", "family": "Latin"},
    "LateG": {"action": "add_new", "full_name": "Late Greek", "family": "Greek"},
    "MediG": {"action": "add_new", "full_name": "Medieval Greek", "family": "Greek"},
    "Bret": {"action": "add_new", "full_name": "Breton", "family": "Celtic"},
    "OBret": {"action": "add_new", "full_name": "Old Breton", "family": "Celtic"},
    "Corn": {"action": "add_new", "full_name": "Cornish", "family": "Celtic"},
    "OSer": {"action": "add_new", "full_name": "Old Serbian", "family": "Slavic"},
    "OSwe": {"action": "add_new", "full_name": "Old Swedish", "family": "Germanic"},
    "Bulg": {"action": "add_new", "full_name": "Bulgarian", "family": "Slavic"},
    "Baby": {"action": "add_new", "full_name": "Babylonian", "family": "Semitic"},
    "B": {"action": "add_new", "full_name": "Biblical (annotation)", "family": "Semitic"},
    # B: sucuriuba_B is Tupi-Guarani for anaconda; Jeroboam_B is Biblical.
    # Heterogeneous — treating as Biblical since that's the majority.

    # --- Ar = Greek (article-related forms) ---
    "Ar": {"action": "add_new", "full_name": "Greek (archaic)", "family": "Greek"},
    # Ar: antipodes_Ar, apodal_Ar, babouche_Ar etc. in *ped- family.
    # These are Greek-derived forms. Ar may be an abbreviation for "archaic Greek"
    # or a data entry artifact. All appear in the *ped- word family.

    # --- Ra = Rhaeto-Romance ---
    "Ra": {"action": "add_new", "full_name": "Rhaeto-Romance", "family": "Latin"},
    # Ra: Ladin_Ra — Ladin is a Rhaeto-Romance language.

    # --- Tu = Tuscan ---
    "Tu": {"action": "add_new", "full_name": "Tuscan", "family": "Latin"},
    # Tu: ditto_Tu — Tuscan Italian dialect.

    # --- Hami = Hamitic ---
    "Hami": {"action": "add_new", "full_name": "Hamitic", "family": "African"},
    # Hami: Hamitic_Hami — the Hamitic language family.

    # --- Gab = Gabonese ---
    "Gab": {"action": "add_new", "full_name": "Gabonese", "family": "African"},
    # Gab: piragua_Gab — Gabonese/Central African language context.
}


# =============================================================================
# Fix the Malayal override (it was set to merge, then described as add_new)
# The last assignment wins in dict literals, so let's ensure consistency.
# Malayal should be add_new (Malayalam is distinct from Malay).
# =============================================================================
CODE_MAPPING["Malayal"] = {"action": "add_new", "full_name": "Malayalam", "family": "Dravidian"}

# Guar should be Guarani, not Gujarati
CODE_MAPPING["Guar"] = {"action": "add_new", "full_name": "Guarani", "family": "Native-American"}


# =============================================================================
# DERIVED EXPORTS
# =============================================================================

# NEW_CODES: codes that need to be added to language_codes.csv and language_families.csv
NEW_CODES = {}
for code, info in CODE_MAPPING.items():
    if info.get("action") == "add_new":
        NEW_CODES[code] = {
            "full_name": info["full_name"],
            "family": info["family"],
        }

# MERGE_CODES: variant code -> canonical code
MERGE_CODES = {}
for code, info in CODE_MAPPING.items():
    if info.get("action") == "merge":
        MERGE_CODES[code] = info["canonical"]

# ARTIFACT_CODES: codes that are not languages and should be removed/flagged
ARTIFACT_CODES = set()
for code, info in CODE_MAPPING.items():
    if info.get("action") == "remove":
        ARTIFACT_CODES.add(code)

# FIX_TYPO_CODES: codes with trailing punctuation to fix
FIX_TYPO_CODES = {}
for code, info in CODE_MAPPING.items():
    if info.get("action") == "fix_typo":
        FIX_TYPO_CODES[code] = info["canonical"]


# =============================================================================
# VALIDATION / SUMMARY
# =============================================================================

if __name__ == "__main__":
    print(f"Total unknown codes mapped: {len(CODE_MAPPING)}")
    print(f"  New codes to add:        {len(NEW_CODES)}")
    print(f"  Merge to canonical:      {len(MERGE_CODES)}")
    print(f"  Artifacts to remove:     {len(ARTIFACT_CODES)}")
    print(f"  Typos to fix:            {len(FIX_TYPO_CODES)}")
    print()

    total = len(NEW_CODES) + len(MERGE_CODES) + len(ARTIFACT_CODES) + len(FIX_TYPO_CODES)
    print(f"  Sum of categories:       {total}")
    print(f"  Match total?             {total == len(CODE_MAPPING)}")
    print()

    # Print new codes by family
    from collections import defaultdict
    by_family = defaultdict(list)
    for code, info in sorted(NEW_CODES.items()):
        by_family[info["family"]].append(f"{code} ({info['full_name']})")

    print("NEW CODES BY FAMILY:")
    for family in sorted(by_family):
        print(f"  {family}:")
        for entry in by_family[family]:
            print(f"    {entry}")
    print()

    print("MERGE CODES:")
    for variant, canonical in sorted(MERGE_CODES.items()):
        print(f"  {variant:20s} -> {canonical}")
    print()

    print("ARTIFACT CODES:")
    for code in sorted(ARTIFACT_CODES):
        print(f"  {code}")
    print()

    print("TYPO FIXES:")
    for code, canonical in sorted(FIX_TYPO_CODES.items()):
        print(f"  {code!r:10s} -> {canonical}")
