# Graph Report - python_tca2  (2026-08-21)

## Corpus Check
- 36 files · ~596,901 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 317 nodes · 538 edges · 28 communities (19 shown, 9 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1b54d49`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- candidate_alignment.py
- AnchorWordList
- Any
- alignment_suggestion.py
- CandidateAlignment
- similarity_utils.py
- AlignmentSearch
- AnchorWordListEntry
- extend_alignment_paths Debug Trace
- best_path_score
- tca2
- Kven Commission Corpus
- .get_aligned_sentence_elements
- Program 6. februar
- Norwegian–Northern Sámi Anchor Lexicon Test Fixture
- Sentence Alignment Input A
- py-tca2.sh
- Norwegian–Kven Test Anchor
- python-tca2
- Q: Why does ElementInfoToBeCompared connect Element Scoring to Utility Clustering, Alignment Elements, Alignment Model?
- Q: What would be a more stable of computing scores? This is quite essential …
- AlignedSentenceElements
- AnchorWordHit
- AlignmentSuggestion
- Score
- slice

## God Nodes (most connected - your core abstractions)
1. `CandidateAlignment` - 31 edges
2. `AnchorWordList` - 27 edges
3. `WordMatch` - 20 edges
4. `MatchCluster` - 17 edges
5. `MatchClusters` - 17 edges
6. `AlignmentSearch` - 17 edges
7. `AlignmentModel` - 15 edges
8. `as_score()` - 15 edges
9. `AnchorWordHit` - 12 edges
10. `RollingDocument` - 11 edges

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

## Communities (28 total, 9 thin omitted)

### Community 0 - "candidate_alignment.py"
Cohesion: 0.06
Nodes (31): _enumerate_scoring_characters(), _enumerate_words(), _is_matching_proper_name(), Yield ref pairs whose extractor output on both sides satisfies predicate., _words_equal(), MatchCluster, Any, Score (+23 more)

### Community 1 - "AnchorWordList"
Cohesion: 0.07
Nodes (44): command, Element, parametrize, AlignedSentenceElements, Convert an AlignedSentenceElements into a tuple of strings. Args:…, to_string_tuple(), main(), AlignmentModel (+36 more)

### Community 3 - "alignment_suggestion.py"
Cohesion: 0.13
Nodes (14): generate_alignment_suggestions(), is_valid_suggestion(), AlignmentSuggestion, This module provides functionality for generating alignment suggestions., Check if the increment combination is valid based on the constraints. Args:…, Create a list of AlignmentSuggestions based on the given number of files. Args:…, PathCandidate, Score (+6 more)

### Community 4 - "CandidateAlignment"
Cohesion: 0.12
Nodes (10): CandidateAlignment, _count_words(), AlignedSentenceElements, Any, Score, Check if all elements in self.info have a length of 1., Counts the number of words in a given string. Parameters: string: The input…, Check if both words are numbers. (+2 more)

### Community 5 - "similarity_utils.py"
Cohesion: 0.14
Nodes (23): adjust_for_length_correlation(), bad_length_correlation(), calculate_length_correlation_factor(), dice_match_word_pair(), dice_match_word_with_phrase(), is_word_anchor_match(), Pattern, Score (+15 more)

### Community 6 - "AlignmentSearch"
Cohesion: 0.09
Nodes (22): AlignedSentenceElements, AlignmentSuggestion, PathCandidate, PathRank, AlignmentSearch, _BeamRound, get_best_path_score(), Beam search over candidate sentence alignments. Beam search explores several… (+14 more)

### Community 7 - "AnchorWordListEntry"
Cohesion: 0.27
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

### Community 12 - ".get_aligned_sentence_elements"
Cohesion: 0.40
Nodes (3): AlignedSentenceElements, slice, Return elements in the current search window for the supplied slices.

### Community 13 - "Program 6. februar"
Cohesion: 0.67
Nodes (3): Joikekoret, Máret Áile, Program 6. februar

### Community 14 - "Norwegian–Northern Sámi Anchor Lexicon Test Fixture"
Cohesion: 0.67
Nodes (3): Norwegian–Northern Sámi Anchor Lexicon, Norwegian–Northern Sámi Anchor Lexicon Test Fixture, Northern Sámi–Norwegian Anchor Lexicon Test Fixture

### Community 21 - "Q: Why does ElementInfoToBeCompared connect Element Scoring to Utility Clustering, Alignment Elements, Alignment Model?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Why does ElementInfoToBeCompared connect Element Scoring to Utility Clustering, Alignment Elements, Alignment Model?, Source Nodes

### Community 22 - "Q: What would be a more stable of computing scores? This is quite essential …"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: What would be a more stable of computing scores? This is quite essential …, Source Nodes

### Community 24 - "AnchorWordHit"
Cohesion: 0.12
Nodes (9): AlignmentElement, Removes special characters from the start and end of a word. Iterates through a…, remove_special_characters(), AnchorWordHit, AnchorWordHits, Pattern, Retrieve synonyms for a given text number from the entries. Args: text_number:…, Retrieves anchor word hits based on provided words and indices. Args: words: A… (+1 more)

## Knowledge Gaps
- **24 isolated node(s):** `python-tca2`, `py-tca2.sh script`, `Answer`, `Outcome`, `Source Nodes` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CandidateAlignment` connect `CandidateAlignment` to `candidate_alignment.py`, `AnchorWordHit`, `AlignmentSearch`, `AnchorWordList`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `AnchorWordList` connect `AnchorWordList` to `AnchorWordHit`, `AnchorWordListEntry`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `AlignmentSearch` connect `AlignmentSearch` to `AnchorWordList`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `CandidateAlignment` (e.g. with `AnchorWordHit` and `MatchClusters`) actually correct?**
  _`CandidateAlignment` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `AnchorWordList` (e.g. with `main()` and `AlignmentModel`) actually correct?**
  _`AnchorWordList` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `WordMatch` (e.g. with `CandidateAlignment` and `MatchCluster`) actually correct?**
  _`WordMatch` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MatchCluster` (e.g. with `WordMatch` and `MatchClusters`) actually correct?**
  _`MatchCluster` has 2 INFERRED edges - model-reasoned connections that need verification._