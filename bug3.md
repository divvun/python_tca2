# Ulik best_path_score for java og python

```json
"10,10,9,10": {
        "element_info_to_be_compared": {
          "score": 0.0,
          "common_clusters": {
            "clusters": []
          },
          "info": [
            {
              "element_number": 10,
              "length": 7,
              "num_words": 1,
              "words": ["Mobiila"],
              "anchor_word_hits": [],
              "scoring_characters": "",
              "proper_names": ["Mobiila"]
            }
          ]
        },
        "best_path_score": 110.499
      },
```

Hvordan lages `best_path_score`?

Dicten ovenfor er en CompareCells

Verdien settes i `Compare.java:Compare.getCellValues()`:

```java
Float temp = matrix.bestPathScores.get(bestPathScoreKey);
matrix.cells.get(key).bestPathScore = temp;

matrix.bestPathScores.put(bestPathScoreKey, matrix.cells.get(key).bestPathScore);
```

`CompareMatrix.java:CompareMatrix`:

```java
Map<String, Float> bestPathScores = new HashMap<String, Float>();
```

Verdien til `bestPathScores[bestPathScoreKey]` settes her:

```java
    void setScore(int[] position, float score) {
        String bestPathScoreKey = "";
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            if (t>0) { bestPathScoreKey += ","; }
            bestPathScoreKey += Integer.toString(position[t]);
        }
        bestPathScores.put(bestPathScoreKey, score);
    }
```

Funksjonen ovenfor kalles i `Compare.java:Compare.setScore`:

```java
    void setScore(int[] position, float score) {
        matrix.setScore(position, score);
    }
```

Funksjonen over kalles i `QueueEntry.java:QueueEntry.makeLongerPath`:

```java
    model.compare.setScore(retQueueEntry.path.position, retQueueEntry.score);
```

`retQueueEntry.score` bestemmes rett ovenfor der igjen:

```java
    retQueueEntry.score = tryStep(model, newStep);
```

Her er `tryStep` og `getStepScore`:

```java
    float tryStep(AlignmentModel model, PathStep newStep) throws EndOfAllTextsException, EndOfTextException, BlockedException {

        float stepScore = 0.f;
        stepScore = getStepScore(model, path.position, newStep);

        return score + stepScore;
    }

    float getStepScore(AlignmentModel model, int[] position, PathStep newStep) throws EndOfAllTextsException, EndOfTextException, BlockedException {

        CompareCells compareCells = model.compare.getCellValues(model, position, newStep);

        return compareCells.elementInfoToBeCompared.getScore();
    }
```

`getScore` får verdien sin fra `ElementInfoToBeCompared.java:ElementInfoToBeCompared.reallyGetScore2`:

```java
    float reallyGetScore2() {
        findAnchorWordMatches();

        for (int t=0; t<Alignment.NUM_FILES; t++) {
            for (int tt=t+1; tt<Alignment.NUM_FILES; tt++) {
                findNumberMatches(t, tt);
                findPropernameMatches(t, tt);
                findDiceMatches(t, tt);
                findSpecialCharacterMatches(t, tt);
            }
        }

        score += commonClusters.getScore(model.getLargeClusterScorePercentage());
        int[] length = new int[Alignment.NUM_FILES];   // length in chars of the relevant elements of each text
        int[] elementCount = new int[Alignment.NUM_FILES];   // number of relevant elements from each text

        for (int t=0; t<Alignment.NUM_FILES; t++) {
            length[t] = 0;
            Iterator<ElementInfo> it = info[t].iterator();
            while (it.hasNext()) {
                ElementInfo info1 = it.next();
                length[t] += info1.length;
            }
            elementCount[t] = info[t].size();
        }

        score = SimilarityUtils.adjustForLengthCorrelation(score, length[0], length[1], elementCount[0], elementCount[1], model.getLengthRatio());

        boolean is11 = true;
        for (int t=0; t<Alignment.NUM_FILES; t++) {
            if (info[t].size() != 1) {
                is11 = false;
            }
        }

        if (!is11) {
            score -= .001;
        }

        return score;
    }
```

Denne linja: `score += commonClusters.getScore(model.getLargeClusterScorePercentage());`
er egentlig bare tøys, for verdien blir overskrevet her:
`score = SimilarityUtils.adjustForLengthCorrelation(score, length[0], length[1], elementCount[0], elementCount[1], model.getLengthRatio());`

`SimilarityUtils.adjustForLengthCorrelation`

```java
    public static float adjustForLengthCorrelation(float score, int length1, int length2, int elementCount1, int elementCount2, float ratio) {

        float newScore = 0.0f;
        float lowerLimit = 0.4f;
        float upperLimit = 1.0f;
        float killLimit = 0.5f;
        float c = (float)(2 * Math.abs(0.0f + ratio*length1 - length2) / (ratio*length1 + length2));

        if ((elementCount1 > 0) && (elementCount2 > 0) && (elementCount1 != elementCount2)) {
            if (c < lowerLimit/2) {
                newScore = score + 2;
            } else if (c < lowerLimit) {
                newScore = score + 1;
            } else if (c > killLimit) {
                newScore = AlignmentModel.ELEMENTINFO_SCORE_HOPELESS;   // 2006-09-20
            } else {
                newScore = score;
            }

        } else {
            if (c < lowerLimit/2) {
                newScore = score + 2;
            } else if (c < lowerLimit) {
                newScore = score + 1;
            } else if (c > upperLimit) {
                newScore = score / 3;
            } else {
                newScore = score;   // (2005-08-17)
            }

        }

        return newScore;

    }
```

Men, for celle "10,10,9,10" er ikke det tilfelle

Etter ma-a-a-a-a-a-a-a-asse roting rundt, så ser det ut til at en del av greia er at det ikke finnes cluster i python.

Starter med `Make longer path: 7,9,1,1`

score-beregninga skiller vei her.
`1 cl score 25 1 -> 1 cl score 25 0`

Det e forskjell i størrelse på self.clusters
