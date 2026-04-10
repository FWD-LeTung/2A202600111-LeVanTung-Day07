# Common Benchmark Results

Dataset: `data/recipe.md`
Chunking strategy: `RecursiveChunker(chunk_size=500)`
Embedding backend: `openai:text-embedding-3-small`
Indexed chunks: 32

## Benchmark Definition

| # | Query | Gold Answer | Metadata Filter |
|---|-------|-------------|-----------------|
| 1 | What are the principal ways of cooking listed in the book? | The principal ways are boiling, broiling, stewing, roasting, baking, frying, sauteing, braising, and fricasseeing. | `{'heading_key': 'ways of cooking'}` |
| 2 | At what temperatures does water boil and simmer? | Water boils at 212F and simmers at around 185F. | `{'heading_key': 'water (h_{2}o)'}` |
| 3 | Why does milk sour according to the text? | A germ converts lactose to lactic acid, which precipitates casein into curd and whey. | `{}` |
| 4 | How is fat tested for frying temperature? | Drop a one-inch cube of bread; if golden brown in about forty seconds, fat is ready for cooked mixtures. | `{'heading_key': 'ways of cooking'}` |
| 5 | What is the chief office of proteids? | Proteids chiefly build and repair tissues, and can also furnish energy. | `{'heading_key': 'food'}` |

## Results

| # | Relevant in Top-3 (search) | Relevant in Top-3 (filtered) | Agent answer correct? | Query score (0-2) |
|---|----------------------------|------------------------------|----------------------|------------------|
| 1 | 3/3 | 3/3 | No | 1 |
- Q1 top-1 (filtered): The principal ways of cooking are boiling, broiling, stewing, roasting, baking, frying, sautéing, braising, and fricasseeing.  =Boiling= is cooking in boiling water. Solid food so ...
- Q1 agent answer: I am not sure based on the provided context.
| 2 | 2/3 | 1/3 | No | 1 |
- Q2 top-1 (filtered): Water freezes at a temperature of 32° F., boils at 212° F.; when bubbles appear on the surface and burst, the boiling-point is reached. In high altitudes water boils at a lower tem...
- Q2 agent answer: I am not sure based on the provided context.
| 3 | 1/3 | 1/3 | No | 1 |
- Q3 top-1 (filtered): Water is boiled for two purposes: first, cooking of itself to destroy organic impurities; second, for cooking foods. Boiling water toughens and hardens albumen in eggs; toughens fi...
- Q3 agent answer: I am not sure based on the provided context.
| 4 | 3/3 | 3/3 | No | 1 |
- Q4 top-1 (filtered): =Rules for Testing Fat for Frying.= 1. When the fat begins to smoke, drop in an inch cube of bread from soft part of loaf, and if in forty seconds it is golden brown, the fat is th...
- Q4 agent answer: I am not sure based on the provided context.
| 5 | 2/3 | 2/3 | No | 1 |
- Q5 top-1 (filtered): The chief office of proteids is to build and repair tissues. They furnish energy, but at greater cost than carbohydrates, fats, and oils. They contain nitrogen, carbon, oxygen, hyd...
- Q5 agent answer: I am not sure based on the provided context.

## Aggregate Metrics

- Retrieval Precision (search): 11/15 relevant chunks in top-3
- Retrieval Precision (filtered): 10/15 relevant chunks in top-3
- Benchmark Score: 5/10
- Note: Query score follows rubric in `docs/SCORING.md` (0-2 points/query).
