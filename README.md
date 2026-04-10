# EtymoLink: A Structured English Etymology Dataset

> **This fork contains a cleaned version of the dataset.** The original data had ~19% duplicate rows, HTML scraping artifacts, graph cycles, and 360 undefined language codes. See [CLEANING.md](CLEANING.md) for a detailed explanation of all corrections. Cleaned files are in the `cleaned/` directory.

This is the dataset for the paper "EtymoLink: A Structured English Etymology Dataset" ([ACL Anthology](https://aclanthology.org/2024.lchange-1.12/)).
## Files

### `etymologies.json`
Contains the complete structured dataset with word entries and their etymology chains.

**Structure:**
```json
{
  "words": [
    {
      "word": "approbate_E",
      "word_root": "approbate",
      "etymology_chain": [
        {"source": "approbate_E", "target": "approbatus_L"},
        {"source": "approbatus_L", "target": "approbare_L"}
      ]
    }
  ]
}
```

**Fields:**
- `word`: The word with language code (e.g., "approbate_E")
- `word_root`: The base word without language code
- `etymology_chain`: List of etymological relationships showing the word's evolution

### `edges.csv`
A simplified edge list format for easy processing and analysis.

**Columns:**
- `source`: The derived word or form
- `target`: The source word or form it derives from
- `word_family`: The root word family this relationship belongs to

**Example:**
```csv
source,target,word_family
approbate_E,approbatus_L,approbate
approbatus_L,approbare_L,approbate
```

### `annotated.csv`
Contains human-annotated entries with additional quality control and verification.

## Data Format Notes

### Multiple Forms
Some entries contain multiple forms separated by forward slashes (e.g., `affectation_F/affectationem_L`), indicating alternative or equivalent forms of the same etymological concept. This occurs when etymological sources mention different related forms. These slash-separated forms should be treated as representing the same node in the etymological graph.

### Etymology Chains
Each word's etymology is represented as a chain of relationships, where each link shows the direct derivation from one form to another. The chain flows from the modern word back to its earliest known origins.


## Language Codes

The dataset uses the following language abbreviations:

| Code | Language | Code | Language |
|------|----------|------|----------|
| PIE | Proto-Indo-European | F | French |
| ONF | Old North French | AF | Anglo-French |
| MF | Middle French | OF | Old French |
| ASpan | American Spanish | L | Latin |
| MediL | Medieval Latin | ModL | Modern Latin |
| LateL | Late Latin | VL | Vulgar Latin |
| OE | Old English | PGer | Proto-Germanic |
| H | Hebrew | Avest | Avestan |
| IndoIr | Indo-Iranian | San | Sanskrit |
| G | Greek | GE | Greenland Eskimo |
| I | Italian | A | Arabic |
| Sy | Syriac | Per | Persian |
| Ira | Iranian | Por | Portuguese |
| OHGer | Old High German | Adut | Afrikaans Dutch |
| Ger | German | AL | Anglo-Latin |
| Cel | Celtic | Tur | Turkish |
| ModG | Modern Greek | ChuL | Church Latin |
| EG | Ecclesiastical Greek | OL | Old Latin |
| PI | Proto-Italic | Nor | Norse |
| ONor | Old Norse | Dan | Danish |
| FCan | French-Canadian | Fran | Frankish |
| Gae | Gaelic | Scot | Scottish |
| Hin | Hindi | Yid | Yiddish |
| Rus | Russian | ORus | Old Russian |
| OPro | Old Provençal | LGer | Low German |
| WGer | West Germanic | Ir | Irish |
| Nah | Nahuatl (Aztecan) | Mal | Malay |
| Ch | Chinese | Scan | Scandinavian |
| Wel | Welsh | Sem | Semitic |
| Norw | Norwegian | Swe | Swedish |
| Sla | Slavonic | Jap | Japanese |
| Ber | Berrichon | Afr | African |
| SerCro | Serbo-Croatian | Aram | Aramaic |
| Gas | Gascon | Egy | Egyptian |
| Tup | Tupi | Jav | Javanese |
| Ben | Bengali | Fin | Finnish |
| Kut | Kutchin | Guugu | Yimidhirr |
| Sio | Siouan | Nepa | Nepalese |
| Dra | Dravidian | Pol | Polish |
| OFri | Old Frisian | Canto | Cantonese |
| Esto | Estonian | Lith | Lithuanian |
| GaRo | Gallo-Roman | CuSpan | Cuban Spanish |
| Araw | Arawakan | Maori | Maori |
| NEAl | Southern New England Algonquian | Nar | Narragansett |
| Flem | Flemish | Aztec | Aztec |
| ByG | Byzantine Greek | Que | Quechua |
| Afrika | Afrikaans | Ojib | Ojibwa |
| Algo | Algonquian | preL | Pre-Latin |
| Serb | Serbian | Aben | Abenaki |
| Hun | Hungarian | Lush | Lushootseed |
| Dako | Dakota | Cro | Croatian |
| EL | Extinct Language | E | English |

## Data Source

This dataset was extracted and processed from etymological information available on etymonline.com. The data represents etymological relationships as documented in historical linguistic sources.

## Citation

If you use this dataset in your research, please cite our paper:

```bibtex
@inproceedings{gao-sun-2024-etymolink,
    title = "{E}tymo{L}ink: A Structured {E}nglish Etymology Dataset",
    author = "Gao, Yuan  and
      Sun, Weiwei",
    editor = "Tahmasebi, Nina  and
      Montariol, Syrielle  and
      Kutuzov, Andrey  and
      Alfter, David  and
      Periti, Francesco  and
      Cassotti, Pierluigi  and
      Huebscher, Netta",
    booktitle = "Proceedings of the 5th Workshop on Computational Approaches to Historical Language Change",
    month = aug,
    year = "2024",
    address = "Bangkok, Thailand",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.lchange-1.12/",
    doi = "10.18653/v1/2024.lchange-1.12",
    pages = "126--136"
}
```

## License

Please cite this dataset if used in research or publications. Check the LICENSE file for specific usage terms.

## Contact

For questions about the dataset or to report issues, please open an issue in the repository.