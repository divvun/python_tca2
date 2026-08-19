# Graph Report - python_tca2  (2026-08-19)

## Corpus Check
- 34 files · ~596,861 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 297 nodes · 540 edges · 22 communities (18 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ce942a6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_alignment.py
- AnchorWordList
- .get_aligned_sentence_elements
- AlignmentSearch
- CandidateAlignment
- similarity_utils.py
- write_streaming_result
- AnchorWordListEntry
- extend_alignment_paths Debug Trace
- best_path_score
- tca2
- Kven Commission Corpus
- RollingDocument
- Program 6. februar
- Norwegian–Northern Sámi Anchor Lexicon Test Fixture
- Sentence Alignment Input A
- py-tca2.sh
- Norwegian–Kven Test Anchor
- python-tca2
- Q: Why does ElementInfoToBeCompared connect Element Scoring to Utility Clustering, Alignment Elements, Alignment Model?

## God Nodes (most connected - your core abstractions)
1. `CandidateAlignment` - 35 edges
2. `AnchorWordList` - 30 edges
3. `AlignmentElement` - 23 edges
4. `AlignmentSearch` - 20 edges
5. `WordMatch` - 20 edges
6. `MatchCluster` - 17 edges
7. `MatchClusters` - 17 edges
8. `PathCandidate` - 16 edges
9. `RollingDocument` - 16 edges
10. `AlignmentModel` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_generate_alignment_suggestions()` --calls--> `generate_alignment_suggestions()`  [EXTRACTED]
  tests/test_alignment_suggestion.py → python_tca2/alignment_suggestion.py
- `load_anchor_words()` --calls--> `AnchorWordListEntry`  [EXTRACTED]
  tests/test_alignmentmodel.py → python_tca2/anchorwordlistentry.py
- `test_anchorword_hits()` --calls--> `CandidateAlignment`  [EXTRACTED]
  tests/test_alignmentmodel.py → python_tca2/candidate_alignment.py
- `test_find_dice_matches()` --calls--> `CandidateAlignment`  [EXTRACTED]
  tests/test_alignmentmodel.py → python_tca2/candidate_alignment.py
- `test_get_score()` --calls--> `CandidateAlignment`  [EXTRACTED]
  tests/test_alignmentmodel.py → python_tca2/candidate_alignment.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Alignment Path Search Flow** — python_tca2_program6_2_2024_suggest_without_gui, python_tca2_program6_2_2024_get_step_suggestion, python_tca2_program6_2_2024_get_best_path, python_tca2_program6_2_2024_lengthen_paths [EXTRACTED 1.00]
- **Kven–Norwegian Parallel Corpus** — data_kommisjonen_21_08_2020_fkv_txt_fkv_new_kven_commission_corpus, data_kommisjonen_21_08_2020_nob_txt_nob_new_norwegian_commission_corpus, suggest1_9_id_446575_html_nob_kven_norwegian_translation_examples [INFERRED 0.95]
- **Norwegian–Northern Sámi Anchor Resources** — suggest1_anchor_nob_sme_norwegian_northern_sami_anchor_lexicon, tests_anchor_nob_sme_norwegian_northern_sami_anchor_lexicon, tests_anchor_sme_nob_northern_sami_norwegian_anchor_lexicon [INFERRED 0.95]

## Communities (22 total, 4 thin omitted)

### Community 0 - "candidate_alignment.py"
Cohesion: 0.06
Nodes (26): _enumerate_scoring_characters(), _enumerate_words(), _is_matching_proper_name(), Yield ref pairs whose extractor output on both sides satisfies predicate., _words_equal(), MatchCluster, Any, A group of overlapping WordMatch occurrences, scored as a single unit. Exists… (+18 more)

### Community 1 - "AnchorWordList"
Cohesion: 0.07
Nodes (41): command, parametrize, AlignmentElement, get_scoring_characters(), Any, Removes special characters from the start and end of a word. Iterates through a…, Extracts and returns scoring characters from the input text. Args: text: The…, A class representing a sentence in a document. Attributes: text_number: The… (+33 more)

### Community 2 - ".get_aligned_sentence_elements"
Cohesion: 0.40
Nodes (3): AlignedSentenceElements, slice, Return elements in the current search window for the supplied slices.

### Community 3 - "AlignmentSearch"
Cohesion: 0.07
Nodes (31): AlignmentSearch, _BeamRound, get_best_path_score(), AlignedSentenceElements, AlignmentSuggestion, slice, Beam search over candidate sentence alignments. Beam search explores several…, Select the first step of the path with the highest normalized score. (+23 more)

### Community 4 - "CandidateAlignment"
Cohesion: 0.12
Nodes (9): CandidateAlignment, _count_words(), AlignedSentenceElements, Any, Check if all elements in self.info have a length of 1., Counts the number of words in a given string. Parameters: string: The input…, Check if both words are numbers., A candidate sentence-pair alignment, scored by how well its sides match. Exists… (+1 more)

### Community 5 - "similarity_utils.py"
Cohesion: 0.14
Nodes (22): adjust_for_length_correlation(), bad_length_correlation(), calculate_length_correlation_factor(), dice_match_word_pair(), dice_match_word_with_phrase(), is_word_anchor_match(), Pattern, Check if the word is an occurrence of the anchor word Args:… (+14 more)

### Community 6 - "write_streaming_result"
Cohesion: 0.22
Nodes (13): Element, add_filename_id(), make_tmx_header(), make_tu(), make_tuv(), AlignedSentenceElements, Path, Add the tmx filename as an prop element in the header. (+5 more)

### Community 7 - "AnchorWordListEntry"
Cohesion: 0.24
Nodes (6): Loads anchor word list entries from a specified file. Reads the file line by…, AnchorWordListEntry, Pattern, Generate a list of phrase patterns from input pairs. Args: pairs: A list of…, Generates a list of compiled regex patterns from a synonym phrase. Args: syn: A…, Make a proper regular expression from the anchor word

### Community 8 - "extend_alignment_paths Debug Trace"
Cohesion: 0.29
Nodes (7): build_tree Debug Trace, extend_alignment_paths Debug Trace, get_best_path, get_step_suggestion, lengthen_paths, retrieve_alignment_suggestion, suggest_without_gui

### Community 9 - "best_path_score"
Cohesion: 0.33
Nodes (6): best_path_score, CompareCells, ElementInfoToBeCompared.reallyGetScore2, QueueEntry.makeLongerPath, SimilarityUtils.adjustForLengthCorrelation, Length Correlation Test Fixture

### Community 10 - "tca2"
Cohesion: 0.50
Nodes (4): Knut Hofland, Sentence Alignment Program, tca2, Øystein Reigem

### Community 11 - "Kven Commission Corpus"
Cohesion: 1.00
Nodes (3): Kven Commission Corpus, Norwegian Commission Corpus, Kven–Norwegian Translation Examples

### Community 12 - "RollingDocument"
Cohesion: 0.24
Nodes (4): slice, Return whether an input position is beyond the document end., Lazily materialize alignment elements and discard committed input., RollingDocument

### Community 13 - "Program 6. februar"
Cohesion: 0.67
Nodes (3): Joikekoret, Máret Áile, Program 6. februar

### Community 14 - "Norwegian–Northern Sámi Anchor Lexicon Test Fixture"
Cohesion: 0.67
Nodes (3): Norwegian–Northern Sámi Anchor Lexicon, Norwegian–Northern Sámi Anchor Lexicon Test Fixture, Northern Sámi–Norwegian Anchor Lexicon Test Fixture

### Community 21 - "Q: Why does ElementInfoToBeCompared connect Element Scoring to Utility Clustering, Alignment Elements, Alignment Model?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Why does ElementInfoToBeCompared connect Element Scoring to Utility Clustering, Alignment Elements, Alignment Model?, Source Nodes

## Knowledge Gaps
- **21 isolated node(s):** `py-tca2.sh script`, `python-tca2`, `Answer`, `Outcome`, `Source Nodes` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CandidateAlignment` connect `CandidateAlignment` to `candidate_alignment.py`, `AnchorWordList`, `AlignmentSearch`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `AlignmentSearch` connect `AlignmentSearch` to `AnchorWordList`, `RollingDocument`, `CandidateAlignment`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `MatchClusters` connect `candidate_alignment.py` to `CandidateAlignment`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `CandidateAlignment` (e.g. with `AlignmentSearch` and `_BeamRound`) actually correct?**
  _`CandidateAlignment` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `AnchorWordList` (e.g. with `AlignmentElement` and `AlignmentModel`) actually correct?**
  _`AnchorWordList` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AlignmentElement` (e.g. with `AnchorWordHits` and `AnchorWordList`) actually correct?**
  _`AlignmentElement` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AlignmentSearch` (e.g. with `CandidateAlignment` and `PathCandidate`) actually correct?**
  _`AlignmentSearch` has 4 INFERRED edges - model-reasoned connections that need verification._