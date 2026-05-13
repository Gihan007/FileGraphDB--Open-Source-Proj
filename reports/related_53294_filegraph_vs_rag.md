# FileGraphDB Related-File Query vs Advanced RAG

Folder: `C:\Users\user\Downloads\twenty+newsgroups\20_newsgroups\20_newsgroups\talk.politics.guns`
Question: `Which documents support the same argument as file 53294?`
Start file: `53294`
Limit: `10`

## Build Summary

- FileGraphDB nodes: `1044`
- FileGraphDB edges: `3027`
- Advanced RAG chunks: `1322`

## FileGraphDB Results

FileGraphDB treats this as a graph-neighborhood query: `related(file)`.

- `53318` score=0.508 type=SEMANTICALLY_SIMILAR evidence=semantic=0.925; keyword=0.254; topic_overlap=0.091; entity_overlap=0.091; shared_topics=year study; shared_entities=Actually, After, British Columbia, Canada, Canadians
- `53372` score=0.422 type=SEMANTICALLY_SIMILAR evidence=semantic=0.862; keyword=0.089; topic_overlap=0.000; entity_overlap=0.034; shared_entities=All, Canada
- `53353` score=0.387 type=SEMANTICALLY_SIMILAR evidence=semantic=0.742; keyword=0.178; topic_overlap=0.000; entity_overlap=0.019; shared_entities=Brits
- `53327` score=0.387 type=SEMANTICALLY_SIMILAR evidence=semantic=0.715; keyword=0.210; topic_overlap=0.000; entity_overlap=0.055; shared_entities=Arras, Associates				   New York, Brits
- `53323` score=0.355 type=SEMANTICALLY_SIMILAR evidence=semantic=0.735; keyword=0.073; topic_overlap=0.000; entity_overlap=0.000
- `53295` score=0.344 type=SEMANTICALLY_SIMILAR evidence=semantic=0.679; keyword=0.101; topic_overlap=0.000; entity_overlap=0.053; shared_entities=American Life, Associates				   New York, Brits
- `53296` score=0.315 type=SEMANTICALLY_SIMILAR evidence=semantic=0.556; keyword=0.132; topic_overlap=0.200; entity_overlap=0.053; shared_topics=seattle, vancouver; shared_entities=Assaults, Canada, Chicago
- `54943` score=0.308 type=SEMANTICALLY_SIMILAR evidence=semantic=0.640; keyword=0.047; topic_overlap=0.000; entity_overlap=0.017; shared_entities=Chicago

## Advanced RAG Results

Advanced RAG treats this as a normal text query. It does not know that `53294` should be expanded through graph relationships.

- `54684#chunk-0012` score=0.493 semantic=0.699 keyword=0.069 rerank=0.400
- `54684#chunk-0015` score=0.484 semantic=0.686 keyword=0.067 rerank=0.400
- `54684#chunk-0007` score=0.465 semantic=0.692 keyword=0.057 rerank=0.200
- `54684#chunk-0020` score=0.456 semantic=0.676 keyword=0.061 rerank=0.200
- `54684#chunk-0011` score=0.453 semantic=0.674 keyword=0.056 rerank=0.200
- `54684#chunk-0014` score=0.440 semantic=0.621 keyword=0.053 rerank=0.400
- `54684#chunk-0008` score=0.432 semantic=0.606 keyword=0.059 rerank=0.400
- `54684#chunk-0018` score=0.429 semantic=0.635 keyword=0.056 rerank=0.200
- `54684#chunk-0019` score=0.417 semantic=0.615 keyword=0.057 rerank=0.200
- `54684#chunk-0013` score=0.415 semantic=0.574 keyword=0.067 rerank=0.400

## Overlap

- `(none)`