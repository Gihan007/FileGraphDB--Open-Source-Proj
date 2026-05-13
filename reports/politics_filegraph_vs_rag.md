# FileGraphDB vs Advanced RAG Baseline

Folder: `C:\Users\user\Downloads\twenty+newsgroups\20_newsgroups\20_newsgroups\talk.politics.guns`
Query: `US UK handgun deaths statistics comparison`
Limit: `10`

## Build Summary

- FileGraphDB documents/chunks: `1036`
- FileGraphDB edges: `2882`
- Advanced RAG chunks: `1322`

## Token Summary

| Method | Total tokens | Selected tokens | Saved tokens | Saved percent |
|---|---:|---:|---:|---:|
| FileGraphDB | 519290 | 6359 | 512931 | 98.78% |
| Advanced RAG | 552167 | 4379 | 547788 | 99.21% |

## FileGraphDB Results

- `53327` score=0.544 reason=query semantic/keyword match
- `53353` score=0.529 reason=query semantic/keyword match
- `53362` score=0.485 reason=query semantic/keyword match
- `53323` score=0.451 reason=query semantic/keyword match
- `53324` score=0.443 reason=query semantic/keyword match
- `53299` score=0.437 reason=query semantic/keyword match
- `53293` score=0.437 reason=query semantic/keyword match
- `53294` score=0.436 reason=query semantic/keyword match
- `53295` score=0.430 reason=query semantic/keyword match
- `53356` score=0.417 reason=query semantic/keyword match

## Advanced RAG Results

- `53327#chunk-0001` score=0.529 semantic=0.675 keyword=0.125 rerank=0.750
- `53353#chunk-0001` score=0.518 semantic=0.664 keyword=0.114 rerank=0.750
- `53294#chunk-0001` score=0.486 semantic=0.628 keyword=0.079 rerank=0.750
- `53362#chunk-0001` score=0.445 semantic=0.589 keyword=0.108 rerank=0.500
- `53323#chunk-0001` score=0.425 semantic=0.479 keyword=0.102 rerank=1.000
- `53324#chunk-0001` score=0.415 semantic=0.555 keyword=0.073 rerank=0.500
- `53293#chunk-0001` score=0.406 semantic=0.531 keyword=0.095 rerank=0.500
- `53299#chunk-0001` score=0.402 semantic=0.531 keyword=0.083 rerank=0.500
- `53295#chunk-0001` score=0.395 semantic=0.486 keyword=0.067 rerank=0.750
- `53356#chunk-0001` score=0.388 semantic=0.507 keyword=0.084 rerank=0.500

## Overlap

- `53293`
- `53294`
- `53295`
- `53299`
- `53323`
- `53324`
- `53327`
- `53353`
- `53356`
- `53362`