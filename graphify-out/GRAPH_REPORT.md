# Graph Report - python_tca2  (2026-08-25)

## Corpus Check
- 33 files · ~31,309 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 303 nodes · 554 edges · 25 communities (18 shown, 7 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `66966bd1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_alignment.py
- test_alignmentmodel.py
- write_streaming_result
- alignment_suggestion.py
- CandidateAlignment
- similarity_utils.py
- AlignmentSearch
- AnchorWordListEntry
- get_best_path
- best_path_score
- tca2
- Kven Commission Corpus
- .get_aligned_sentence_elements
- Program 6. februar
- Norwegian–Northern Sámi Anchor Lexicon Test Fixture
- AlignedSentenceElements
- py-tca2.sh
- Norwegian–Kven Test Anchor
- python-tca2
- AlignmentSuggestion
- Score
- slice
- .get_anchor_word_hits

## God Nodes (most connected - your core abstractions)
1. `CandidateAlignment` - 32 edges
2. `AlignmentElement` - 23 edges
3. `AnchorWordList` - 22 edges
4. `WordMatch` - 20 edges
5. `MatchCluster` - 17 edges
6. `MatchClusters` - 17 edges
7. `AlignmentSearch` - 17 edges
8. `AlignmentModel` - 15 edges
9. `as_score()` - 15 edges
10. `AnchorWordHits` - 13 edges

## Surprising Connections (you probably didn't know these)
- `load_anchor_words()` --uses--> `AnchorWordList`  [INFERRED]
  tests/test_alignmentmodel.py → python_tca2/anchorwordlist.py
- `test_is_hit()` --calls--> `PathCandidate`  [EXTRACTED]
  tests/test_path_candidate.py → python_tca2/path_candidate.py
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

## Communities (25 total, 7 thin omitted)

### Community 0 - "candidate_alignment.py"
Cohesion: 0.06
Nodes (25): _enumerate_scoring_characters(), _enumerate_words(), _is_matching_proper_name(), Yield ref pairs whose extractor output on both sides satisfies predicate., _words_equal(), MatchCluster, Any, A group of overlapping WordMatch occurrences, scored as a single unit. Exists… (+17 more)

### Community 1 - "test_alignmentmodel.py"
Cohesion: 0.07
Nodes (35): command, parametrize, AlignedSentenceElements, Convert an AlignedSentenceElements into a tuple of strings. Args:…, to_string_tuple(), AlignmentElement, Removes special characters from the start and end of a word. Iterates through a…, remove_special_characters() (+27 more)

### Community 2 - "write_streaming_result"
Cohesion: 0.20
Nodes (15): Element, add_filename_id(), make_tmx_header(), make_tu(), make_tuv(), AlignedSentenceElements, Path, Add the tmx filename as an prop element in the header. (+7 more)

### Community 3 - "alignment_suggestion.py"
Cohesion: 0.13
Nodes (14): generate_alignment_suggestions(), is_valid_suggestion(), AlignmentSuggestion, This module provides functionality for generating alignment suggestions., Check if the increment combination is valid based on the constraints. Args:…, Create a list of AlignmentSuggestions based on the given number of files. Args:…, PathCandidate, Score (+6 more)

### Community 4 - "CandidateAlignment"
Cohesion: 0.09
Nodes (17): AnchorWordHit, CandidateAlignment, _count_words(), AlignedSentenceElements, Any, Score, Check if all elements in self.info have a length of 1., Counts the number of words in a given string. Parameters: string: The input… (+9 more)

### Community 5 - "similarity_utils.py"
Cohesion: 0.14
Nodes (23): adjust_for_length_correlation(), bad_length_correlation(), calculate_length_correlation_factor(), dice_match_word_pair(), dice_match_word_with_phrase(), is_word_anchor_match(), Pattern, Score (+15 more)

### Community 6 - "AlignmentSearch"
Cohesion: 0.10
Nodes (21): AlignedSentenceElements, AlignmentSuggestion, PathCandidate, AlignmentSearch, _BeamRound, get_best_path_score(), Beam search over candidate sentence alignments. Beam search explores several…, Select the first step of the path with the highest normalized score. (+13 more)

### Community 7 - "AnchorWordListEntry"
Cohesion: 0.24
Nodes (6): Loads anchor word list entries from a specified file. Reads the file line by…, AnchorWordListEntry, Pattern, Generate a list of phrase patterns from input pairs. Args: pairs: A list of…, Generates a list of compiled regex patterns from a synonym phrase. Args: syn: A…, Make a proper regular expression from the anchor word

### Community 8 - "get_best_path"
Cohesion: 0.40
Nodes (5): get_best_path, get_step_suggestion, lengthen_paths, retrieve_alignment_suggestion, suggest_without_gui

### Community 9 - "best_path_score"
Cohesion: 0.33
Nodes (6): best_path_score, CompareCells, ElementInfoToBeCompared.reallyGetScore2, QueueEntry.makeLongerPath, SimilarityUtils.adjustForLengthCorrelation, Length Correlation Test Fixture

### Community 10 - "tca2"
Cohesion: 0.50
Nodes (4): Knut Hofland, Sentence Alignment Program, tca2, Øystein Reigem

### Community 11 - "Kven Commission Corpus"
Cohesion: 1.00
Nodes (3): Kven Commission Corpus, Norwegian Commission Corpus, Kven–Norwegian Translation Examples

### Community 12 - ".get_aligned_sentence_elements"
Cohesion: 0.40
Nodes (3): AlignedSentenceElements, slice, Return elements in the current search window for the supplied slices.

### Community 13 - "Program 6. februar"
Cohesion: 0.67
Nodes (3): Joikekoret, Máret Áile, Program 6. februar

### Community 14 - "Norwegian–Northern Sámi Anchor Lexicon Test Fixture"
Cohesion: 0.67
Nodes (3): Norwegian–Northern Sámi Anchor Lexicon, Norwegian–Northern Sámi Anchor Lexicon Test Fixture, Northern Sámi–Norwegian Anchor Lexicon Test Fixture

### Community 24 - ".get_anchor_word_hits"
Cohesion: 0.33
Nodes (4): Pattern, Retrieve synonyms for a given text number from the entries. Args: text_number:…, Retrieves anchor word hits based on provided words and indices. Args: words: A…, Checks if a sequence of words matches an anchor phrase pattern. Args: words:…

## Knowledge Gaps
- **16 isolated node(s):** `python-tca2`, `py-tca2.sh script`, `Knut Hofland`, `Øystein Reigem`, `Sentence Alignment Program` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CandidateAlignment` connect `CandidateAlignment` to `candidate_alignment.py`, `test_alignmentmodel.py`, `AlignmentSearch`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `MatchClusters` connect `candidate_alignment.py` to `CandidateAlignment`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `AlignmentSearch` connect `AlignmentSearch` to `test_alignmentmodel.py`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `CandidateAlignment` (e.g. with `AlignmentElement` and `AnchorWordHit`) actually correct?**
  _`CandidateAlignment` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AlignmentElement` (e.g. with `AnchorWordHits` and `CandidateAlignment`) actually correct?**
  _`AlignmentElement` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `AnchorWordList` (e.g. with `main()` and `AlignmentModel`) actually correct?**
  _`AnchorWordList` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `WordMatch` (e.g. with `CandidateAlignment` and `MatchCluster`) actually correct?**
  _`WordMatch` has 3 INFERRED edges - model-reasoned connections that need verification._